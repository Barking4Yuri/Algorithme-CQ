import os
import csv
import sqlite3
import main

TEST_CSV = 'test.csv'
TEST_DB = 'test.db'
N = 6 

def setup(n=N):
    main.CSV_FILE = TEST_CSV
    main.DB_FILE = TEST_DB

    with open(TEST_CSV, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['Id', 'Nom', 'Description', 'Categorie', 'Prix (€)', 'Stock', 'Promotion'], delimiter=';')
        writer.writeheader()
        for i in range(1, n + 1):
            writer.writerow({
                'Id': str(i),
                'Nom': f'Produit{i}',
                'Description': f'Desc {i}',
                'Categorie': 'Test',
                'Prix (€)': f'{i * 0.5:.2f}',
                'Stock': str(i * 2),
                'Promotion': '1.0'
            })

    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    main.sync_db()

def cleanup():
    for f in [TEST_CSV, TEST_DB]:
        if os.path.exists(f):
            os.remove(f)


def test_get_all():
    setup()
    rows = main.get_all()
    assert len(rows) == N, f"Attendu {N}, obtenu {len(rows)}"
    print("get_all réussie")
    cleanup()

def test_get_produit():
    setup()
    assert main.get_produit(1)['Nom'] == 'Produit1'
    assert main.get_produit(999) is None
    print("get_produit réussie")
    cleanup()

def test_tri_prix():
    setup()
    asc = main.get_by_price('asc')
    desc = main.get_by_price('desc')
    assert asc[0]['Nom'] == 'Produit1'
    assert desc[0]['Nom'] == f'Produit{N}'
    print("get_by_price réussie")
    cleanup()

def test_update():
    setup()
    main.update_produit(1, {"Nom": "Modifie"})
    assert main.get_produit(1)['Nom'] == 'Modifie'
    print("update réussie")
    cleanup()

def test_delete():
    setup()
    main.delete_produit(1)
    assert main.get_produit(1) is None
    assert len(main.get_all()) == N - 1
    print("delete réussie")
    cleanup()

def test_add():
    setup()
    main.add_produit({"Nom": "Nouveau", "Prix": "9.99", "Stock": 1, "Promotion": "1.0"})
    assert main.get_produit(N + 1)['Nom'] == 'Nouveau'
    print("add réussie")
    cleanup()

def test_db_sync():
    setup()
    main.update_produit(1, {"Nom": "DB Test"})
    conn = sqlite3.connect(TEST_DB)
    cur = conn.cursor()
    cur.execute("SELECT Nom FROM produits WHERE Id = '1'")
    assert cur.fetchone()[0] == 'DB Test'
    conn.close()
    print("db sync réussie")
    cleanup()

if __name__ == '__main__':
    test_get_all()
    test_get_produit()
    test_tri_prix()
    test_update()
    test_delete()
    test_add()
    test_db_sync()
    print("\n✅ Tous les tests passent !")   
