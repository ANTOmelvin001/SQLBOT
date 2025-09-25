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
# English -> SQL translator
# ----------------------------
def english_to_sql(command: str):
    cmd = command.lower().strip()

    # Show students
    if re.search(r"\b(show|list|display|get)\b(?:\s+all)?\s+\bstudents?\b", cmd):
        return "SELECT * FROM students;"

    # Add student NAME [age N]
    m = re.search(r"(?:add|insert)\s+(?:a\s+)?(?:student\s+)?['\"]?([a-zA-Z0-9_]+)['\"]?(?:[, ]+\s*(?:age|aged)\s*[: ]\s*(\d+))?", cmd)
    if m:
        name = m.group(1)
        age = m.group(2)
        if age:
            return f"INSERT INTO students (name, age) VALUES ('{name}', {age});"
        return f"INSERT INTO students (name) VALUES ('{name}');"

    # Who is oldest / highest age
    if re.search(r"\b(oldest|highest age|who has the highest age)\b", cmd):
        return "SELECT name, age FROM students ORDER BY age DESC LIMIT 1;"

    # Update NAME age to N
    m = re.search(r"(?:update|set)\s+['\"]?([a-zA-Z0-9_]+)['\"]?(?:'s)?\s+age\s+(?:to|=)\s*(\d+)", cmd)
    if m:
        name, age = m.group(1), m.group(2)
        return f"UPDATE students SET age={age} WHERE name='{name}';"

    # Delete student NAME
    m = re.search(r"(?:delete|remove)\s+(?:student\s+)?['\"]?([a-zA-Z0-9_]+)['\"]?", cmd)
    if m:
        name = m.group(1)
        return f"DELETE FROM students WHERE name='{name}';"

    # Show students older than N
    m = re.search(r"\b(students?)\b.*\b(older|greater)\s+than\s+(\d+)", cmd)
    if m:
        age = m.group(3)
        return f"SELECT * FROM students WHERE age > {age};"

    # Show students younger than N
    m = re.search(r"\b(students?)\b.*\b(younger|less)\s+than\s+(\d+)", cmd)
    if m:
        age = m.group(3)
        return f"SELECT * FROM students WHERE age < {age};"

    return None

# ----------------------------
# Helper: detect raw SQL
# ----------------------------
def is_raw_sql(text: str):
    return re.match(r"^\s*(select|insert|update|delete|create|alter|drop)\b", text, flags=re.I) is not None

# ----------------------------
# Chatbot Loop (English + SQL)
# ----------------------------
print("🤖 SQL Chatbot Ready! Type 'exit' to quit.\n")

while True:
    user_input = input("You: ").strip()
    if not user_input:
        continue
    if user_input.lower() == "exit":
        print("🤖 Goodbye!")
        break

    # Try English -> SQL
    sql_query = english_to_sql(user_input)

    # If not recognized, allow raw SQL only
    if sql_query is None:
        if is_raw_sql(user_input):
            sql_query = user_input if user_input.strip().endswith(";") else user_input + ";"
            print("DEBUG: treated input as raw SQL (allowed).")
        else:
            print("🤖 Sorry, I don't understand that command. (Won't send raw English to DB)")
            continue

    print("🤖 SQL Generated (executing):", sql_query)

    try:
        cursor.execute(sql_query)
        if sql_query.lower().startswith("select"):
            rows = cursor.fetchall()
            if rows:
                col_names = [d[0] for d in cursor.description] or []
                print("\n🤖 Results:")
                if col_names:
                    print(" | ".join(col_names))
                    print("-" * max(20, len(" | ".join(col_names))))
                for r in rows:
                    print(" | ".join(str(x) for x in r))
                print(f"\n🤖 Found {len(rows)} record(s)\n")
            else:
                print("🤖 No results found.\n")
        else:
            db.commit()
            print("🤖 Query executed successfully!\n")
    except Exception as ex:
        print("🤖 Error executing SQL:", ex)
        traceback.print_exc()
