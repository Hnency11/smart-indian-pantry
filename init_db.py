import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def init_db():
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME", "smart_pantry"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", ""),
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432")
        )
        cur = conn.cursor()
        
        with open('schema.sql', 'r') as f:
            cur.execute(f.read())
            
        conn.commit()
        cur.close()
        conn.close()
        print("Database initialized successfully!")
    except Exception as e:
        print(f"Error initializing database: {e}")

if __name__ == "__main__":
    init_db()
