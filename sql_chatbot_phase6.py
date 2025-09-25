# sql_chatbot_phase6.py
import streamlit as st
import mysql.connector
import re
import pandas as pd
import traceback

# ----------------------------
# Connect to MySQL
# ----------------------------
def connect_db():
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1234",
            database="sql_chatbot"
        )
        return db
    except Exception as e:
        st.error(f"❌ Connection Error: {e}")
        return None

# ----------------------------
# English -> SQL translator
# ----------------------------
def english_to_sql(cmd: str):
    cmd = cmd.lower().strip()
    
    # SELECT all students
    if re.search(r"\b(show|list|display|get)\b(?:\s+all)?\s+students?\b", cmd):
        return "SELECT * FROM students;"
    
    # INSERT student
    m = re.search(r"(?:add|insert)\s+(?:a\s+)?(?:student\s+)?['\"]?([a-zA-Z0-9_]+)['\"]?(?:[, ]+\s*(?:age|aged)\s*[: ]\s*(\d+))?", cmd)
    if m:
        name, age = m.group(1), m.group(2)
        if age:
            return f"INSERT INTO students (name, age) VALUES ('{name}', {age});"
        return f"INSERT INTO students (name) VALUES ('{name}');"
    
    # UPDATE student age
    m = re.search(r"(?:update|set)\s+['\"]?([a-zA-Z0-9_]+)['\"]?(?:'s)?\s+age\s+(?:to|=)\s*(\d+)", cmd)
    if m:
        return f"UPDATE students SET age={m.group(2)} WHERE name='{m.group(1)}';"
    
    # DELETE student
    m = re.search(r"(?:delete|remove)\s+(?:student\s+)?['\"]?([a-zA-Z0-9_]+)['\"]?", cmd)
    if m:
        return f"DELETE FROM students WHERE name='{m.group(1)}';"
    
    # Aggregations
    if "count" in cmd or "how many" in cmd:
        m = re.search(r"students.*(?:older|greater) than (\d+)", cmd)
        if m:
            return f"SELECT COUNT(*) FROM students WHERE age > {m.group(1)};"
        return "SELECT COUNT(*) FROM students;"
    
    if "average age" in cmd or "avg age" in cmd:
        return "SELECT AVG(age) FROM students;"
    if "maximum age" in cmd or "max age" in cmd:
        return "SELECT MAX(age) FROM students;"
    if "minimum age" in cmd or "min age" in cmd:
        return "SELECT MIN(age) FROM students;"
    
    # ORDER BY
    m = re.search(r"list students ordered by (\w+)", cmd)
    if m:
        order = "DESC" if "desc" in cmd or "descending" in cmd else "ASC"
        return f"SELECT * FROM students ORDER BY {m.group(1)} {order};"
    
    # JOIN example
    if "students with their class" in cmd:
        return "SELECT s.name, c.class_name FROM students s JOIN classes c ON s.class_id = c.id;"
    
    return None

# ----------------------------
# SQL explanation generator
# ----------------------------
def explain_sql(sql_query):
    sql = sql_query.lower()
    explanation = []
    
    if sql.startswith("select"):
        explanation.append("1️⃣ This query retrieves data from a table (SELECT).")
        if "where" in sql:
            explanation.append("2️⃣ It filters rows according to the WHERE condition.")
        if "order by" in sql:
            explanation.append("3️⃣ It sorts the results according to ORDER BY clause.")
        if "group by" in sql:
            explanation.append("4️⃣ It groups rows based on GROUP BY.")
        if "avg" in sql:
            explanation.append("5️⃣ It calculates the average of a column (AVG).")
        if "count" in sql:
            explanation.append("5️⃣ It counts the number of rows (COUNT).")
        if "max" in sql:
            explanation.append("5️⃣ It finds the maximum value in a column (MAX).")
        if "min" in sql:
            explanation.append("5️⃣ It finds the minimum value in a column (MIN).")
        if "join" in sql:
            explanation.append("6️⃣ It combines data from multiple tables (JOIN).")
    elif sql.startswith("insert"):
        explanation.append("1️⃣ This query adds a new row into a table (INSERT).")
        explanation.append("2️⃣ The column values are specified in VALUES clause.")
    elif sql.startswith("update"):
        explanation.append("1️⃣ This query updates existing rows in a table (UPDATE).")
        explanation.append("2️⃣ The rows are matched using the WHERE condition.")
    elif sql.startswith("delete"):
        explanation.append("1️⃣ This query deletes rows from a table (DELETE).")
        explanation.append("2️⃣ The rows are matched using the WHERE condition.")
    else:
        explanation.append("ℹ️ This is a raw SQL query.")
    
    return "\n".join(explanation)

# ----------------------------
# Streamlit UI
# ----------------------------
st.set_page_config(page_title="SQL Tutor Bot", layout="wide")
st.title("🤖 SQL Tutor Bot")
st.write("Type your SQL query or plain English instruction below:")

# Session state to store chat history
if "history" not in st.session_state:
    st.session_state.history = []

user_input = st.text_input("You:", "")

if user_input:
    st.session_state.history.append({"role": "user", "message": user_input})
    
    db = connect_db()
    if not db:
        st.stop()
    
    sql_query = english_to_sql(user_input)
    
    if sql_query is None:
        sql_query = user_input if re.match(r"^\s*(select|insert|update|delete|create|alter|drop)\b", user_input, re.I) else None
        if sql_query is None:
            st.warning("⚠️ I don't understand that command.")
    
    if sql_query:
        st.session_state.history.append({"role": "bot", "message": f"SQL Generated:\n{sql_query}"})
        explanation = explain_sql(sql_query)
        st.session_state.history.append({"role": "bot", "message": f"Explanation:\n{explanation}"})
        
        try:
            cursor = db.cursor()
            cursor.execute(sql_query)
            if sql_query.lower().startswith("select"):
                rows = cursor.fetchall()
                if rows:
                    df = pd.DataFrame(rows, columns=[d[0] for d in cursor.description])
                    st.session_state.history.append({"role": "bot", "message": "Results:"})
                    st.session_state.history.append({"role": "bot", "message": df})
                else:
                    st.session_state.history.append({"role": "bot", "message": "✅ No data found."})
            else:
                db.commit()
                st.session_state.history.append({"role": "bot", "message": "✅ Query executed successfully."})
        except Exception as e:
            st.session_state.history.append({"role": "bot", "message": f"❌ Error: {e}"})
            traceback.print_exc()
    db.close()

# Display chat history
for chat in st.session_state.history:
    if chat["role"] == "user":
        st.markdown(f"**You:** {chat['message']}")
    else:
        if isinstance(chat["message"], pd.DataFrame):
            st.dataframe(chat["message"])
        else:
            st.markdown(f"**Bot:** {chat['message']}")
