import csv
import sqlite3
import argparse

DB_FILE = 'produits.db'
CSV_FILE = 'db.csv'
DELIMITER = ';'
HEADERS = ['Id', 'Nom', 'Description', 'Categorie', 'Prix (€)', 'Stock', 'Promotion']

def _read_csv():
    '''
    Lit le ficher CSV en le retournant sous forme de liste
    '''
    with open(CSV_FILE, 'r', encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f, delimiter=DELIMITER))

def _write_csv(rows):
    '''
    Ecrit dans le fichier CSV
    '''
    with open(CSV_FILE, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS, delimiter=DELIMITER)
        writer.writeheader()
        writer.writerows(rows)


def get_conn(db_file = DB_FILE): 
    '''
    retourne la connection avec la DB
    '''
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

def sync_db(db_file= DB_FILE):
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
        if 1 <= f < 0:
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

def get_produit_sql(con, id_produit):
    return con.execute('''
    SELECT * FROM produits WHERE Id = ?;
''', (id_produit))

def get_by_price_sql(con):
    return con.execute('''
    SELECT Id, Nom, Prix FROM produits ORDER BY Prix;
    ''')

def add_produit_sql(con, data :dict):
    if len(data) == 7:
        con.execute('''
        INSERT INTO Produits VALUES (?,?,?,?,?,?,?);
        ''', tuple(data.values()))

def update_sql(con, id_objet, data : dict):
    ref = get_produit_sql(con, id_objet)
    dic_ref = {"Id": ref[0],"Nom": ref[1], "Description" : ref[2], "Categorie" : ref[3], "Prix" : ref[4], "Stock" : ref[5], "Promotion" : ref[6]}

    for key in dic_ref.keys():
        if key not in data:
            data[key] = NULL
    data["Id"] = id_objet

    query = ''' UPDATE produits
                SET Nom = COALESCE(:Nom, Nom)
                    Description = COALESCE(:Description, Description)
                    Categorie = COALESCE(:Categorie, Categorie)
                    Prix = COALESCE(:Prix, Prix)
                    Stock = COALESCE(:Stock, Stock)
                    Promotion = COALESCE(:Promotion, Promotion)
                WHERE Id = :Id;
            '''
    
    con.execute(query, data)

def delete_produit_sql(con, id_objet):
    con.execute('''
    DELETE FROM produits WHERE Id = ?;
    ''', (id_objet,))

def afficher_produits(rows):
    if not rows:
        print("Aucun produit trouvé.")
        return

    for produit in rows:
        print("-" * 50)
        print(f"ID          : {produit['Id']}")
        print(f"Nom         : {produit['Nom']}")
        print(f"Description : {produit['Description']}")
        print(f"Catégorie   : {produit['Categorie']}")
        print(f"Prix        : {produit['Prix (€)']} €")
        print(f"Stock       : {produit['Stock']}")
        print(f"Promotion   : {produit['Promotion']}")
    print("-" * 50)

def main():
    parser = argparse.ArgumentParser(
        description="Gestion du catalogue de produits"
    )
    commandes = parser.add_mutually_exclusive_group()
    commandes.add_argument(
        "--list",
        action="store_true",
        help="Afficher tous les produits"
    )
    commandes.add_argument(
        "--sort-name",
        choices=["asc", "desc"],
        help="Trier les produits par nom"
    )
    commandes.add_argument(
        "--sort-price",
        choices=["asc", "desc"],
        help="Trier les produits par prix"
    )
    commandes.add_argument(
        "--search",
        type=str,
        help="Rechercher un produit par mot-clé"
    )
    commandes.add_argument(
        "--add",
        action="store_true",
        help="Ajouter un produit"
    )
    commandes.add_argument(
        "--update",
        type=str,
        metavar="ID",
        help="Modifier un produit"
    )
    commandes.add_argument(
        "--delete",
        type=str,
        metavar="ID",
        help="Supprimer un produit"
    )
    parser.add_argument("--nom")
    parser.add_argument("--description")
    parser.add_argument("--categorie")
    parser.add_argument("--prix")
    parser.add_argument("--stock")
    parser.add_argument("--promotion")
    args = parser.parse_args()
    if args.sort_name:
        afficher_produits(get_by_name(args.sort_name))
    elif args.sort_price:
        afficher_produits(get_by_price(args.sort_price))
    elif args.search:
        afficher_produits(search_produit(args.search))
    elif args.add:
        if args.nom is None or args.prix is None:
            parser.error("--add nécessite au minimum --nom et --prix")

        try:
            data = {
                "Nom": args.nom,
                "Description": args.description or "",
                "Categorie": args.categorie or "",
                "Prix": args.prix,
                "Stock": int(args.stock or 0),
                "Promotion": args.promotion or "1.0"
            }

            add_produit(data)

        except ValueError as e:
            parser.error(str(e))
    elif args.update:
        data = {}

        if args.nom is not None:
            data["Nom"] = args.nom
        if args.description is not None:
            data["Description"] = args.description
        if args.categorie is not None:
            data["Categorie"] = args.categorie
        if args.prix is not None:
            data["Prix"] = args.prix
        if args.stock is not None:
            data["Stock"] = int(args.stock)
        if args.promotion is not None:
            data["Promotion"] = args.promotion
        if not data:
            parser.error("Indiquez au moins un champ à modifier.")
        try:
            update_produit(args.update, data)
        except ValueError as e:
            parser.error(str(e))

    elif args.delete:
        delete_produit(args.delete)
    else:
        afficher_produits(get_all())


if __name__ == '__main__':
    main()
