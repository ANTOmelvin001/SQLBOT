# sql_tutor_bot_phase8_educational_full_expl.py
import streamlit as st
import mysql.connector
import pandas as pd
import re
import traceback

# ----------------------------
# DB connect helper
# ----------------------------
def connect_db():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1234",
            database="sql_chatbot"
        )
        return conn
    except mysql.connector.Error as e:
        st.warning(f"❌ Cannot connect to database: {e}\n⚠️ You can still learn SQL concepts and practice!")
        return None

# ----------------------------
# Concept explanations with samples and practice
# ----------------------------
def concept_guide(topic):
    topic = topic.lower()
    
    if "ddl" in topic or "create table" in topic or "drop" in topic:
        st.info("📚 Concept: DDL (Data Definition Language)")
        st.write("• **Definition:** DDL commands define or modify the structure of database objects such as tables, schemas, or indexes. Examples: CREATE, ALTER, DROP.")
        st.markdown("**Sample SQL:**")
        st.code("""
-- Create table
CREATE TABLE students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50),
    age INT,
    class_id INT
);

-- Alter table
ALTER TABLE students ADD COLUMN email VARCHAR(100);

-- Drop table
DROP TABLE students;
""", language="sql")
        st.markdown("**Practice Questions:**\n1. Create a table 'classes' with id and class_name.\n2. Add a column 'address' to 'students'.\n3. Drop the 'students' table.")

    elif "dml" in topic or "insert" in topic or "update" in topic or "delete" in topic:
        st.info("📚 Concept: DML (Data Manipulation Language)")
        st.write("• **Definition:** DML commands are used to manipulate data stored in tables. Examples: INSERT, UPDATE, DELETE.")
        st.markdown("**Sample SQL:**")
        st.code("""
-- Insert data
INSERT INTO students (name, age, class_id) VALUES ('John', 20, 1);

-- Update data
UPDATE students SET age = 21 WHERE name = 'John';

-- Delete data
DELETE FROM students WHERE name = 'John';
""", language="sql")
        st.markdown("**Practice Questions:**\n1. Insert 2 students into 'students'.\n2. Update age of student 'Alice' to 22.\n3. Delete student with name 'Bob'.")

    elif "dcl" in topic or "grant" in topic or "revoke" in topic:
        st.info("📚 Concept: DCL (Data Control Language)")
        st.write("• **Definition:** DCL commands manage database access and permissions. They control what users can do in the database. Common commands are GRANT (give privileges) and REVOKE (remove privileges).")
        st.markdown("**Sample SQL:**")
        st.code("""
-- Grant privileges
GRANT SELECT, INSERT ON sql_chatbot.* TO 'user1'@'localhost';

-- Revoke privileges
REVOKE INSERT ON sql_chatbot.* FROM 'user1'@'localhost';
""", language="sql")
        st.markdown("**Practice Questions:**\n1. Grant UPDATE permission to 'user2'.\n2. Revoke DELETE permission from 'user1'.")

    elif "tcl" in topic or "commit" in topic or "rollback" in topic:
        st.info("📚 Concept: TCL (Transaction Control Language)")
        st.write("• **Definition:** TCL commands manage transactions in SQL. They control when changes are permanently applied or undone. Common commands are COMMIT (save changes) and ROLLBACK (undo changes).")
        st.markdown("**Sample SQL:**")
        st.code("""
-- Begin transaction
START TRANSACTION;

-- Execute DML
INSERT INTO students (name, age) VALUES ('Emma', 23);

-- Commit changes
COMMIT;

-- Or undo changes
ROLLBACK;
""", language="sql")
        st.markdown("**Practice Questions:**\n1. Start a transaction and insert 2 students, then rollback.\n2. Commit a transaction after updating ages.")

    elif "where" in topic:
        st.info("📚 Concept: WHERE Clause")
        st.write("• **Definition:** The WHERE clause filters rows based on a condition. Used in SELECT, UPDATE, DELETE queries.")
        st.code("""
-- Select students aged 22
SELECT * FROM students WHERE age = 22;

-- Update student age
UPDATE students SET age = 23 WHERE name = 'Alice';

-- Delete student
DELETE FROM students WHERE id = 3;
""", language="sql")
        st.markdown("**Practice Questions:**\n1. Students older than 21.\n2. Students in class_id = 1.\n3. Delete students with age < 20.")

    elif "join" in topic:
        st.info("📚 Concept: JOIN Clause")
        st.write("• **Definition:** JOIN combines rows from two or more tables based on a related column. Types: INNER JOIN, LEFT JOIN, RIGHT JOIN, FULL OUTER JOIN.")
        st.code("""
SELECT s.name, c.class_name
FROM students s
JOIN classes c ON s.class_id = c.id;
""", language="sql")
        st.markdown("**Practice Questions:** List all students with their class names using JOIN.")

    elif "group by" in topic:
        st.info("📚 Concept: GROUP BY Clause")
        st.write("• **Definition:** GROUP BY groups rows that have the same value in specified columns. Usually used with aggregate functions like COUNT, AVG.")
        st.code("""
-- Count students per class
SELECT class_id, COUNT(*) AS student_count
FROM students
GROUP BY class_id;
""", language="sql")
        st.markdown("**Practice Questions:** Count students older than 20 in each class.")

    elif any(x in topic for x in ["count", "avg", "min", "max"]):
        st.info("📚 Concept: Aggregate Functions")
        st.write("• **Definition:** Aggregate functions compute a single value from multiple rows. Common ones: COUNT, AVG, MIN, MAX, SUM.")
        st.code("""
-- Count total students
SELECT COUNT(*) AS total_students FROM students;

-- Average age
SELECT AVG(age) AS avg_age FROM students;

-- Maximum age
SELECT MAX(age) AS max_age FROM students;

-- Minimum age
SELECT MIN(age) AS min_age FROM students;
""", language="sql")
        st.markdown("**Practice Questions:** Find min, max, average age of students.")

    else:
        st.info("Try topics like: DDL, DML, DCL, TCL, WHERE, JOIN, GROUP BY, aggregates.")

