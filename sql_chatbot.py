import mysql.connector
import sys

# ----------------------------
# Connect to MySQL
# ----------------------------
try:
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",   # your MySQL password
        database="sql_chatbot"
    )
    cursor = db.cursor()
    print("🤖 Connected to MySQL successfully! ✅")
except Exception as e:
    print("🤖 Connection Error:", e)
    sys.exit(1)

# ----------------------------
# Chatbot Loop (Raw SQL)
# ----------------------------
print("🤖 SQL Chatbot Ready! Type 'exit' to quit.\n")

while True:
    query = input("You: ").strip()
    if not query:
        continue
    if query.lower() == "exit":
        print("🤖 Goodbye!")
        break

    try:
        cursor.execute(query)

        if query.lower().startswith("select"):
            rows = cursor.fetchall()
            if rows:
                col_names = [desc[0] for desc in cursor.description]
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
