import pandas as pd
import psycopg2
import os
import re
from dotenv import load_dotenv

load_dotenv()

def normalize_ingredient(ingredient):
    # Basic normalization: lowercase, remove special chars, trim
    ingredient = ingredient.lower().strip()
    
    # Remove fragments in parentheses
    ingredient = re.sub(r'\(.*?\)', '', ingredient).strip()
    
    # Aggressive removal of descriptive phrases/prefixes
    descriptive_parts = [
        r'^a few\s+', r'^a small\s+', r'^a sprig\s+', r'^a pinch\s+', r'^a bunch\s+',
        r'^some\s+', r'^any\s+', r'^about\s+', r'^optional\s+', r'^additional\s+',
        r'^alternative\s+', r'^for the\s+', r'^for garnish\s+', r'^for frying\s+',
        r'^as required\s+', r'^as needed\s+', r'^soaked in\s+', r'^dissolved in\s+',
        r'^peeled and\s+', r'^washed and\s+', r'^roughly\s+', r'^finely\s+',
        r'^chopped\s+', r'^grated\s+', r'^minced\s+', r'^crushed\s+', r'^sliced\s+',
        r'^mashed\s+', r'^boiled\s+', r'^roasted\s+', r'^dried\s+', r'^fresh\s+',
        r'^and\s+', r'^or\s+', r'^with\s+', r'^into\s+', r'^to\s+',
        r'\s+chopped$', r'\s+peeled$', r'\s+grated$', r'\s+mashed$', r'\s+boiled$',
        r'\s+pieces$', r'\s+fillet$', r'\s+chunks$', r'\s+strips$', r'\s+garnish$',
        r'\bof\b', r'\band\b'
    ]
    for part in descriptive_parts:
        ingredient = re.sub(part, '', ingredient).strip()

    junk_words = [
        'cup', 'cups', 'tablespoon', 'tablespoons', 'teaspoon', 'teaspoons', 
        'tbsp', 'tsp', 'gram', 'grams', 'kg', 'ml', 'litre', 'liter',
        'strands', 'sprigs', 'size', 'sized', 'ball', 'half', 'quarter',
        'extra', 'more', 'divided', 'pinch', 'bunch', 'drop', 'bit', 'leaf', 'leaves'
    ]
    
    # Remove quantities
    ingredient = re.sub(r'^(\d+/\d+|\d+-\d+|\d+\.\d+|\d+)\s*', '', ingredient)
    
    # Remove standalone junk words
    for word in junk_words:
        ingredient = re.sub(r'\b' + re.escape(word) + r'\b', '', ingredient).strip()
    
    # Remove junk characters but keep spaces
    ingredient = re.sub(r'[^a-z\s]', ' ', ingredient)
    
    # Collapse spaces
    ingredient = re.sub(r'\s+', ' ', ingredient).strip()
    
    # Very generic phrases to discard
    junk_phrases = [
        'a few', 'a sprig', 'a small', 'a bit', 'a drop', 'as required', 'to taste',
        'in addition to the potatoes', 'following ingredients', 'you could use the'
    ]
    for phrase in junk_phrases:
        if phrase in ingredient:
            ingredient = ingredient.replace(phrase, '').strip()

    if not ingredient or ingredient.isdigit() or len(ingredient) < 3:
        return None
        
    return ingredient

# List of common Indian ingredients for "Quick Kitchen"
COMMON_INDIAN_INGREDIENTS = [
    'onion', 'potato', 'tomato', 'ginger', 'garlic', 'green chili', 
    'coriander leaves', 'cumin seeds', 'mustard seeds', 'turmeric powder', 
    'red chili powder', 'garam masala', 'salt', 'oil', 'ghee', 
    'atta', 'flour', 'rice', 'dal', 'milk', 'curd', 'paneer', 'lemon', 
    'sugar', 'black pepper', 'curry leaves', 'hing'
]

def load_data():
    csv_file = 'dataset/cuisines.csv'
    if not os.path.exists(csv_file):
        print(f"Error: {csv_file} not found. Please place the dataset CSV in the dataset/ folder.")
        return

    try:
        df = pd.read_csv(csv_file)
        
        # Connect to DB
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME", "smart_pantry"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", ""),
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432")
        )
        cur = conn.cursor()

        for _, row in df.iterrows():
            # Insert Recipe
            title = row.get('name', row.get('Title', 'Unknown Recipe'))
            instructions = row.get('instructions', row.get('Instructions', 'No instructions provided.'))
            image_url = row.get('image_url', row.get('Image_Name', ''))
            category = row.get('course', row.get('Category', 'Main Course'))
            is_vegetarian = 'vegetarian' in str(row.get('diet', '')).lower()
            prep_time = str(row.get('prep_time', ''))
            cuisine = str(row.get('cuisine', ''))

            cur.execute("""
                INSERT INTO recipes (title, instructions, image_url, category, is_vegetarian, prep_time, cuisine)
                VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id
            """, (title, instructions, image_url, category, is_vegetarian, prep_time, cuisine))
            recipe_id = cur.fetchone()[0]

            # Process Ingredients
            raw_ingredients = row.get('ingredients', row.get('Ingredients', ''))
            if isinstance(raw_ingredients, str):
                # Split by comma or newline depending on format
                ingal_list = [i.strip() for i in re.split(r',|\n', raw_ingredients) if i.strip()]
                
                for ing in ingal_list:
                    normalized_ing = normalize_ingredient(ing)
                    if not normalized_ing:
                        continue
                        
                    # Insert Ingredient if not exists
                    # Tag as 'Quick' if in our common list
                    category = 'Quick Kitchen' if any(word in normalized_ing for word in COMMON_INDIAN_INGREDIENTS) else 'All'
                    
                    cur.execute("""
                        INSERT INTO ingredients (name, category)
                        VALUES (%s, %s)
                        ON CONFLICT (name) DO UPDATE SET category = EXCLUDED.category
                        RETURNING id
                    """, (normalized_ing, category))
                    ingredient_id = cur.fetchone()[0]

                    # Link Recipe and Ingredient
                    cur.execute("""
                        INSERT INTO recipe_ingredients (recipe_id, ingredient_id)
                        VALUES (%s, %s)
                        ON CONFLICT DO NOTHING
                    """, (recipe_id, ingredient_id))

        conn.commit()
        cur.close()
        conn.close()
        print("Dataset loaded successfully!")

    except Exception as e:
        print(f"Error loading dataset: {e}")

if __name__ == "__main__":
    load_data()
