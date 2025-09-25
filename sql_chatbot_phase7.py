# sql_tutor_bot_phase7.py
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
            password="1234",     # <-- update if needed
            database="sql_chatbot"
        )
        return conn
    except Exception as e:
        return None

# ----------------------------
# English -> SQL translator (basic + intermediate patterns)
# ----------------------------
def english_to_sql(cmd: str):
    cmd = cmd.lower().strip()

    # show/list students
    if re.search(r"\b(show|list|display|get)\b(?:\s+all)?\s+students?\b", cmd):
        return "SELECT * FROM students;"

    # insert: add student NAME, age N
    m = re.search(
        r"(?:add|insert)\s+(?:a\s+)?(?:student\s+)?['\"]?([a-zA-Z0-9_ ]+)['\"]?(?:[, ]+\s*(?:age|aged)\s*[: ]\s*(\d+))?",
        cmd
    )
    if m:
        name, age = m.group(1).strip(), m.group(2)
        name_sql = name.replace("'", "''")
        if age:
            return f"INSERT INTO students (name, age) VALUES ('{name_sql}', {age});"
        return f"INSERT INTO students (name) VALUES ('{name_sql}');"

    # update: update NAME age to N
    m = re.search(r"(?:update|set)\s+['\"]?([a-zA-Z0-9_ ]+)['\"]?(?:'s)?\s+age\s+(?:to|=)\s*(\d+)", cmd)
    if m:
        name, age = m.group(1).strip(), m.group(2)
        name_sql = name.replace("'", "''")
        return f"UPDATE students SET age={age} WHERE name='{name_sql}';"

    # delete: delete student NAME
    m = re.search(r"(?:delete|remove)\s+(?:student\s+)?['\"]?([a-zA-Z0-9_ ]+)['\"]?", cmd)
    if m:
        name = m.group(1).strip().replace("'", "''")
        return f"DELETE FROM students WHERE name='{name}';"

    # aggregations: count / avg / min / max
    if re.search(r"\b(how many|count)\b", cmd):
        m = re.search(r"students.*(?:older|greater) than (\d+)", cmd)
        if m:
            return f"SELECT COUNT(*) AS total_students FROM students WHERE age > {m.group(1)};"
        if "per class" in cmd:
            return "SELECT class_id, COUNT(*) AS total_students FROM students GROUP BY class_id;"
        return "SELECT COUNT(*) AS total_students FROM students;"
    if re.search(r"\b(average age|avg age)\b", cmd):
        if "per class" in cmd:
            return "SELECT class_id, AVG(age) AS avg_age FROM students GROUP BY class_id;"
        return "SELECT AVG(age) AS avg_age FROM students;"
    if re.search(r"\b(maximum age|max age)\b", cmd):
        return "SELECT MAX(age) AS max_age FROM students;"
    if re.search(r"\b(minimum age|min age)\b", cmd):
        return "SELECT MIN(age) AS min_age FROM students;"

    # order by
    m = re.search(r"list students ordered by (\w+)", cmd)
    if m:
        order = "DESC" if "descending" in cmd or "desc" in cmd else "ASC"
        return f"SELECT * FROM students ORDER BY {m.group(1)} {order};"

    # join example
    if "students with their class" in cmd or "students with classes" in cmd:
        return "SELECT s.name, c.class_name FROM students s JOIN classes c ON s.class_id = c.id;"

    return None

# ----------------------------
# Explain SQL (improved beginner explanations)
# ----------------------------
def explain_sql(sql: str):
    sql_low = sql.lower()
    lines = []
    if sql_low.startswith("select"):
        lines.append("• SELECT: what columns to show (or * for all).")
        if "from" in sql_low:
            lines.append("• FROM: which table we read rows from.")
        if "where" in sql_low:
            lines.append("• WHERE: filters which rows are returned.")
        if "group by" in sql_low:
            lines.append("• GROUP BY: groups rows together to compute aggregates (like COUNT, AVG).")
        if "order by" in sql_low:
            lines.append("• ORDER BY: sorts rows by a column (ASC or DESC).")
        if re.search(r"count\(|avg\(|max\(|min\(", sql_low):
            lines.append("• Aggregate functions compute summary values: COUNT, AVG, MAX, MIN.")
        if "join" in sql_low:
            lines.append("• JOIN: combines rows from multiple tables where keys match.")
    elif sql_low.startswith("insert"):
        lines.append("• INSERT INTO: adds a new row to the table.")
        m = re.search(r"insert into\s+([^\(]+)\s*\((.*?)\)\s*values\s*\((.*?)\)", sql_low, re.I)
        if m:
            cols = [c.strip() for c in m.group(2).split(",")]
            vals = [v.strip() for v in m.group(3).split(",")]
            for c, v in zip(cols, vals):
                lines.append(f"  - Column `{c}` will receive value {v}")
            lines.append("• After insertion you can query the row with SELECT.")
    elif sql_low.startswith("update"):
        lines.append("• UPDATE: changes existing rows.")
        if "set" in sql_low:
            lines.append("• SET: lists columns and their new values.")
        if "where" in sql_low:
            lines.append("• WHERE: only rows matching this are changed.")
    elif sql_low.startswith("delete"):
        lines.append("• DELETE FROM: removes rows from the table.")
        lines.append("• Be careful: without WHERE it deletes all rows.")
    else:
        lines.append("• This is a raw SQL statement.")
    return "\n".join(lines) if lines else "No explanation available."

