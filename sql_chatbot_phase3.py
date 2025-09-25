import re

def english_to_sql(command: str):
    cmd = command.lower().strip()

    # --- Basic SELECT all students
    if re.search(r"\b(show|list|display|get)\b(?:\s+all)?\s+\bstudents?\b", cmd):
        return "SELECT * FROM students;"

    # --- INSERT student
    m = re.search(r"(?:add|insert)\s+(?:a\s+)?(?:student\s+)?['\"]?([a-zA-Z0-9_]+)['\"]?(?:[, ]+\s*(?:age|aged)\s*[: ]\s*(\d+))?", cmd)
    if m:
        name, age = m.group(1), m.group(2)
        if age:
            return f"INSERT INTO students (name, age) VALUES ('{name}', {age});"
        return f"INSERT INTO students (name) VALUES ('{name}');"

    # --- UPDATE student age
    m = re.search(r"(?:update|set)\s+['\"]?([a-zA-Z0-9_]+)['\"]?(?:'s)?\s+age\s+(?:to|=)\s*(\d+)", cmd)
    if m:
        name, age = m.group(1), m.group(2)
        return f"UPDATE students SET age={age} WHERE name='{name}';"

    # --- DELETE student
    m = re.search(r"(?:delete|remove)\s+(?:student\s+)?['\"]?([a-zA-Z0-9_]+)['\"]?", cmd)
    if m:
        name = m.group(1)
        return f"DELETE FROM students WHERE name='{name}';"

    # --- Aggregation
    if re.search(r"\bhow many\b|\bcount\b", cmd):
        # e.g., "How many students are older than 20?"
        m = re.search(r"students.*(?:older|greater) than (\d+)", cmd)
        if m:
            age = m.group(1)
            return f"SELECT COUNT(*) FROM students WHERE age > {age};"
        return "SELECT COUNT(*) FROM students;"

    if re.search(r"\baverage age\b|\bavg age\b", cmd):
        return "SELECT AVG(age) FROM students;"

    if re.search(r"\bmaximum age\b|\bmax age\b", cmd):
        return "SELECT MAX(age) FROM students;"

    if re.search(r"\bminimum age\b|\bmin age\b", cmd):
        return "SELECT MIN(age) FROM students;"

    # --- ORDER BY
    m = re.search(r"list students ordered by (\w+)", cmd)
    if m:
        col = m.group(1)
        order = "ASC"
        if "descending" in cmd or "desc" in cmd:
            order = "DESC"
        return f"SELECT * FROM students ORDER BY {col} {order};"

    # --- JOIN example (students + classes)
    if re.search(r"students with their class", cmd):
        return ("SELECT s.name, c.class_name "
                "FROM students s "
                "JOIN classes c ON s.class_id = c.id;")

    return None
