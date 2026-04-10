import re
with open("pro_newmedia/settings.py", "r") as f:
    text = f.read()

# Replace the SQLite production block
text = re.sub(
    r"if not DEBUG and _db_engine == \"django.db.backends.sqlite3\":.*?raise RuntimeError.*?\"\"\".*?\)",
    "",
    text,
    flags=re.DOTALL
)
with open("pro_newmedia/settings.py", "w") as f:
    f.write(text)
