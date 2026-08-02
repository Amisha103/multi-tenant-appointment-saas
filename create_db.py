import os
import psycopg2
import time
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
print("DATABASE_URL =", os.getenv("DATABASE_URL"))
for i in range(10):
    try:
        conn = psycopg2.connect(
            DATABASE_URL,
            sslmode='require'   # 🔥 IMPORTANT for Render
        )
        cur = conn.cursor()

        print("✅ Connected to database successfully!")

        cur.close()
        conn.close()
        break

    except psycopg2.OperationalError as e:
        print(f"❌ Error: {e}")
        print(f"⏳ Database not ready... retrying ({i+1}/10)")
        time.sleep(2)

else:
    print("❌ Could not connect to database after multiple attempts")