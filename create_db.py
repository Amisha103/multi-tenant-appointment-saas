import os

url = os.getenv("DATABASE_URL")

print("DATABASE URL:")
print(url)

conn = psycopg2.connect(url)