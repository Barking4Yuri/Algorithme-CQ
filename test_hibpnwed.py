from haveibeenpwned import check_hibp, suggestions

def test_hibpwned():
    count = check_hibp("password123")
    assert count > 0, f"'password123' devrait être compromis mais count = {count}"
    print(f"Reussie hibpwned compromis ({count:,} fuites)")

    count2 = check_hibp("$$E$A00ekIEJ5''e'")
    assert count2 == 0, f"mdp aléatoire ne devrait pas être compromis"
    print("Reussie hibpwned aléatoire (non compromis)")

    s = suggestions("abc")
    assert len(s) > 0, "Doit retourner des suggestions"
    print(f"Reussie suggestions ({len(s)} pour 'abc')")   

if __name__ == '__main__':
    test_hibpwned()
