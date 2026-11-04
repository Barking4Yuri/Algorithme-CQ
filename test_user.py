import csv
import bcrypt

CSV_FILE = 'utilisateur.csv'
DELIMITER = ';'
HEADERS = ['Id', 'role', 'email', 'pseudo', 'motdepasse']

def charger_utilisateurs(chemin_csv):
    utilisateurs = {}
    with open(chemin_csv, newline='', encoding='utf-8') as f:
        lecteur = csv.DictReader(f, delimiter=';')
        for ligne in lecteur:
            utilisateurs[ligne['pseudo']] = ligne
    return utilisateurs

def login(pseudo, mot_de_passe, utilisateurs):
    user = utilisateurs.get(pseudo)
    if user is None:
        return False
    hash_stocke = user['motdepasse'].encode('utf-8')
    return bcrypt.checkpw(mot_de_passe.encode('utf-8'), hash_stocke)

def creation_compte(email,pseudo,mot_de_passe):
    role = "utilisateur"

    ids = [int(u['Id']) for u in utilisateurs.values()]
    nouvel_id = max(ids) + 1 if ids else 1

    hash_mdp = bcrypt.hashpw(mot_de_passe.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    nouvelle_ligne = {
        'Id': nouvel_id,
        'role': role,
        'email': email,
        'pseudo': pseudo,
        'motdepasse': hash_mdp
    }

    with open(CSV_FILE, 'a', newline='\n', encoding='utf-8') as f:
        ecrivain = csv.DictWriter(f, delimiter=';', fieldnames=['Id', 'role', 'email', 'pseudo', 'motdepasse'])
        ecrivain.writerow(nouvelle_ligne)

    utilisateurs[pseudo] = nouvelle_ligne
    print("Compte créé.")


if __name__ == "__main__":
    
    utilisateurs = charger_utilisateurs("utilisateur.csv")
    pseudo = input("Pseudo : ")
    mdp = input("Mot de passe : ")

    if login(pseudo, mdp, utilisateurs):
        print("Connexion réussie.")
    else:
        print("Pseudo ou mot de passe incorrect.")

        