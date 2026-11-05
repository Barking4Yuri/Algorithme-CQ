import sqlite3
import bcrypt

DB_FILE = 'utilisateurs.db'

utilisateurs = {}


def get_conn():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row

    conn.execute("""
        CREATE TABLE IF NOT EXISTS utilisateurs (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL DEFAULT 'utilisateur',
            email TEXT NOT NULL UNIQUE,
            pseudo TEXT NOT NULL UNIQUE,
            motdepasse TEXT NOT NULL
        )
    """)

    conn.commit()
    return conn


def charger_utilisateurs():
    utilisateurs.clear()

    conn = get_conn()

    rows = conn.execute(
        "SELECT * FROM utilisateurs"
    ).fetchall()

    for ligne in rows:
        utilisateurs[ligne['pseudo']] = dict(ligne)

    conn.close()
    return utilisateurs


def check_login(pseudo, mot_de_passe, utilisateurs=None):
    conn = get_conn()

    try:
        user = conn.execute(
            "SELECT motdepasse FROM utilisateurs WHERE pseudo = ?",
            (pseudo,)
        ).fetchone()

        if user is None:
            return False

        hash_stocke = user['motdepasse'].encode('utf-8')

        return bcrypt.checkpw(
            mot_de_passe.encode('utf-8'),
            hash_stocke
        )
    finally:
        conn.close()


def creation_compte(email, pseudo, mot_de_passe):
    if not email or not pseudo or not mot_de_passe:
        return False

    conn = get_conn()

    try:
        hash_mdp = bcrypt.hashpw(
            mot_de_passe.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')

        conn.execute("""
            INSERT INTO utilisateurs
            (role, email, pseudo, motdepasse)
            VALUES (?, ?, ?, ?)
        """, (
            'utilisateur',
            email,
            pseudo,
            hash_mdp
        ))

        conn.commit()
        charger_utilisateurs()

        return True

    except sqlite3.IntegrityError:
        return False

    finally:
        conn.close()


def get_utilisateur(pseudo):
    conn = get_conn()

    try:
        user = conn.execute(
            "SELECT * FROM utilisateurs WHERE pseudo = ?",
            (pseudo,)
        ).fetchone()

        return dict(user) if user else None

    finally:
        conn.close()


def changer_role(pseudo, nouveau_role):
    conn = get_conn()

    try:
        cursor = conn.execute(
            "UPDATE utilisateurs SET role = ? WHERE pseudo = ?",
            (nouveau_role, pseudo)
        )

        conn.commit()

        if cursor.rowcount > 0:
            charger_utilisateurs()
            return True

        return False

    finally:
        conn.close()