# ----------------------------
# Raw SQL detector
# ----------------------------
def is_raw_sql(text: str):
    return re.match(r"^\s*(select|insert|update|delete|create|alter|drop)\b", text, flags=re.I) is not None

# ----------------------------
# Tiny local 'AI assistant' for DDL & beginner questions
# (template-based — not an external LLM)
# ----------------------------
def ai_assistant(prompt: str):
    p = prompt.lower().strip()
    # Create table examples
    m = re.search(r"create (?:a )?table(?: for)?\s*([a-z_][a-z0-9_]*)?", p)
    if m:
        tbl = m.group(1) or "your_table"
        # simple heuristic templates for 'students'
        if "student" in p or tbl.startswith("student"):
            tpl = (
                f"-- Example CREATE TABLE for `{tbl}`\n"
                "CREATE TABLE students (\n"
                "  id INT AUTO_INCREMENT PRIMARY KEY,\n"
                "  name VARCHAR(100) NOT NULL,\n"
                "  age INT,\n"
                "  class_id INT  -- optional: link to classes table\n"
                ");\n\n"
                "-- You can insert sample data:\n"
                "INSERT INTO students (name, age) VALUES ('John', 20), ('Alice', 22);\n"
            )
            expl = (
                "This creates a students table with an auto-increment id (unique), a name, and age.\n"
                "If you want classes, create a `classes` table and add a `class_id` foreign key in students."
            )
            return tpl + "\n-- Explanation:\n" + expl

        # generic table template
        tpl = (
            f"-- Example CREATE TABLE for `{tbl}`\n"
            f"CREATE TABLE {tbl} (\n"
            "  id INT AUTO_INCREMENT PRIMARY KEY,\n"
            "  column1 VARCHAR(255),\n"
            "  column2 INT\n"
            ");\n"
        )
        return tpl + "\n-- Explanation:\nA basic table with an id and two columns. Update types/names to match your data."

    # add column
    m = re.search(r"(?:add|alter)\s+(?:column|field)\s+(\w+)\s+to\s+([a-z_][a-z0-9_]*)", p)
    if m:
        col, tbl = m.group(1), m.group(2)
        return (f"-- Example to add column `{col}` to `{tbl}`:\n"
                f"ALTER TABLE {tbl} ADD COLUMN {col} VARCHAR(255);\n\n"
                "Modify the type as needed (INT, DATE, etc.).")

    # explanation requests
    if "what is join" in p or p.startswith("explain join") or "explain joins" in p:
        return (
            "JOIN explanation:\n"
            "- A JOIN combines rows from two tables when a related column matches.\n"
            "Example:\n"
            "SELECT s.name, c.class_name\n"
            "FROM students s\n"
            "JOIN classes c ON s.class_id = c.id;\n"
            "This shows student names together with their class name."
        )

    if "group by" in p or "explain group by" in p:
        return (
            "GROUP BY explanation:\n"
            "- GROUP BY groups rows that have the same value in specified columns so you can compute aggregates per group.\n"
            "Example:\n"
            "SELECT class_id, COUNT(*) AS total_students\n"
            "FROM students\n"
            "GROUP BY class_id;"
        )

    if "pivot" in p:
        return (
            "Pivot example (MySQL 8+ using row_number):\n"
            "WITH numbered AS (\n"
            "  SELECT name, occupation,\n"
            "         ROW_NUMBER() OVER (PARTITION BY occupation ORDER BY name) AS rn\n"
            "  FROM occupations\n"
            ")\n"
            "SELECT\n"
            "  MAX(CASE WHEN occupation='Doctor' THEN name END) AS Doctor,\n"
            "  MAX(CASE WHEN occupation='Professor' THEN name END) AS Professor,\n"
            "  MAX(CASE WHEN occupation='Singer' THEN name END) AS Singer,\n"
            "  MAX(CASE WHEN occupation='Actor' THEN name END) AS Actor\n"
            "FROM numbered\n"
            "GROUP BY rn;\n\n"
            "This lists names by occupation in columns; empty cells become NULL."
        )

    # default fallback
    if p.endswith("?") or p.startswith("how") or p.startswith("what") or "create table" in p or "add column" in p:
        return ("I can generate example DDL or explain SQL concepts. Try:\n"
                "- 'Create table students'\n"
                "- 'Explain JOIN'\n"
                "- 'How to add column class_id to students'\n")
    return None

