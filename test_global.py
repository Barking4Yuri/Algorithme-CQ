
import os
import csv
import sqlite3
import tempfile
import db
from fonctions import compte
from fonctions import haveibeenpwned
reussis = 0
echoues = 0


def test(nom, fonction):
    global reussis, echoues
    try:
        fonction()
        print("[OK]", nom)
        reussis += 1
    except Exception as e:
        print("[ERREUR]", nom, "-", e)
        echoues += 1

def test_produits():
    ancien_csv = db.CSV_FILE
    ancienne_db = db.DB_FILE

    try:
        with tempfile.TemporaryDirectory() as dossier:
            db.CSV_FILE = os.path.join(dossier, "test.csv")
            db.DB_FILE = os.path.join(dossier, "test.db")

            with open(db.CSV_FILE, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=db.HEADERS,
                    delimiter=';'
                )
                writer.writeheader()

                for i in range(1, 7):
                    writer.writerow({
                        'Id': str(i),
                        'Nom': f'Produit{i}',
                        'Description': f'Description {i}',
                        'Categorie': 'Test',
                        'Prix (€)': str(i * 0.5),
                        'Stock': str(i * 2),
                        'Promotion': '1.0'
                    })

            db.sync_db()
            assert len(db.get_all()) == 6
            assert db.get_produit(1)['Nom'] == 'Produit1'
            assert db.get_produit(999) is None
            assert db.get_by_price('asc')[0]['Nom'] == 'Produit1'
            assert db.get_by_price('desc')[0]['Nom'] == 'Produit6'
            assert db.get_by_name('asc')[0]['Nom'] == 'Produit1'
            assert db.get_by_name('desc')[0]['Nom'] == 'Produit6'

            assert len(db.search_produit('Description 1')) == 1
            db.add_produit({
                'Nom': 'Nouveau',
                'Prix': '9.99',
                'Stock': 1,
                'Promotion': '1.0'
            })

            assert db.get_produit(7)['Nom'] == 'Nouveau'

            db.update_produit(1, {'Nom': 'Modifie'})
            assert db.get_produit(1)['Nom'] == 'Modifie'
            db.delete_produit(2)
            assert db.get_produit(2) is None

            conn = sqlite3.connect(db.DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM produits")
            assert cursor.fetchone()[0] == 6
            conn.close()

    finally:
        db.CSV_FILE = ancien_csv
        db.DB_FILE = ancienne_db


def test_utilisateurs():
    ancien_csv = compte.CSV_FILE
    anciens_utilisateurs = compte.utilisateurs
    try:
        with tempfile.TemporaryDirectory() as dossier:
            fichier = os.path.join(dossier, "utilisateur.csv")
            compte.CSV_FILE = fichier

            with open(fichier, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=compte.HEADERS,
                    delimiter=';'
                )
                writer.writeheader()

            compte.utilisateurs = {}

            resultat = compte.creation_compte(
                'test@mail.com',
                'user_test',
                'MdpTest123!'
            )
            assert resultat is True
            utilisateurs = compte.charger_utilisateurs(fichier)
            assert 'user_test' in utilisateurs
            assert utilisateurs['user_test']['email'] == 'test@mail.com'
            assert utilisateurs['user_test']['role'] == 'utilisateur'

            assert compte.check_login(
                'user_test',
                'MdpTest123!',
                utilisateurs
            )

            assert not compte.check_login(
                'user_test',
                'mauvais_mdp',
                utilisateurs
            )

            assert not compte.check_login(
                'inconnu',
                'password',
                utilisateurs
            )

    finally:
        compte.CSV_FILE = ancien_csv
        compte.utilisateurs = anciens_utilisateurs


def test_hibp():
    resultat = haveibeenpwned.check_hibp("password123")
    assert resultat > 0

    suggestions = haveibeenpwned.suggestions("abc")
    assert len(suggestions) > 0


if __name__ == "__main__":
    print("\n--- TESTS DU PROJET ---\n")

    test("Produits CSV et SQLite", test_produits)
    test("Utilisateurs et connexion", test_utilisateurs)
    test("Have I Been Pwned", test_hibp)

    print("\n--- RESULTATS ---")
    print("Tests réussis :", reussis)
    print("Tests échoués :", echoues)

    if echoues == 0:
        print("\nTous les tests sont réussis !")
    else:
        print("\nCertains tests ont échoué.")
