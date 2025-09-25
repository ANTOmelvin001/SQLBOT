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
# English → SQL translator
# ----------------------------
def english_to_sql(command: str):
    cmd = command.lower().strip()

    # --- SELECT
    if re.search(r"\b(show|list|display|get)\b.*\bstudents?\b", cmd):
        return "SELECT * FROM students;"

    # --- INSERT
    m = re.search(r"(?:add|insert)\s+(?:a\s+)?(?:student\s+)?['\"]?([a-zA-Z0-9_]+)['\"]?(?:[, ]+\s*(?:age|aged)\s*[: ]\s*(\d+))?", cmd)
    if m:
        name, age = m.group(1), m.group(2)
        if age:
            return f"INSERT INTO students (name, age) VALUES ('{name}', {age});"
        return f"INSERT INTO students (name) VALUES ('{name}');"

    # --- UPDATE
    m = re.search(r"(?:update|set)\s+['\"]?([a-zA-Z0-9_]+)['\"]?(?:'s)?\s+age\s+(?:to|=)\s*(\d+)", cmd)
    if m:
        name, age = m.group(1), m.group(2)
        return f"UPDATE students SET age={age} WHERE name='{name}';"

    # --- DELETE
    m = re.search(r"(?:delete|remove)\s+(?:student\s+)?['\"]?([a-zA-Z0-9_]+)['\"]?", cmd)
    if m:
        name = m.group(1)
        return f"DELETE FROM students WHERE name='{name}';"

    # --- AGGREGATION: COUNT
    if re.search(r"\bhow many\b|\bcount\b", cmd):
        m = re.search(r"students.*(?:older|greater) than (\d+)", cmd)
        if m:
            age = m.group(1)
            return f"SELECT COUNT(*) FROM students WHERE age > {age};"
        return "SELECT COUNT(*) FROM students;"

    # --- AGGREGATION: AVG/MAX/MIN
    if re.search(r"\baverage age\b|\bavg age\b", cmd):
        return "SELECT AVG(age) FROM students;"
    if re.search(r"\bmaximum age\b|\bmax age\b", cmd):
        return "SELECT MAX(age) FROM students;"
    if re.search(r"\bminimum age\b|\bmin age\b", cmd):
        return "SELECT MIN(age) FROM students;"

    return None

# ----------------------------
# Detailed explanation generator
# ----------------------------
def explain_query(sql_query: str):
    sql = sql_query.lower()

    # INSERT
    if sql.startswith("insert"):
        m = re.search(r"insert into students\s*\((.*?)\)\s*values\s*\((.*?)\)", sql, re.I)
        if m:
            cols = m.group(1).split(",")
            vals = m.group(2).split(",")
            explanation = ["1. This query inserts a new row into the `students` table."]
            for c, v in zip(cols, vals):
                explanation.append(f"2. Column `{c.strip()}` will store the value {v.strip()}.")
            explanation.append(f"{len(cols)+2}. After execution, the new row exists in the table and can be retrieved with `SELECT * FROM students;`")
            return "\n".join(explanation)

    # SELECT
    elif sql.startswith("select"):
        explanation = ["1. This query retrieves data from the `students` table."]
        if "count" in sql:
            explanation.append("2. COUNT(*) counts the number of rows matching the condition.")
        if "avg" in sql:
            explanation.append("2. AVG(age) calculates the average of the `age` column.")
        if "max" in sql:
            explanation.append("2. MAX(age) finds the maximum value in the `age` column.")
        if "min" in sql:
            explanation.append("2. MIN(age) finds the minimum value in the `age` column.")
        if "where" in sql:
            explanation.append("3. The WHERE clause filters rows based on a condition.")
        if "order by" in sql:
            explanation.append("4. The ORDER BY clause sorts the results.")
        return "\n".join(explanation)

    # UPDATE
    elif sql.startswith("update"):
        m = re.search(r"update students set age\s*=\s*(\d+)\s*where name\s*=\s*'(\w+)'", sql, re.I)
        if m:
            age, name = m.group(1), m.group(2)
            return (f"1. This query updates an existing row in the `students` table.\n"
                    f"2. It changes the `age` of the student with name `{name}` to {age}.\n"
                    "3. Only rows matching the WHERE condition are updated.")

    # DELETE
    elif sql.startswith("delete"):
        m = re.search(r"delete from students where name\s*=\s*'(\w+)'", sql, re.I)
        if m:
            name = m.group(1)
            return (f"1. This query deletes a row from the `students` table.\n"
                    f"2. It removes the student whose name is `{name}`.\n"
                    "3. Only rows matching the WHERE condition are deleted.")

    return "No detailed explanation available."

# ----------------------------
# Main Chatbot Loop
# ----------------------------
print("🤖 SQL Tutor Bot – English → SQL with Step-by-Step Explanation\n")

while True:
    user_input = input("You: ").strip()
    if not user_input:
        continue
    if user_input.lower() == "exit":
        print("🤖 Goodbye!")
        break

    sql_query = english_to_sql(user_input)
    if sql_query:
        print("🤖 SQL Generated:", sql_query)
        explanation = explain_query(sql_query)
        print("🤖 Explanation:\n", explanation)
        try:
            cursor.execute(sql_query)
            if sql_query.lower().startswith("select"):
                rows = cursor.fetchall()
                if rows:
                    col_names = [d[0] for d in cursor.description]
                    print(" | ".join(col_names))
                    print("-" * max(20, len(" | ".join(col_names))))
                    for r in rows:
                        print(" | ".join(str(x) for x in r))
                else:
                    print("🤖 No results found.")
            else:
                db.commit()
                print("🤖 Query executed successfully!")
        except Exception as e:
            print("🤖 Error:", e)
    else:
        print("🤖 Sorry, I don’t understand that command yet.")