# ----------------------------
# Utilities: check DB shape
# ----------------------------
def table_exists(cursor, table_name):
    try:
        cursor.execute("SHOW TABLES;")
        tables = [t[0].lower() for t in cursor.fetchall()]
        return table_name.lower() in tables
    except:
        return False

def column_exists(cursor, table, column):
    try:
        cursor.execute(f"SHOW COLUMNS FROM {table};")
        cols = [c[0].lower() for c in cursor.fetchall()]
        return column.lower() in cols
    except:
        return False

# ----------------------------
# Streamlit UI & Flow
# ----------------------------
st.set_page_config(page_title="SQL Tutor Bot (Interactive)", layout="wide")
st.title("🤖 SQL Tutor Bot — Interactive Hints & AI Assistant")
st.write("Type a question in English (or raw SQL). I will show the SQL I plan to run and ask for confirmation before executing it.")

# use form to avoid instant execution on input change
with st.form("query_form"):
    user_input = st.text_input("Enter SQL or English command", "")
    auto_run = st.checkbox("Auto-run (run without confirmation)", value=False)
    submit = st.form_submit_button("Submit")

if submit:
    st.markdown(f"**You:** {user_input}")

    # 1) Try English -> SQL
    generated_sql = english_to_sql(user_input)
    raw_sql_flag = False
    if generated_sql is None:
        if is_raw_sql(user_input):
            generated_sql = user_input if user_input.strip().endswith(";") else user_input + ";"
            raw_sql_flag = True
        else:
            # ask AI assistant if user requested explanation or DDL
            ai_resp = ai_assistant(user_input)
            if ai_resp:
                st.markdown("### 🤖 AI Assistant (suggestion / template)")
                st.code(ai_resp, language="sql")
                st.info("You can copy the above SQL, paste it in the input, and press Submit to run it.")
            else:
                st.warning("I don't understand that command. Try simple English like 'show students' or ask 'Create table students'.")
            st.stop()

    # 2) Show mapping and explanation (always show)
    st.markdown("### 🔎 SQL I will run (preview)")
    st.code(generated_sql, language="sql")
    st.markdown("### 💬 Explanation")
    st.text(explain_sql(generated_sql))

    # 3) If auto_run checked, run immediately, else show confirm buttons
    if not auto_run:
        col1, col2, col3 = st.columns([1,1,2])
        run_btn = col1.button("✅ Run SQL", key="run")
        more_help_btn = col2.button("❓ Ask AI Assistant", key="aihelp")
        cancel_btn = col3.button("✖ Cancel", key="cancel")

        # Ask AI assistant for detailed help/templates
        if more_help_btn:
            ai_resp = ai_assistant(user_input)
            if ai_resp:
                st.markdown("### 🤖 AI Assistant (detailed help)")
                st.code(ai_resp, language="sql")
            else:
                st.info("No specific template found. Try 'Create table students' or 'Explain JOIN'.")
            st.stop()

        if cancel_btn:
            st.info("Cancelled — will not run the SQL.")
            st.stop()
    else:
        run_btn = True

    if run_btn:
        conn = connect_db()
        if not conn:
            st.error("Cannot connect to database. Check credentials and that MySQL is running.")
            st.stop()

        cur = conn.cursor()
        try:
            # Executing the SQL safely (user already confirmed)
            cur.execute(generated_sql)
            if generated_sql.strip().lower().startswith("select"):
                rows = cur.fetchall()
                if rows:
                    df = pd.DataFrame(rows, columns=[d[0] for d in cur.description])
                    st.markdown("### 📋 Results")
                    st.dataframe(df, use_container_width=True)
                else:
                    st.success("✅ Query executed successfully — no rows returned.")
            else:
                conn.commit()
                st.success("✅ Query executed successfully.")
            # success explanation
            st.markdown("### 📘 After running")
            st.text("If you want a detailed explanation of what happened, ask: 'explain that' or review the SQL above.")
        except mysql.connector.errors.ProgrammingError as e:
            msg = str(e)
            st.error(f"❌ SQL Error: {msg}")
            # friendly hints for common errors
            if "Unknown column" in msg:
                st.info("Hint: one of the columns in your SQL doesn't exist. Use `SHOW COLUMNS FROM table_name;` to inspect the table schema.")
            elif "Unknown table" in msg or "doesn't exist" in msg:
                st.info("Hint: referenced table does not exist. You can ask the AI assistant to generate a CREATE TABLE template (click 'Ask AI Assistant').")
            else:
                st.text(traceback.format_exc())
        except Exception as e:
            st.error(f"❌ Unexpected error: {e}")
            st.text(traceback.format_exc())
        finally:
            cur.close()
            conn.close()
