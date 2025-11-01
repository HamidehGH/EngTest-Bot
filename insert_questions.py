import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Establish a connection using environment variables
conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST")
)

# Open a cursor to perform database operations
cur = conn.cursor()

# Create a table to store the questions data
cur.execute("""
    CREATE TABLE IF NOT EXISTS questions (
	id SERIAL PRIMARY KEY,
        question TEXT,
        options TEXT[],
        answer TEXT,
        explanation TEXT,
        is_sent INTEGER DEFAULT 0
    )
""")

# Delete all existing data from the table
cur.execute("DELETE FROM questions")

# Read questions from a file
questions = []
with open('all_inter_qa.txt', 'r') as file:
    lines = file.readlines()
    
data_without_newlines = [sentence.strip() for sentence in lines if sentence != '\n']
for i in range(0, len(data_without_newlines), 4):
    row = data_without_newlines[i:i+4]
    question, options, answer, explanation = row[0], row[1].split(','), row[2], row[3]
    cur.execute("INSERT INTO questions (question, options, answer, explanation) VALUES (%s, %s, %s, %s)", (question, options, answer, explanation))

# Commit the transaction
conn.commit()

# Close the cursor and the connection
cur.close()
conn.close()