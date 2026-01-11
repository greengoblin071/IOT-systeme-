# init_firebase.py
import firebase_admin
from firebase_admin import credentials, db

# Initialisation Firebase
cred = credentials.Certificate("firebase-credentials.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://gestion-ee-default-rtdb.europe-west1.firebasedatabase.app'
})

# Données à insérer
data = {
    "utilisateurs": {
        "UID_MAG_001": {
            "nom": "Ahmed Benali",
            "badge": "23DE701A",
            "email": "ahmed.benali@entreprise.com",
            "role": "magasinier",
            "date_creation": "2025-11-01T10:00:00"
        },
        "UID_RESP_001": {
            "nom": "Fatima Zahra",
            "badge": "35D9FD03",
            "email": "fatima.zahra@entreprise.com",
            "role": "responsable",
            "date_creation": "2025-11-01T10:00:00"
        }
    },
    
    "ouvriers": {
        "F1E30004": {
            "nom": "Hassan Idrissi",
            "date_inscription": "2025-11-03T09:15:00",
            "actif": True
        },
        "79C20004": {
            "nom": "Youssef Tazi",
            "date_inscription": "2025-11-03T10:20:00",
            "actif": True
        },
        "46600104": {
            "nom": "Rachid Bennani",
            "date_inscription": "2025-11-04T08:45:00",
            "actif": True
        },
        "87FF0004": {
            "nom": "Karim Ouazzani",
            "date_inscription": "2025-11-05T11:00:00",
            "actif": True
        }
    },
    
    "outils": {
        "OUTIL_001": {
            "nom": "Tournevis cruciforme",
            "type": "non_consomable",
            "quantite": 15,
            "seuil_alerte": 5,
            "reference": "TRV-CR-001",
            "emplacement": "Armoire A - Étagère 2"
        },
        "OUTIL_002": {
            "nom": "Perceuse sans fil 18V",
            "type": "non_consomable",
            "quantite": 8,
            "seuil_alerte": 3,
            "reference": "PER-SF-002",
            "emplacement": "Armoire B - Étagère 1"
        },
        "OUTIL_003": {
            "nom": "Clé à molette 300mm",
            "type": "non_consomable",
            "quantite": 12,
            "seuil_alerte": 4,
            "reference": "CLE-MO-003",
            "emplacement": "Armoire A - Étagère 3"
        },
        "OUTIL_004": {
            "nom": "Marteau rivoir 500g",
            "type": "non_consomable",
            "quantite": 10,
            "seuil_alerte": 3,
            "reference": "MAR-RV-004",
            "emplacement": "Armoire C - Étagère 1"
        },
        "OUTIL_005": {
            "nom": "Pince multiprise 250mm",
            "type": "non_consomable",
            "quantite": 20,
            "seuil_alerte": 6,
            "reference": "PIN-MP-005",
            "emplacement": "Armoire A - Étagère 1"
        },
        "OUTIL_006": {
            "nom": "Vis M6x20 (boîte de 100)",
            "type": "consommable",
            "quantite": 50,
            "seuil_alerte": 10,
            "reference": "VIS-M6-006",
            "emplacement": "Stock consommables - Bac 12"
        },
        "OUTIL_007": {
            "nom": "Écrous M8 (boîte de 100)",
            "type": "consommable",
            "quantite": 35,
            "seuil_alerte": 8,
            "reference": "ECR-M8-007",
            "emplacement": "Stock consommables - Bac 13"
        },
        "OUTIL_008": {
            "nom": "Huile de coupe (1L)",
            "type": "consommable",
            "quantite": 8,
            "seuil_alerte": 5,
            "reference": "HUI-CP-008",
            "emplacement": "Étagère liquides - Zone A"
        },
        "OUTIL_009": {
            "nom": "Rondelles M10 (boîte de 50)",
            "type": "consommable",
            "quantite": 25,
            "seuil_alerte": 6,
            "reference": "RON-M10-009",
            "emplacement": "Stock consommables - Bac 14"
        },
        "OUTIL_010": {
            "nom": "Meuleuse d'angle 125mm",
            "type": "non_consomable",
            "quantite": 6,
            "seuil_alerte": 2,
            "reference": "MEU-AN-010",
            "emplacement": "Armoire B - Étagère 2"
        }
    },
    
    "transactions": {}
}

# Insertion dans Firebase
ref = db.reference()
ref.set(data)
print("✅ Base de données initialisée avec succès!")
print("\n📊 Résumé:")
print(f"   - 2 utilisateurs (1 magasinier, 1 responsable)")
print(f"   - 4 ouvriers")
print(f"   - 10 outils (6 non-consommables, 4 consommables)")
