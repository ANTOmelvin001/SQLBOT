# sqlbot_phase5.py
import mysql.connector
import re
import sys
import traceback

# ----------------------------
# Connect to MySQL
# ----------------------------
try:
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="sql_chatbot"
    )
    cursor = db.cursor()
    print("🤖 Connected to MySQL successfully! ✅")
except Exception as e:
    print("🤖 Connection Error:", e)
    sys.exit(1)

# ----------------------------
# English → SQL Translator (Phase 2+3+Intermediate)
# ----------------------------
def english_to_sql(cmd: str):
    cmd = cmd.lower().strip()

    # --- SELECT all students
    if re.search(r"\b(show|list|display|get)\b(?:\s+all)?\s+students?\b", cmd):
        return "SELECT * FROM students;"

    # --- INSERT
    m = re.search(r"(?:add|insert)\s+(?:a\s+)?(?:student\s+)?['\"]?(\w+)['\"]?(?:[, ]+\s*(?:age|aged)\s*[: ]\s*(\d+))?", cmd)
    if m:
        name, age = m.group(1), m.group(2)
        if age:
            return f"INSERT INTO students (name, age) VALUES ('{name}', {age});"
        return f"INSERT INTO students (name) VALUES ('{name}');"

    # --- UPDATE
    m = re.search(r"(?:update|set)\s+['\"]?(\w+)['\"]?(?:'s)?\s+age\s+(?:to|=)\s*(\d+)", cmd)
    if m:
        return f"UPDATE students SET age={m.group(2)} WHERE name='{m.group(1)}';"

    # --- DELETE
    m = re.search(r"(?:delete|remove)\s+(?:student\s+)?['\"]?(\w+)['\"]?", cmd)
    if m:
        return f"DELETE FROM students WHERE name='{m.group(1)}';"

    # --- Aggregations
    if "count" in cmd or "how many" in cmd:
        m = re.search(r"students.*(?:older|greater) than (\d+)", cmd)
        if m:
            return f"SELECT COUNT(*) AS total_students FROM students WHERE age > {m.group(1)};"
        if "per class" in cmd:
            return "SELECT class_id, COUNT(*) AS total_students FROM students GROUP BY class_id;"
        return "SELECT COUNT(*) AS total_students FROM students;"

    if "average age" in cmd or "avg age" in cmd:
        if "per class" in cmd:
            return "SELECT class_id, AVG(age) AS avg_age FROM students GROUP BY class_id;"
        return "SELECT AVG(age) AS avg_age FROM students;"

    if "maximum age" in cmd or "max age" in cmd:
        return "SELECT MAX(age) AS max_age FROM students;"

    if "minimum age" in cmd or "min age" in cmd:
        return "SELECT MIN(age) AS min_age FROM students;"

    # --- ORDER BY
    m = re.search(r"list students ordered by (\w+)", cmd)
    if m:
        order = "DESC" if "desc" in cmd or "descending" in cmd else "ASC"
        return f"SELECT * FROM students ORDER BY {m.group(1)} {order};"

    # --- JOIN example (students + classes)
    if "students with their class" in cmd:
        return "SELECT s.name, c.class_name FROM students s JOIN classes c ON s.class_id = c.id;"

    return None

# ----------------------------
# Explanation Generator
# ----------------------------
def explain_query(sql_query: str):
    sql = sql_query.lower()
    explanation = []

    if sql.startswith("select"):
        explanation.append("1. This query retrieves data from a table (SELECT).")
        if "where" in sql:
            explanation.append("2. It filters rows using the WHERE clause.")
        if "group by" in sql:
            explanation.append("3. It groups rows based on columns for aggregation (GROUP BY).")
        if "count" in sql:
            explanation.append("4. COUNT counts rows in each group or total rows.")
        if "avg" in sql:
            explanation.append("4. AVG calculates the average of a numeric column.")
        if "max" in sql:
            explanation.append("4. MAX returns the maximum value in a column.")
        if "min" in sql:
            explanation.append("4. MIN returns the minimum value in a column.")
        if "order by" in sql:
            explanation.append("5. ORDER BY sorts the results by the given column.")
        if "join" in sql:
            explanation.append("6. JOIN combines rows from two tables based on a related column.")
    elif sql.startswith("insert"):
        explanation.append("1. This query adds a new row to the table (INSERT).")
        m = re.search(r"insert into students \(name, age\) values \('(\w+)', (\d+)\);", sql)
        if m:
            explanation.append(f"2. Name inserted: {m.group(1)}, Age inserted: {m.group(2)}")
    elif sql.startswith("update"):
        explanation.append("1. This query modifies existing rows in the table (UPDATE).")
        m = re.search(r"update students set age=(\d+) where name='(\w+)';", sql)
        if m:
            explanation.append(f"2. Sets age={m.group(1)} for student '{m.group(2)}'")
    elif sql.startswith("delete"):
        explanation.append("1. This query removes rows from the table (DELETE).")
        m = re.search(r"delete from students where name='(\w+)';", sql)
        if m:
            explanation.append(f"2. Deletes the student '{m.group(1)}' from the table.")

    return "\n".join(explanation) if explanation else "No explanation available."

# ----------------------------
# Raw SQL detection
# ----------------------------
def is_raw_sql(text):
    return re.match(r"^\s*(select|insert|update|delete|create|alter|drop)\b", text, flags=re.I)

# ----------------------------
# Main Chatbot Loop
# ----------------------------
print("🤖 SQL Tutor Chatbot Ready! Type 'exit' to quit.\n")

while True:
    user_input = input("You: ").strip()
    if not user_input:
        continue
    if user_input.lower() == "exit":
        print("🤖 Goodbye!")
        break

    # 1) English → SQL
    sql_query = english_to_sql(user_input)

    # 2) Allow raw SQL if unrecognized
    if sql_query is None:
        if is_raw_sql(user_input):
            sql_query = user_input if user_input.endswith(";") else user_input + ";"
        else:
            print("🤖 Sorry, I don't understand that command.")
            continue

    print("🤖 SQL Generated (executing):", sql_query)

    # 3) Execute and explain
    try:
        cursor.execute(sql_query)
        explanation = explain_query(sql_query)

        if sql_query.lower().startswith("select"):
            rows = cursor.fetchall()
            if rows:
                col_names = [d[0] for d in cursor.description]
                print(" | ".join(col_names))
                print("-" * max(20, len(" | ".join(col_names))))
                for r in rows:
                    print(" | ".join(str(x) for x in r))
                print(f"\n🤖 Found {len(rows)} record(s)")
            else:
                print("🤖 No results found.")
        else:
            db.commit()
            print("🤖 Query executed successfully!")

        print("🤖 Explanation:\n", explanation, "\n")

    except Exception as ex:
        print("🤖 Error executing SQL:", ex)
        traceback.print_exc()