# ----------------------------
# English -> SQL translator
# ----------------------------
def english_to_sql(cmd: str):
    cmd = cmd.lower().strip()
    if "students with their class" in cmd or "students with classes" in cmd:
        return "SELECT s.name, c.class_name FROM students s JOIN classes c ON s.class_id = c.id;"
    if re.search(r"\b(show|list|display|get)\b.*students?", cmd):
        return "SELECT * FROM students;"
    if re.search(r"\bcount\b.*students", cmd):
        return "SELECT COUNT(*) FROM students;"
    return None

# ----------------------------
# SQL Explanation
# ----------------------------
def explain_sql(sql):
    sql_low = sql.lower()
    lines = []
    if sql_low.startswith("select"):
        lines.append("• SELECT: which columns to display")
        if "from" in sql_low: lines.append("• FROM: table to read rows from")
        if "where" in sql_low: lines.append("• WHERE: filter rows")
        if "group by" in sql_low: lines.append("• GROUP BY: group rows for aggregates")
        if "order by" in sql_low: lines.append("• ORDER BY: sort rows")
        if re.search(r"count\(|avg\(|max\(|min\(", sql_low):
            lines.append("• Aggregate functions: COUNT, AVG, MAX, MIN")
        if "join" in sql_low: lines.append("• JOIN: combine rows from tables")
    elif sql_low.startswith("insert"):
        lines.append("• INSERT INTO: add new row")
    elif sql_low.startswith("update"):
        lines.append("• UPDATE: modify existing rows")
    elif sql_low.startswith("delete"):
        lines.append("• DELETE FROM: remove rows")
    else:
        lines.append("• Raw SQL statement")
    return "\n".join(lines)

# ----------------------------
# Raw SQL detector
# ----------------------------
def is_raw_sql(text):
    return re.match(r"^\s*(select|insert|update|delete|create|alter|drop|grant|revoke|commit|rollback)\b", text, flags=re.I)

# ----------------------------
# Execute SQL
# ----------------------------
def execute_sql(sql):
    conn = connect_db()
    if not conn: return
    cur = conn.cursor()
    try:
        cur.execute(sql)
        if sql.strip().lower().startswith("select"):
            rows = cur.fetchall()
            if rows:
                df = pd.DataFrame(rows, columns=[d[0] for d in cur.description])
                st.dataframe(df, use_container_width=True)
            else:
                st.success("✅ Query executed — no rows returned")
        else:
            conn.commit()
            st.success("✅ Query executed successfully")
    except mysql.connector.Error as e:
        st.error(f"❌ SQL Error: {e}")
        st.text(traceback.format_exc())
    finally:
        cur.close()
        conn.close()

# ----------------------------
# Streamlit UI
# ----------------------------
st.set_page_config(page_title="SQL Tutor Bot", layout="wide")
st.title("🤖 SQL Tutor Bot — Educational Mode")

user_input = st.text_input("Ask a question in English or type SQL:")

if user_input:
    user_low = user_input.lower()
    # Concept explanation
    if any(k in user_low for k in ["explain", "concept", "show example", "what is", "dml","ddl","dcl","tcl","where","join","group by","aggregate","count","avg","min","max"]):
        concept_guide(user_input)
    else:
        generated_sql = english_to_sql(user_input)
        if generated_sql:
            st.markdown("### 🔎 SQL Example")
            st.code(generated_sql, language="sql")
            st.markdown("### 💬 Explanation")
            st.text(explain_sql(generated_sql))
            if st.button("✅ Run SQL"):
                execute_sql(generated_sql)
        elif is_raw_sql(user_input):
            st.info("Detected raw SQL input")
            st.markdown("### 💬 Explanation")
            st.text(explain_sql(user_input))
            if st.button("✅ Run SQL"):
                execute_sql(user_input)
        else:
            st.info("I can explain concepts like DDL, DML, DCL, TCL, WHERE, JOIN, GROUP BY, aggregates.")
