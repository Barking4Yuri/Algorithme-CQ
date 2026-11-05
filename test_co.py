import csv
import sqlite3
import os

CSV_FILE = "utilisateur.csv"
DB_FILE = "produits.db"

if not os.path.exists(CSV_FILE):
    print("utilisateur.csv not found!")
    exit()

conn = sqlite3.connect(DB_FILE)

conn.execute("""
CREATE TABLE IF NOT EXISTS utilisateurs (
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    role TEXT NOT NULL DEFAULT 'utilisateur',
    email TEXT NOT NULL UNIQUE,
    pseudo TEXT NOT NULL UNIQUE,
    motdepasse TEXT NOT NULL
)
""")

with open(CSV_FILE, "r", encoding="utf-8", newline="") as f:
    reader = csv.DictReader(f, delimiter=";")

    total = 0

    for row in reader:
        try:
            conn.execute("""
                INSERT OR IGNORE INTO utilisateurs
                (Id, role, email, pseudo, motdepasse)
                VALUES (?, ?, ?, ?, ?)
            """, (
                row["Id"],
                row["role"],
                row["email"],
                row["pseudo"].strip(),
                row["motdepasse"]
            ))

            total += 1

        except Exception as e:
            print("Erreur :", e)

conn.commit()

print("Migration terminée !")

users = conn.execute(
    "SELECT Id, pseudo, role FROM utilisateurs"
).fetchall()

for user in users:
    print(user)

conn.close()