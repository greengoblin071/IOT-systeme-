import streamlit as st
from firebase_config import init_firebase
from mqtt_handler import mqtt_handler
from pages.connexion import page_connexion
from pages.inscription import page_inscription
from pages.transaction import page_transaction
from pages.historique import page_historique

# ═══════════════════════════════════════════════════════════════════
#  INITIALISATION
# ═══════════════════════════════════════════════════════════════════

init_firebase()

if "mqtt_started" not in st.session_state:
    mqtt_handler.start()
    st.session_state.mqtt_started = True

# ═══════════════════════════════════════════════════════════════════
#  CONFIG STREAMLIT
# ═══════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Gestion Stock RFID",
    layout="wide",
    page_icon="📦"
)

# Init session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "uid_inscription" not in st.session_state:
    st.session_state.uid_inscription = ""
if "uid_transaction" not in st.session_state:
    st.session_state.uid_transaction = ""
if "scanning_1" not in st.session_state:
    st.session_state.scanning_1 = False
if "scanning_2" not in st.session_state:
    st.session_state.scanning_2 = False

# ═══════════════════════════════════════════════════════════════════
#  ROUTAGE
# ═══════════════════════════════════════════════════════════════════

if not st.session_state.logged_in:
    page_connexion()
else:
    # Sidebar
    st.sidebar.success(f"✓ {st.session_state.user_name}")
    st.sidebar.caption(f"Rôle: {st.session_state.user_role}")
    st.sidebar.divider()
    
    # Menu
    menu = st.sidebar.radio("📋 Menu", ["Inscription", "Transaction", "Historique"])
    
    # Navigation
    if menu == "Inscription":
        page_inscription()
    elif menu == "Transaction":
        page_transaction()
    elif menu == "Historique":
        page_historique()
    
    st.sidebar.divider()
    
    # Déconnexion
    if st.sidebar.button("🚪 Déconnexion", type="primary", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.uid_inscription = ""
        st.session_state.uid_transaction = ""
        st.rerun()
.0