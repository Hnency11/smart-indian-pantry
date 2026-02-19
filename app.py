from flask import Flask, request, jsonify, render_template
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import psycopg2
import bcrypt
import os
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "super-secret")
jwt = JWTManager(app)

@app.before_request
def log_request_info():
    print(f"Request: {request.method} {request.url}")

@app.after_request
def log_response_info(response):
    print(f"Response: {response.status}")
    return response

# Frontend Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/auth')
def auth_page():
    return render_template('auth.html')

@app.route('/pantry-page')
def pantry_page():
    return render_template('pantry.html')

@app.route('/recipes-page')
def recipes_page():
    return render_template('recipes.html')

@app.route('/recipe-page/<int:recipe_id>')
def recipe_page(recipe_id):
    return render_template('recipe_detail.html')

def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME", "smart_pantry"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432")
    )

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"msg": "Missing email or password"}), 400

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO users (email, password_hash) VALUES (%s, %s)", (email, hashed_password))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"msg": "User created successfully"}), 201
    except psycopg2.IntegrityError:
        return jsonify({"msg": "User already exists"}), 400
    except Exception as e:
        return jsonify({"msg": str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, password_hash FROM users WHERE email = %s", (email,))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if user and bcrypt.checkpw(password.encode('utf-8'), user[1].encode('utf-8')):
        access_token = create_access_token(identity=str(user[0]))
        return jsonify(access_token=access_token)

    return jsonify({"msg": "Bad email or password"}), 401

@app.route('/ingredients', methods=['GET'])
@jwt_required()
def get_ingredients():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, category FROM ingredients ORDER BY category, name")
    ingredients = cur.fetchall()
    cur.close()
    conn.close()

    result = []
    for ing in ingredients:
        result.append({"id": ing[0], "name": ing[1], "category": ing[2]})
    
    return jsonify(result)

@app.route('/pantry', methods=['GET', 'POST'])
@jwt_required()
def manage_pantry():
    user_id = get_jwt_identity()
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        try:
            ingredient_ids = request.json.get('ingredient_ids', [])
            
            # Check if user exists
            cur.execute("SELECT id FROM users WHERE id = %s", (user_id,))
            if not cur.fetchone():
                return jsonify({"msg": "Session expired or user deleted. Please log in again."}), 401

            # Clear existing pantry
            cur.execute("DELETE FROM user_pantry WHERE user_id = %s", (user_id,))
            # Add new ingredients
            for ing_id in ingredient_ids:
                cur.execute("INSERT INTO user_pantry (user_id, ingredient_id) VALUES (%s, %s)", (user_id, ing_id))
            conn.commit()
            return jsonify({"msg": "Pantry updated"})
        except Exception as e:
            conn.rollback()
            print(f"Pantry Save Error: {e}")
            return jsonify({"msg": "Error saving pantry", "error": str(e)}), 500
        finally:
            cur.close()
            conn.close()

    # GET method
    cur.execute("""
        SELECT i.id, i.name, i.category 
        FROM ingredients i 
        JOIN user_pantry up ON i.id = up.ingredient_id 
        WHERE up.user_id = %s
    """, (user_id,))
    pantry = cur.fetchall()
    cur.close()
    conn.close()

    result = [{"id": p[0], "name": p[1], "category": p[2]} for p in pantry]
    return jsonify(result)

@app.route('/recommend', methods=['GET'])
@jwt_required()
def recommend():
    user_id = get_jwt_identity()
    conn = get_db_connection()
    cur = conn.cursor()

    # Get user's ingredients
    cur.execute("SELECT ingredient_id FROM user_pantry WHERE user_id = %s", (user_id,))
    user_ingredients = [row[0] for row in cur.fetchall()]

    if not user_ingredients:
        cur.close()
        conn.close()
        return jsonify([])

    # Get all recipes and their ingredients (id and name)
    cur.execute("""
        SELECT r.id, r.title, r.image_url, r.is_vegetarian, r.category,
               ARRAY_AGG(i.name) as ingredient_names,
               ARRAY_AGG(i.id) as ingredient_ids
        FROM recipes r
        JOIN recipe_ingredients ri ON r.id = ri.recipe_id
        JOIN ingredients i ON ri.ingredient_id = i.id
        GROUP BY r.id
    """)
    recipes = cur.fetchall()
    cur.close()
    conn.close()

    recommendations = []
    for r_id, title, img, is_veg, cat, r_ing_names, r_ing_ids in recipes:
        matching_ids = set(user_ingredients) & set(r_ing_ids)
        match_score = len(matching_ids) / len(r_ing_ids) if r_ing_ids else 0
        
        # Missing ingredients details (names)
        missing_ingredients = [name for name, iid in zip(r_ing_names, r_ing_ids) if iid not in user_ingredients]
        
        recommendations.append({
            "id": r_id,
            "title": title,
            "image_url": img,
            "is_vegetarian": is_veg,
            "category": cat,
            "match_score": round(match_score * 100, 2),
            "missing_count": len(missing_ingredients),
            "missing_ingredients": missing_ingredients[:3] # Show top 3 missing
        })

    # Sort by match score descending
    recommendations.sort(key=lambda x: x['match_score'], reverse=True)
    
    return jsonify(recommendations[:20]) # Return top 20

@app.route('/recipe/<int:recipe_id>', methods=['GET'])
@jwt_required()
def recipe_detail(recipe_id):
    user_id = get_jwt_identity()
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM recipes WHERE id = %s", (recipe_id,))
    recipe = cur.fetchone()
    if not recipe:
        cur.close()
        conn.close()
        return jsonify({"msg": "Recipe not found"}), 404

    # Get recipe ingredients
    cur.execute("""
        SELECT i.name, i.id IN (SELECT ingredient_id FROM user_pantry WHERE user_id = %s) as is_owned
        FROM ingredients i
        JOIN recipe_ingredients ri ON i.id = ri.ingredient_id
        WHERE ri.recipe_id = %s
    """, (user_id, recipe_id))
    ingredients = cur.fetchall()
    cur.close()
    conn.close()

    # Sort ingredients: matched (True) first
    ingredients_list = [{"name": i[0], "matched": i[1]} for i in ingredients]
    ingredients_list.sort(key=lambda x: x['matched'], reverse=True)

    return jsonify({
        "id": recipe[0],
        "title": recipe[1],
        "instructions": recipe[2],
        "image_url": recipe[3],
        "category": recipe[4],
        "is_vegetarian": recipe[5],
        "prep_time": recipe[6],
        "cuisine": recipe[7],
        "ingredients": ingredients_list
    })

if __name__ == '__main__':
    app.run(debug=True, port=5001)
