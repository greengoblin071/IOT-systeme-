# 📐 ARCHITECTURE MODULAIRE FINALE
## Système de Gestion de Stock RFID - ESP32 + Streamlit + Firebase

**Version:** 2.0 Finale  
**Date:** Novembre 2025  
**Broker MQTT:** broker.hivemq.com  
**Framework:** Streamlit + PubSubClient + Firebase Realtime DB

---

## 📋 TABLE DES MATIÈRES

1. [Vue d'ensemble](#vue-densemble)
2. [Architecture système](#architecture-système)
3. [Structure modulaire](#structure-modulaire)
4. [Flux de communication](#flux-de-communication)
5. [Technologies](#technologies)
6. [Installation](#installation)
7. [Déploiement](#déploiement)

---

## 🎯 VUE D'ENSEMBLE

### Objectif
Système complet de gestion de stock utilisant:
- **Capteurs**: 2 lecteurs RFID sur ESP32
- **Communication**: MQTT via broker public
- **Interface**: Application web temps réel avec Streamlit
- **Stockage**: Firebase Realtime Database

### Caractéristiques
- ✅ Reconnaissance badges RFID
- ✅ Gestion authentification (magasinier/responsable)
- ✅ Inscription des ouvriers
- ✅ Sortie/retour outils avec suivi stock
- ✅ Historique complet des transactions
- ✅ Alertes stock faible
- ✅ Communication MQTT temps réel

---

## 🏗️ ARCHITECTURE SYSTÈME

```
┌─────────────────────────────────────────────────────────────┐
│                    UTILISATEURS                             │
│              (Magasiniers, Responsables, Ouvriers)          │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
   ┌─────────┐  ┌──────────────┐  ┌─────────┐
   │ RFID #1 │  │ RFID #2      │  │ Interface│
   │ Lecteur │  │ Lecteur      │  │ Web      │
   │ Badges  │  │ Transactions │  │Streamlit │
   └────┬────┘  └──────┬───────┘  └─────┬───┘
        │               │                │
        └───────────────┼────────────────┘
                        │
                  ┌─────▼──────┐
                  │    ESP32    │  (Capteur Intelligent)
                  │ 2x SPI RFID │
                  │ WiFi + MQTT │
                  └─────┬──────┘
                        │
                 ┌──────▼──────┐
                 │    MQTT     │
                 │ broker.    │
                 │hivemq.com  │
                 └──────┬──────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
   ┌─────────┐  ┌─────────────┐  ┌──────────┐
   │ Topics  │  │ Callbacks   │  │Interface │
   │ MQTT    │  │ Python      │  │Récéption │
   └─────────┘  └─────────────┘  └──────────┘
                        │
                 ┌──────▼─────────┐
                 │   Firebase     │
                 │ Realtime DB    │
                 │ - utilisateurs │
                 │ - ouvriers     │
                 │ - outils       │
                 │ - transactions │
                 └────────────────┘
```

---

## 📦 STRUCTURE MODULAIRE

### Arborescence du Projet

```
gestion_stock/
│
├── 📄 main.py                          # Point d'entrée principal
│   ├─ Initialisation Streamlit
│   ├─ Config pages
│   ├─ Routage navigation
│   └─ Session state management
│
├── 📄 mqtt_handler.py                  # Module MQTT
│   ├─ Classe OptimizedMQTTHandler
│   ├─ Connection/Disconnection
│   ├─ Subscribe topics
│   ├─ Publish messages
│   └─ Instance globale mqtt_handler
│
├── 📄 firebase_config.py               # Module Firebase
│   ├─ init_firebase()
│   ├─ get_user_by_badge()
│   ├─ get_worker_by_badge()
│   ├─ get_all_outils()
│   ├─ get_all_transactions()
│   ├─ add_transaction()
│   ├─ update_stock()
│   └─ Fonctions utilitaires DB
│
├── 📁 pages/
│   ├── __init__.py                     # Fichier vide (import Python)
│   │
│   ├── connexion.py                    # Page 1 : Authentification
│   │   ├─ check_mqtt_updates()
│   │   ├─ page_connexion()
│   │   ├─ Vérification Firebase
│   │   └─ Gestion roles (magasinier/responsable)
│   │
│   ├── inscription.py                  # Page 2 : Enregistrement ouvriers
│   │   ├─ Scan badge ouvrier
│   │   ├─ Vérification doublon
│   │   ├─ Enregistrement Firebase
│   │   └─ Affichage liste ouvriers
│   │
│   ├── transaction.py                  # Page 3 : Gestion outils
│   │   ├─ sortie_outil()
│   │   │  ├─ Scan badge ouvrier
│   │   │  ├─ Sélection outil
│   │   │  ├─ Validation sortie
│   │   │  └─ Mise à jour stock
│   │   │
│   │   └─ retour_outil()
│   │      ├─ Affichage outils en cours
│   │      ├─ Validation retour
│   │      └─ Restauration stock
│   │
│   └── historique.py                   # Page 4 : Rapports
│       ├─ Statistiques globales
│       ├─ Historique complet
│       ├─ Filtres et export CSV
│       └─ Alertes stock faible
│
├── 📄 firebase-credentials.json        # Clé Firebase (NOT IN GIT!)
│
└── 📄 requirements.txt                 # Dépendances Python
    ├─ streamlit==1.29.0
    ├─ firebase-admin==6.3.0
    ├─ paho-mqtt==1.6.1
    └─ pandas==2.1.3
```

---

## 🔄 FLUX DE COMMUNICATION

### Flux 1 : Connexion Utilisateur

```
1. Utilisateur → Interface
   "Cliquer sur 'Scanner mon badge'"
   
2. Interface → MQTT
   Publish: stock/cmd/scan1
   Message: "START"
   
3. MQTT → ESP32
   Topic: stock/cmd/scan1
   
4. ESP32 → RFID
   Activer lecteur RFID #1
   Attendre badge
   
5. Badge → ESP32
   Lecture UID
   
6. ESP32 → MQTT
   Publish: stock/rfid/inscription
   Message: {"uid":"A1B2C3D4"}
   
7. MQTT → Interface
   Callback: on_message()
   
8. Interface → Firebase
   Vérifier utilisateur dans "utilisateurs"
   Vérifier rôle (magasinier/responsable)
   
9. Firebase → Interface
   Retour utilisateur avec rôle
   
10. Interface → Session
    Définir logged_in = True
    Stocker user_name, user_role
```

### Flux 2 : Inscription Ouvrier

```
1. Magasinier → Interface (Menu "Inscription")
   Cliquer "Scanner badge"
   
2. Interface → MQTT
   Publish: stock/cmd/scan1
   
3. ESP32 → RFID → Badge → UID
   
4. UID → MQTT → Interface
   
5. Interface → Firebase
   Vérifier si UID existe dans "ouvriers"
   
6. Si nouveau:
   Interface demande nom
   
7. Nom + UID → Firebase
   add_ouvrier(uid, {nom, date_inscription, actif})
```

### Flux 3 : Sortie Outil

```
1. Magasinier → Interface (Menu "Transaction" Tab "Sortie")
   Cliquer "Scanner badge ouvrier"
   
2. Interface → MQTT → ESP32 → RFID
   Lecture UID ouvrier
   
3. UID ouvrier → MQTT → Interface
   
4. Interface → Firebase
   get_worker_by_badge(uid)
   
5. Si ouvrier existe:
   Interface affiche: Ouvrier identifié
   Interface charge: get_all_outils()
   Affiche liste outils en stock
   
6. Magasinier sélectionne outil + quantité
   
7. Clic "Valider sortie":
   - Créer transaction dans Firebase
   - update_stock(outil_id, quantite - sortie)
   
8. Firebase met à jour:
   transactions/ : nouvelle transaction
   outils/outil_id : nouveau stock
```

### Flux 4 : Retour Outil

```
1. Magasinier → Interface (Tab "Retour")
   Affichage liste outils "en_cours"
   
2. Clic "Retour":
   - update_transaction(trans_id, {statut: "retourne"})
   - update_stock(outil_id, quantite + retour)
   
3. Firebase met à jour
   Stock restauré
```

---

## 🛠️ TECHNOLOGIES

### ESP32
```
Microcontrôleur: ESP32-WROOM-32
Connectivité: WiFi 802.11b/g/n (2.4 GHz)
Protocole: MQTT via PubSubClient
Lecteurs RFID: 2x MFRC522 (SPI)
Alimentation: 5V / 1A
```

### Capteurs RFID
```
Type: MFRC522
Interface: SPI
Fréquence: 13.56 MHz
Portée: ~5 cm
Énergie: 3.3V
```

### Broker MQTT
```
Service: HiveMQ Public Broker
URL: broker.hivemq.com
Port: 1883
QoS: 1
Sécurité: Public (pour démo)
```

### Backend
```
Database: Firebase Realtime DB
Auth: JSON credentials file
Structure: No-SQL (collections)
Accès: Firebase Admin SDK
```

### Frontend
```
Framework: Streamlit
Langue: Python 3.7+
Communication: MQTT via paho-mqtt
Visualisation: Pandas DataFrames
```

---

## 📊 STRUCTURE FIREBASE

```
gestion-ee-default-rtdb
│
├── utilisateurs/
│   ├── user1
│   │   ├─ nom: "Ahmed"
│   │   ├─ email: "ahmed@example.com"
│   │   ├─ badge: "A1B2C3D4"
│   │   └─ role: "magasinier"
│   │
│   └── user2
│       ├─ nom: "Fatima"
│       ├─ email: "fatima@example.com"
│       ├─ badge: "E5F6G7H8"
│       └─ role: "responsable"
│
├── ouvriers/
│   ├── A1B2C3D4
│   │   ├─ nom: "Mohammed"
│   │   ├─ date_inscription: "2025-11-20T10:30:00"
│   │   └─ actif: true
│   │
│   └── E5F6G7H8
│       ├─ nom: "Fatima"
│       ├─ date_inscription: "2025-11-20T11:00:00"
│       └─ actif: true
│
├── outils/
│   ├── OUTIL001
│   │   ├─ nom: "Clé à molette"
│   │   ├─ type: "non_consomable"
│   │   ├─ reference: "REF-001"
│   │   ├─ quantite: 5
│   │   ├─ seuil_alerte: 2
│   │   └─ emplacement: "Armoire A"
│   │
│   └── OUTIL002
│       ├─ nom: "Tournevis"
│       ├─ type: "consommable"
│       ├─ reference: "REF-002"
│       ├─ quantite: 12
│       └─ seuil_alerte: 5
│
└── transactions/
    ├── trans_001
    │   ├─ id_outil: "OUTIL001"
    │   ├─ nom_outil: "Clé à molette"
    │   ├─ uid_ouvrier: "A1B2C3D4"
    │   ├─ nom_ouvrier: "Mohammed"
    │   ├─ quantite: 1
    │   ├─ date_sortie: "2025-11-20T14:30:00"
    │   ├─ date_retour: "2025-11-20T16:00:00"
    │   ├─ statut: "retourne"
    │   └─ enregistre_par: "Ahmed"
    │
    └── trans_002
        ├─ id_outil: "OUTIL002"
        ├─ nom_outil: "Tournevis"
        ├─ uid_ouvrier: "E5F6G7H8"
        ├─ nom_ouvrier: "Fatima"
        ├─ quantite: 2
        ├─ date_sortie: "2025-11-20T15:00:00"
        ├─ statut: "consomme"
        └─ enregistre_par: "Ahmed"
```

---

## 📡 TOPICS MQTT

### Topics Publiés par ESP32

```
Topic: stock/rfid/inscription
Format: {"uid":"A1B2C3D4"}
Description: UID badge lu par RFID #1 (connexion/inscription)

Topic: stock/rfid/transaction
Format: {"uid":"E5F6G7H8"}
Description: UID badge lu par RFID #2 (transactions outils)

Topic: stock/test
Format: {"test":"ESP32 Online"}
Description: Message de test connexion
```

### Topics Reçus par ESP32

```
Topic: stock/cmd/scan1
Format: "START"
Description: Commande au RFID #1 pour démarrer scan

Topic: stock/cmd/scan2
Format: "START"
Description: Commande au RFID #2 pour démarrer scan
```

---

## ⚙️ INSTALLATION

### Prérequis
- Python 3.7+
- Arduino IDE pour ESP32
- Compte Firebase
- Connexion WiFi 2.4 GHz

### Étape 1 : Configuration Firebase

```
1. Créer projet sur console.firebase.google.com
2. Activer Realtime Database
3. Télécharger JSON credentials
4. Placer dans: gestion_stock/firebase-credentials.json
```

### Étape 2 : Installation Python

```bash
# Créer virtualenv
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Installer dépendances
pip install -r requirements.txt
```

### Étape 3 : Configuration ESP32

```cpp
// Fichier: sketch.ino
// Lignes à modifier:

const char* WIFI_SSID = "VOTRE_SSID";        // Ligne 18
const char* WIFI_PASSWORD = "VOTRE_MDP";     // Ligne 19
const char* MQTT_SERVER = "broker.hivemq.com"; // Ligne 22
```

### Étape 4 : Téléversement ESP32

```
1. Arduino IDE → Sélectionner carte ESP32
2. Configurer:
   - Board: ESP32 Dev Module
   - Upload Speed: 921600
   - Port: COMx ou /dev/ttyUSBx
3. Vérifier → Téléverser
4. Ouvrir Moniteur Série (115200 baud)
```

### Étape 5 : Lancement Application

```bash
# Depuis le dossier gestion_stock/
streamlit run main.py

# Application accessible sur:
# http://localhost:8501
```

---

## 🚀 DÉPLOIEMENT

### Déploiement Local (Développement)

```bash
# Terminal 1: Interface Streamlit
cd gestion_stock/
streamlit run main.py

# Terminal 2: Monitor MQTT (optionnel)
python test_mqtt.py

# ESP32: Code téléversé et en exécution
```

### Déploiement Cloud (Production)

#### Option 1 : Streamlit Cloud

```
1. Pusher code sur GitHub
2. Aller sur share.streamlit.io
3. Connecter repo GitHub
4. Déployer branch
```

#### Option 2 : Heroku

```bash
# Créer Procfile
web: streamlit run --server.port=$PORT main.py

# Deploy
heroku create app-name
git push heroku main
```

#### Option 3 : VPS Personnel

```bash
# Installer Python + Streamlit sur serveur
sudo apt-get update
sudo apt-get install python3-pip

# Clone repo
git clone repo-url
cd gestion_stock

# Installer dépendances
pip install -r requirements.txt

# Démarrer avec PM2 ou systemd
pm2 start "streamlit run main.py"
```

---

## 📊 MÉTRIQUES & MONITORING

### Métriques Suivies

```
- Nombre de messages MQTT reçus
- Latence réseau (ms)
- Nombre de transactions par jour
- Outils alertés (stock faible)
- Erreurs de connexion
- Uptime système
```

### Logs Générés

```
ESP32:
- [WiFi] Connexion/Déconnexion
- [MQTT] Messages envoyés/reçus
- [SCAN] Activation/Timeout
- [ERROR] Erreurs système

Streamlit:
- [MQTT] État connexion
- [FIREBASE] Opérations DB
- [PAGE] Navigation utilisateur
```

---

## ✅ CHECKLIST FINAL

### ESP32
- [ ] WiFi connecté
- [ ] MQTT connecté
- [ ] 2x RFID initialisés
- [ ] LED/Buzzer fonctionnels
- [ ] Moniteur série affiche messages

### Interface
- [ ] MQTT connecté
- [ ] Firebase connecté
- [ ] Pages chargent correctement
- [ ] Session state fonctionne

### Firebase
- [ ] Collections créées
- [ ] Données de test présentes
- [ ] Credentials configurées

### Communication
- [ ] Topics MQTT actifs
- [ ] Messages reçus/envoyés
- [ ] Test badge réussi

---

## 🔐 SÉCURITÉ

### Recommandations Production

```
1. Utiliser broker MQTT privé (sécurisé TLS)
2. Authentification Firebase robuste
3. Mots de passe WiFi forts
4. Certificats SSL pour connexions
5. Chiffrement données sensibles
6. Audit et logs d'accès
7. Limiter accès API Firebase
8. Mettre à jour bibliothèques régulièrement
```

---

## 📚 RÉFÉRENCES

### Documentation
- Streamlit: https://docs.streamlit.io
- Firebase: https://firebase.google.com/docs
- MQTT: https://mqtt.org
- ESP32: https://docs.espressif.com

### Librairies
- paho-mqtt: https://github.com/eclipse/paho.mqtt.python
- firebase-admin: https://github.com/firebase/firebase-admin-python
- streamlit: https://github.com/streamlit/streamlit

---

## 📝 VERSION FINALE

**Version:** 2.0  
**Date:** Novembre 2025  
**Status:** Production Ready  
**Support:** Available

**Modifications Finales:**
- ✅ ESP32 envoie UID uniquement
- ✅ Interface gère toute la logique
- ✅ Broker MQTT distant (HiveMQ)
- ✅ Architecture modulaire complète
- ✅ Firebase Realtime DB intégré
- ✅ Authentification et rôles
- ✅ Suivi stock et transactions
- ✅ Historique et rapports
- ✅ Gestion erreurs robuste
- ✅ Logs de debug complets

---

**FIN DU DOCUMENT**