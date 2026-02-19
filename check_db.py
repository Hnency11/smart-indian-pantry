import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def check_data():
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME", "smart_pantry"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", ""),
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432")
        )
        cur = conn.cursor()
        
        cur.execute("SELECT count(*) FROM ingredients;")
        ing_count = cur.fetchone()[0]
        print(f"Total Ingredients: {ing_count}")
        
        cur.execute("SELECT name FROM ingredients LIMIT 10;")
        ings = cur.fetchall()
        print(f"Sample Ingredients: {ings}")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_data()
