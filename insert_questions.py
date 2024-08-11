import psycopg2

# Establish a connection to your PostgreSQL database
conn = psycopg2.connect(
    dbname="TestDB",
    user="postgres",
    password="123456",
    host="localhost"
)

# Open a cursor to perform database operations
cur = conn.cursor()

# Create a table to store the questions data
cur.execute("""
    CREATE TABLE IF NOT EXISTS EnglishQuestions1 (
        question TEXT,
        options TEXT[],
        answer TEXT,
        explanation TEXT
    )
""")

# Delete all existing data from the table
cur.execute("DELETE FROM EnglishQuestions1")

# Read questions from a file
questions = []
with open('English_questions1.txt', 'r') as file:
    lines = file.readlines()
    

data_without_newlines = [sentence.strip() for sentence in lines if sentence != '\n']
for i in range(0, len(data_without_newlines), 4):
    row = data_without_newlines[i:i+4]
    question, options, answer, explanation = row[0], row[1].split(','), row[2], row[3]
    cur.execute("INSERT INTO EnglishQuestions1 (question, options, answer, explanation) VALUES (%s, %s, %s, %s)", (question, options, answer, explanation))

# Commit the transaction
conn.commit()

# Close the cursor and the connection
cur.close()
conn.close()