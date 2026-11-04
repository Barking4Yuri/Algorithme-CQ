import csv
import sqlite3

DB_FILE = 'produits.db'
CSV_FILE = 'db.csv'
DELIMITER = ';'
HEADERS = ['Id', 'Nom', 'Description', 'Categorie', 'Prix (€)', 'Stock', 'Promotion']


def _read_csv():
    with open(CSV_FILE, 'r', encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f, delimiter=DELIMITER))


def _write_csv(rows):
    with open(CSV_FILE, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS, delimiter=DELIMITER)
        writer.writeheader()
        writer.writerows(rows)

def get_conn(db_file=None):
    if db_file is None:
        db_file = DB_FILE
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


def sync_db(db_file=None):
    if db_file is None:
        db_file = DB_FILE
    conn = get_conn(db_file)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM produits")

    with open(CSV_FILE, 'r', encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f, delimiter=DELIMITER)
        rows = [
            (
                r['Id'], r['Nom'], r['Description'], r['Categorie'],
                float(r['Prix (€)'].replace(',', '.')),
                int(r['Stock']),
                r['Promotion']
            )
            for r in reader
        ]

    cursor.executemany(
        "INSERT OR REPLACE INTO produits VALUES (?, ?, ?, ?, ?, ?, ?)",
        rows
    )
    conn.commit()
    conn.close()


def get_all():
    return _read_csv()


def get_produit(id_objet):
    for row in _read_csv():
        if row['Id'] == str(id_objet):
            return row
    return None
def _validate_promotion(value):
    try:
        f = float(value)
        if f < 0:
            raise ValueError
        return f
    except (ValueError, TypeError):
        raise ValueError(f"Promotion invalide : '{value}'. Doit être un nombre (ex: 1.0, 0.5, 1.5)")   

def get_by_price(order='asc'):
    rows = _read_csv()
    rows.sort(key=lambda r: float(r['Prix (€)'].replace(',', '.')), reverse=(order == 'desc'))
    return rows   

def add_produit(data: dict):
    if 'Promotion' in data:
        _validate_promotion(data['Promotion'])

    rows = _read_csv()
    new_id = str(max((int(r['Id']) for r in rows), default=0) + 1)

    rows.append({
        'Id': new_id,
        'Nom': data.get('Nom', ''),
        'Description': data.get('Description', ''),
        'Categorie': data.get('Categorie', ''),
        'Prix (€)': data.get('Prix', '0.0'),
        'Stock': data.get('Stock', 0),
        'Promotion': str(data.get('Promotion', '1.0'))
    })

    _write_csv(rows)
    sync_db()
    print(f"Produit {new_id} ajouté.")


def update_produit(id_objet, data: dict):
    if 'Promotion' in data:
        _validate_promotion(data['Promotion'])

    rows = _read_csv()
    updated = False

    for row in rows:
        if row['Id'] == str(id_objet):
            if 'Nom' in data:
                row['Nom'] = data['Nom']
            if 'Description' in data:
                row['Description'] = data['Description']
            if 'Categorie' in data:
                row['Categorie'] = data['Categorie']
            if 'Prix' in data:
                row['Prix (€)'] = data['Prix']
            if 'Stock' in data:
                row['Stock'] = data['Stock']
            if 'Promotion' in data:
                row['Promotion'] = str(data['Promotion'])
            updated = True
            break

    if updated:
        _write_csv(rows)
        sync_db()
        print(f"Produit {id_objet} mis à jour.")
    else:
        print(f"Produit {id_objet} introuvable.")   

def delete_produit(id_objet):
    rows = _read_csv()
    new_rows = [r for r in rows if r['Id'] != str(id_objet)]

    if len(new_rows) == len(rows):
        print(f"Produit {id_objet} introuvable.")
        return

    _write_csv(new_rows)
    sync_db()
    print(f"Produit {id_objet} supprimé.")


if __name__ == '__emain__':
    sync_db()
    print(get_all())
    update_produit(1, {"Nom": "Banane", "Prix": 2.5})
    print(get_produit(1))
    delete_produit(2)
    print(get_all())   


print(get_by_price('asc'))
