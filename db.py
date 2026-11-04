import csv
import sqlite3

DB_FILE = 'produits.db'
CSV_FILE = 'db.csv'


def get_conn(db_file=DB_FILE):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produits (
            Id          TEXT PRIMARY KEY,
            Nom         TEXT,
            Description TEXT,
            Categorie   TEXT,
            Prix        REAL,
            Stock       INTEGER,
            Promotion   TEXT
        )
    ''')
    conn.commit()
    return conn


def csv_to_db(csv_file=CSV_FILE, db_file=DB_FILE):
    conn = get_conn(db_file)
    cursor = conn.cursor()

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        rows = [
            (
                row['Id'],
                row['Nom'],
                row['Description'],
                row['Categorie'],
                float(row['Prix (€)'].replace(',', '.')),
                int(row['Stock']),
                row['Promotion']
            )
            for row in reader
        ]

    cursor.executemany(
        "INSERT OR REPLACE INTO produits VALUES (?, ?, ?, ?, ?, ?, ?)",
        rows
    )
    conn.commit()
    count = cursor.rowcount
    conn.close()
    print(f"{count} row(s) inserted.")
    return count


def get_produit(id_objet, db_file=DB_FILE):
    conn = get_conn(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produits WHERE Id = ?", (str(id_objet),))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            'Id': row[0], 'Nom': row[1], 'Description': row[2],
            'Categorie': row[3], 'Prix': row[4], 'Stock': row[5], 'Promotion': row[6]
        }
    return None


def get_all(db_file=DB_FILE):
    conn = get_conn(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produits")
    rows = cursor.fetchall()
    conn.close()
    return [
        {'Id': r[0], 'Nom': r[1], 'Description': r[2],
         'Categorie': r[3], 'Prix': r[4], 'Stock': r[5], 'Promotion': r[6]}
        for r in rows
    ]


def update_produit(id_objet, data: dict, db_file=DB_FILE):
    allowed = {'Nom', 'Description', 'Categorie', 'Prix', 'Stock', 'Promotion'}
    data = {k: v for k, v in data.items() if k in allowed}

    if not data:
        print("Aucun champ valide à mettre à jour.")
        return 0

    set_clause = ', '.join(f"{col} = ?" for col in data)
    values = list(data.values()) + [str(id_objet)]

    conn = get_conn(db_file)
    cursor = conn.cursor()
    cursor.execute(f"UPDATE produits SET {set_clause} WHERE Id = ?", values)
    conn.commit()
    count = cursor.rowcount
    conn.close()
    print(f"{count} row(s) updated.")
    return count


def delete_produit(id_objet, db_file=DB_FILE):
    conn = get_conn(db_file)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM produits WHERE Id = ?", (str(id_objet),))
    conn.commit()
    count = cursor.rowcount
    conn.close()
    print(f"{count} row(s) deleted.")
    return count

if __name__ == '__main__':
    csv_to_db()
    print(get_all())
    update_produit(1, {"Nom": "Banane", "Prix": 2.5})
    print(get_produit(1))
    delete_produit(2)
    print(get_all())   
