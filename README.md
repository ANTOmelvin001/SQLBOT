🤖 SQL Tutor Bot — Educational Mode

An interactive SQL learning chatbot built with Python, SQL, and Streamlit.
It explains SQL concepts (basic → intermediate), runs real queries, and helps learners practice with examples.

📌 Features

📚 Concept Guides – Explains SQL topics (DDL, DML, DCL, TCL, WHERE, JOIN, GROUP BY, Aggregates) with examples and practice questions.

💬 English → SQL – Converts natural language questions into SQL queries.

🖥️ SQL Execution – Runs queries on a MySQL database and shows results in a table.

🔎 SQL Explanation – Breaks down raw SQL statements into easy-to-understand parts.

🎓 Beginner-Friendly – Helps users learn step by step from basics to intermediate SQL.

🛠️ Tech Stack

Python 🐍 – Core programming

Streamlit 🎨 – Interactive web app UI

MySQL 🗄️ – Database backend

Pandas 📊 – Display query results in tabular format

Regex 🔍 – English-to-SQL translation & input detection

📂 Project Structure
sql_tutor_bot_phase8_educational_full_expl.py   # Main application

🚀 How to Run

Clone the repo / Save the script

git clone https://github.com/your-username/sql-tutor-bot.git
cd sql-tutor-bot


Install dependencies

pip install streamlit mysql-connector-python pandas


Set up MySQL Database

CREATE DATABASE sql_chatbot;
USE sql_chatbot;

CREATE TABLE students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50),
    age INT,
    class_id INT
);

CREATE TABLE classes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    class_name VARCHAR(50)
);


Run the app

streamlit run sql_tutor_bot_phase8_educational_full_expl.py


Open in browser → http://localhost:8501

🎯 Example Interactions

User: "Explain DDL"

Bot: Shows explanation + sample queries + practice tasks.

User: "List all students"

Bot: Generates →

SELECT * FROM students;


Explanation + Option to Run Query.

User: Raw SQL

SELECT name, age FROM students WHERE age > 20;


Bot: Explains each SQL clause and executes query.

🔑 Key Learning Benefits

✅ Learn SQL concepts step-by-step
✅ Run and test queries in real-time
✅ Practice with guided questions
✅ Understand queries with simple explanations

🌟 Future Enhancements

Add support for advanced SQL (window functions, subqueries)

AI-powered error correction for SQL syntax

Gamified SQL practice challenges

🙌 Built with ❤️ by Anto Melvin E – Turning ideas into interactive learning tools.
