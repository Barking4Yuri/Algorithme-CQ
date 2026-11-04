import hashlib
import requests
import re

api = "https://api.pwnedpasswords.com/range/"

def hashing(mot_de_passe):
    return hashlib.sha1(mot_de_passe.encode()).hexdigest().upper()

def check_hibp(mot_de_passe):
    sha1 = hashing(mot_de_passe)
    prefix, suffix = sha1[:5], sha1[5:]
    r = requests.get(api + prefix)
    for ligne in r.text.splitlines():
        h, count = ligne.split(':')
        if h == suffix:
            return int(count)
    return 0

def suggestions(mot_de_passe):
    s = []
    if len(mot_de_passe) < 12:
        s.append("allonge-le (12+ caractères)")
    if not re.search(r'[a-z]', mot_de_passe) or not re.search(r'[A-Z]', mot_de_passe):
        s.append("mélange minuscules et majuscules")
    if not re.search(r'\d', mot_de_passe):
        s.append("ajoute un chiffre")
    if not re.search(r'[^a-zA-Z0-9]', mot_de_passe):
        s.append("ajoute un symbole")
    if re.search(r'(.)\1{2,}', mot_de_passe):
        s.append("évite les caractères répétés")
    if re.search(r'(0123|1234|2345|3456|4567|5678|6789|7890|qwerty|azerty)', mot_de_passe.lower()):
        s.append("évite les séquences prévisibles")
    if re.search(r'\d{4}', mot_de_passe):
        s.append("évite les années en clair")
    return s

mdp = "$$E$A00ekIEJ5''e'"

count = check_hibp(mdp)
if count:
    print(f"⚠️  Compromis dans {count:,} fuites")

for idee in suggestions(mdp):
    print(f"- {idee}")   
