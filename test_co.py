import os
import csv
from fonctions import compte


print("--- Tests directs sur utilisateur.csv ---")

assert os.path.exists("utilisateur.csv")
print("Le fichier utilisateur.csv existe.")

utilisateurs_db = compte.charger_utilisateurs("utilisateur.csv")
assert isinstance(utilisateurs_db, dict)
print("Chargement de la base de données OK.")

print("Test d'écriture dans la DB...")

with open("utilisateur.csv", "r", encoding="utf-8") as f:
    lignes_initiales = f.readlines()

compte.utilisateurs = utilisateurs_db
compte.CSV_FILE = "utilisateur.csv"
compte.creation_compte('test_db@mail.com', 'user_test_db', 'MdpDb123!')

utilisateurs_verif = compte.charger_utilisateurs("utilisateur.csv")
assert 'user_test_db' in utilisateurs_verif
assert utilisateurs_verif['user_test_db']['email'] == 'test_db@mail.com'
print("Ajout dans utilisateur.csv OK.")

with open("utilisateur.csv", "w", encoding="utf-8") as f:
    f.writelines(lignes_initiales)

utilisateurs_finaux = compte.charger_utilisateurs("utilisateur.csv")
assert 'user_test_db' not in utilisateurs_finaux
print("Nettoyage du compte de test OK (DB originale intacte).")

print("Tous les tests sur la DB ont réussi !")