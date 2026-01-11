import firebase_admin
from firebase_admin import credentials, db

def init_firebase():
    """Initialise Firebase une seule fois"""
    if not firebase_admin._apps:
        cred = credentials.Certificate("firebase-credentials.json")
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://gestion-ee-default-rtdb.europe-west1.firebasedatabase.app'
        })

def get_user_by_badge(uid):
    """Recherche utilisateur par badge"""
    users = db.reference("utilisateurs").get()
    if users:
        for user_id, user in users.items():
            if user.get("badge") == uid:
                return user
    return None

def get_worker_by_badge(uid):
    """Recherche ouvrier par badge"""
    ouvriers = db.reference("ouvriers").get()
    if ouvriers and uid in ouvriers:
        return ouvriers[uid]
    return None

def get_all_outils():
    """Récupère tous les outils"""
    return db.reference("outils").get() or {}

def get_all_transactions():
    """Récupère toutes les transactions"""
    return db.reference("transactions").get() or {}

def get_all_ouvriers():
    """Récupère tous les ouvriers"""
    return db.reference("ouvriers").get() or {}

def update_stock(outil_id, nouvelle_quantite):
    """Met à jour le stock d'un outil"""
    db.reference(f"outils/{outil_id}").update({"quantite": nouvelle_quantite})

def add_transaction(trans_data):
    """Ajoute une transaction"""
    return db.reference("transactions").push(trans_data)

def update_transaction(trans_id, data):
    """Met à jour une transaction"""
    db.reference(f"transactions/{trans_id}").update(data)

def add_ouvrier(uid, data):
    """Ajoute un ouvrier"""
    db.reference("ouvriers").child(uid).set(data)
