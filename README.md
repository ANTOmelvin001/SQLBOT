🤖 SQL Tutor Bot – Educational Mode

This is an interactive SQL learning assistant built using Python, Streamlit, and MySQL.
It teaches basic to intermediate SQL concepts with explanations, sample queries, practice questions, and even executes queries in real time.

🚀 Features

📚 Concept Explanations – Learn DDL, DML, DCL, TCL, WHERE, JOIN, GROUP BY, and Aggregate functions
💬 English → SQL – Converts natural language into SQL queries
🖥️ Query Execution – Runs SQL queries and displays results in a table
🔎 SQL Breakdown – Explains each part of a query in simple terms
🧑‍🏫 Practice Mode – Provides practice tasks for learners
📱 Interactive UI – Built with Streamlit for a clean learning experience

📁 Files Included

sql_tutor_bot_phase8_educational_full_expl.py – Main Streamlit app
requirements.txt – Dependencies (Streamlit, MySQL Connector, Pandas)
Database: students & classes tables (used for demo queries)

📦 How to Use
Clone or download the project folder.
Install dependencies:
pip install streamlit mysql-connector-python pandas


Setup MySQL Database:

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


Run the app:
streamlit run sql_tutor_bot_phase8_educational_full_expl.py
Open in browser → http://localhost:8501

✅ Assignment Checklist
📚 Explains SQL concepts clearly
💬 Handles English & SQL inputs
🖥️ Runs queries on MySQL
🔎 Explains query parts
🎓 Includes practice questions
📱 User-friendly Streamlit interface

🎥 Demo
🔗 Source Code: GitHub Repository
🌐 Live Demo (Optional): Deploy on Streamlit Cloud or Heroku

🛠 Built With
Python 🐍
Streamlit 🎨
MySQL 🗄️
Pandas 📊
Regex 🔍

👨‍💻 Author

Developed by Anto Melvin E – Passionate about Python, SQL, Web Development, and AI-powered assistants.
