import os
import streamlit as st
import PyPDF2
import json
import base64
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import pandas as pd
from groq import Groq
from PIL import Image
import io
import urllib.parse
import streamlit.components.v1 as components

VAULT_FILE = ".vektor_vault.json"
HISTORY_FILE = ".vektor_history.json"
NOTEPAD_FILE = ".vektor_notepad.json"
METRICS_FILE = ".vektor_admin_metrics.json"
PINS_FILE = ".vektor_activation_pins.json"

# ==========================================
# AUTHENTICATION & STORAGE UTILITIES
# ==========================================
def encode_cred(text):
    return base64.b64encode(text.encode()).decode()

def load_vault():
    if os.path.exists(VAULT_FILE):
        try:
            with open(VAULT_FILE, "r") as f: return json.load(f)
        except: return {}
    return {}

def save_to_vault(username, password):
    vault = load_vault()
    vault[encode_cred(username)] = encode_cred(password)
    with open(VAULT_FILE, "w") as f: json.dump(vault, f)
    track_user_activity(username, action="register")

def load_history(username):
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                full_history = json.load(f)
                return full_history.get(encode_cred(username), {})
        except: return {}
    return {}

def save_history(username, key, data):
    full_history = {}
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f: full_history = json.load(f)
        except: pass
    user_key = encode_cred(username)
    if user_key not in full_history: full_history[user_key] = {}
    full_history[user_key][key] = data
    with open(HISTORY_FILE, "w") as f: json.dump(full_history, f)

def load_notepad(username):
    if os.path.exists(NOTEPAD_FILE):
        try:
            with open(NOTEPAD_FILE, "r") as f:
                data = json.load(f)
                user_data = data.get(encode_cred(username), {"current": "", "history": []})
                if isinstance(user_data, str):
                    return {"current": user_data, "history": []}
                return user_data
        except: return {"current": "", "history": []}
    return {"current": "", "history": []}

def save_notepad(username, content, history_list):
    notes = {}
    if os.path.exists(NOTEPAD_FILE):
        try:
            with open(NOTEPAD_FILE, "r") as f: notes = json.load(f)
        except: pass
    notes[encode_cred(username)] = {"current": content, "history": history_list}
    with open(NOTEPAD_FILE, "w") as f: json.dump(notes, f)

# ==========================================
# BACKGROUND USER ACTIVITY METRICS AGENT
# ==========================================
def load_admin_metrics():
    if os.path.exists(METRICS_FILE):
        try:
            with open(METRICS_FILE, "r") as f: return json.load(f)
        except: return {}
    return {}

def save_admin_metrics(data):
    with open(METRICS_FILE, "w") as f: json.dump(data, f)

def load_pins():
    if os.path.exists(PINS_FILE):
        try:
            with open(PINS_FILE, "r") as f: return json.load(f)
        except: return {}
    return {}

def save_pins(data):
    with open(PINS_FILE, "w") as f: json.dump(data, f)

def track_user_activity(username, action="login"):
    metrics = load_admin_metrics()
    u_key = encode_cred(username)
    now_str = datetime.now(ZoneInfo('Africa/Lagos')).strftime("%Y-%m-%d %H:%M:%S")
    
    if u_key not in metrics:
        metrics[u_key] = {
            "username": username,
            "registered_at": now_str,
            "last_active": now_str,
            "status": "Active",
            "payment_status": "Unpaid",
            "license_expiry": (datetime.now(ZoneInfo('Africa/Lagos')) + timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
        }
    else:
        metrics[u_key]["last_active"] = now_str
        if action == "login" or action == "heartbeat":
            metrics[u_key]["status"] = "Active"
            
    save_admin_metrics(metrics)

# ==========================================
# MULTILINGUAL DICTIONARY MATRIX WITH ABOUT
# ==========================================
LANG_DATA = {
    "English": {
        "title": "⚡ VEKTOR.AI // Multi-Agent Node Matrix", 
        "gate_title": "SECURE LOCAL SHELL — PERSONAL WORKSPACE PORTAL",
        "signin": "🔐 Sign In", "register": "🛠️ Register New Workspace", "username": "Security ID Username",
        "password": "Access Key Password", "btn_auth": "Authorize Access", "btn_reg": "Provision Hidden Profile Space",
        "nav_lbl": "Select Operation Target Engine:", "clear_cache": "Clear Cache Data 🗑️", "logout": "Terminate Session 🔓",
        "search_title": "🌐 Global Commodity Cost & Currency Conversion Oracle", "search_btn": "🔍 Look Up Commodity Cost",
        "search_ph": "e.g., 1 bag of cement, barrel of crude oil, price of rice per ton", "curr_lbl": "Target Currency Symbol:",
        "upload_lbl": "Upload Corporate Knowledge Assets (PDF)", "orac_res": "🌐 Pricing Oracle Result:",
        "comp_panel": "📊 Company Progress Panel", "oracle_chat": "💬 Context Oracle Chat", "exec_brief": "📝 Executive Briefing Engine",
        "composer": "✉️ Contextual Draft Composer", "extractor": "📊 Structural Data Extractor", "cross_file": "🔍 Cross-File Intelligence",
        "tracker": "📅 Task & Milestone Tracker", "sandbox": "💡 Brainstorm Sandbox", "predictor": "💸 Resource Predictor",
        "indexer": "🗂️ Knowledge Base Indexer", "runway_plan": "🛡️ Runway & Reinvestment Planner",
        "about_panel": "ℹ️ About Application",
        "run_diag": "⚡ Run System Diagnostic Engine", "error_ingest": "🚨 Ingestion Missing: Drop asset documents into the workspace first.",
        "calc_btn": "📊 Calculate Parameters", "success_ac": "⚡ Data Accelerator updated successfully!",
        "save_fn": "Save As (Filename):", "dl_lbl": "📥 Save As (Download File)", "metrics_lbl": "Enter comma-separated metric values:"
    },
    "Français": {
        "title": "⚡ VEKTOR.AI // Matrice de Nœuds Multi-Agents", 
        "gate_title": "SHELL LOCAL SÉCURISÉ — PORTAIL D'ESPACE PERSONNEL",
        "signin": "🔐 Se Connecter", "register": "🛠️ Enregistrer un Espace", "username": "Nom d'utilisateur de Sécurité",
        "password": "Mot de Passe d'Accès", "btn_auth": "Autoriser l'Accès", "btn_reg": "Créer un Espace Masqué",
        "nav_lbl": "Sélectionner le Moteur Opérationnel:", "clear_cache": "Effacer le Cache Data 🗑️", "logout": "Terminer la Session 🔓",
        "search_title": "🌐 Oracle des Coûts des Matières Premières & Conversion", "search_btn": "🔍 Chercher le Coût",
        "search_ph": "ex. 1 sac de ciment, baril de pétrole brut, prix du riz au tonne", "curr_lbl": "Symbole Devise Cible:",
        "upload_lbl": "Charger des Documents de Connaissance d'Entreprise (PDF)", "orac_res": "🌐 Résultat de l'Oracle de Prix:",
        "comp_panel": "📊 Panneau de Progrès d'Entreprise", "oracle_chat": "💬 Chat Contexte Oracle", "exec_brief": "📝 Moteur de Briefing Exécutif",
        "composer": "✉️ Compositeur de Projet Contextuel", "extractor": "📊 Extracteur de Données Structurelles", "cross_file": "🔍 Intelligence Multi-Fichiers",
        "tracker": "📅 Suivi des Tâches & Jalons", "sandbox": "💡 Bac à Sable Remue-Méninges", "predictor": "💸 Prédiction de Ressources",
        "indexer": "🗂️ Indexeur de Base de Connaissances", "runway_plan": "🛡️ Planificateur de Trésorerie & Réinvestissement",
        "about_panel": "ℹ️ À Propos de l'App",
        "run_diag": "⚡ Lancer le Diagnostic Système", "error_ingest": "🚨 Ingestion Manquante: Déposez les documents d'actifs d'abord.",
        "calc_btn": "📊 Calculer les Paramètres", "success_ac": "⚡ Accélérateur de données mis à jour!",
        "save_fn": "Enregistrer sous (Nom du fichier):", "dl_lbl": "📥 Télécharger le fichier", "metrics_lbl": "Entrez les valeurs séparées par des virgules:"
    }
}

st.set_page_config(
    page_title="Vektor AI",
    page_icon="playstore.png"
)

# Force Safari to use your custom icon on the iPhone Home Screen
components.html(
    """
    <script>
        const link = window.parent.document.createElement('link');
        link.rel = 'apple-touch-icon';
        link.href = 'https://raw.githubusercontent.com/Talabi-David-Adeoluwa2010/my-Vector-AI-app/main/playstore.png';
        window.parent.document.head.appendChild(link);
    </script>
    """,
    height=0,
)

# Initialize Session variables
if "loading_complete" not in st.session_state: st.session_state.loading_complete = False
if "authenticated" not in st.session_state: st.session_state.authenticated = False
if "current_user" not in st.session_state: st.session_state.current_user = ""
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "active_view" not in st.session_state: st.session_state.active_view = "HOME"

# ==========================================================
# 1. BEAUTIFUL HIGH-TECH LOADING SCREEN / CUSTOM SPLASH PAGE
# ==========================================================
if not st.session_state.loading_complete:
    components.html(
        """
        <div id="loading-screen">
            <div class="loading-content">
                <img src="https://raw.githubusercontent.com/Talabi-David-Adeoluwa2010/my-Vector-AI-app/main/playstore.png" alt="Vektor AI Logo" class="vektor-logo">
                
                <div class="app-intro">
                    <h2>Welcome to Vektor AI</h2>
                    <p>A high-performance multi-agent workspace matrix engineered to simplify complex developer workflows and asset telemetry.</p>
                    <div class="navigation-tips">
                        <h3>Quick Navigation Guide:</h3>
                        <ul>
                            <li>Use the persistent sidebar on the left to navigate dashboard view arrays.</li>
                            <li>Access deep architecture details through the new sidebar 'About' button.</li>
                        </ul>
                    </div>
                </div>

                <div class="progress-container">
                    <div id="progress-bar"></div>
                </div>
                <div id="progress-text">0%</div>

                <div class="founder-credits">
                    Founder / Produced by - Talabi David Adeoluwa
                </div>
            </div>
        </div>

        <style>
            #loading-screen {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-color: #05070f;
                color: #ffffff;
                z-index: 99999;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            .loading-content {
                text-align: center;
                width: 90%;
                max-width: 480px;
                position: relative;
                height: 90vh;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
            }
            .vektor-logo {
                width: 110px;
                height: 110px;
                object-fit: contain;
                margin-bottom: 25px;
                border-radius: 20px;
                box-shadow: 0 0 25px rgba(0, 242, 254, 0.25);
                animation: pulse 2s infinite ease-in-out;
            }
            .app-intro h2 {
                color: #00f2fe;
                margin-bottom: 12px;
                font-size: 1.7rem;
                letter-spacing: 0.5px;
            }
            .app-intro p {
                font-size: 0.95rem;
                color: #94a3b8;
                line-height: 1.5;
                margin-bottom: 15px;
            }
            .navigation-tips {
                background: rgba(255, 255, 255, 0.03);
                border: 1px solid #1f293d;
                padding: 15px;
                border-radius: 12px;
                margin: 15px 0;
                text-align: left;
            }
            .navigation-tips h3 {
                font-size: 0.9rem;
                color: #4facfe;
                margin-top: 0;
                margin-bottom: 6px;
            }
            .navigation-tips ul {
                margin: 0;
                padding-left: 18px;
                font-size: 0.85rem;
                color: #cbd5e1;
            }
            .navigation-tips li { margin-bottom: 5px; }
            .progress-container {
                width: 100%;
                background-color: #121626;
                border-radius: 10px;
                height: 8px;
                overflow: hidden;
                margin-top: 20px;
                border: 1px solid #1f293d;
            }
            #progress-bar {
                width: 0%;
                height: 100%;
                background: linear-gradient(90deg, #00f2fe, #4facfe);
            }
            #progress-text {
                margin-top: 8px;
                font-size: 0.85rem;
                color: #64748b;
            }
            .founder-credits {
                position: absolute;
                bottom: 20px;
                left: 10px;
                font-size: 0.8rem;
                color: #64748b;
                font-weight: 600;
                letter-spacing: 0.3px;
            }
            @keyframes pulse {
                0% { transform: scale(1); opacity: 0.9; }
                50% { transform: scale(1.05); opacity: 1; }
                100% { transform: scale(1); opacity: 0.9; }
            }
        </style>

        <script>
            let width = 0;
            let bar = document.getElementById('progress-bar');
            let txt = document.getElementById('progress-text');
            let loop = setInterval(() => {
                if(width >= 100) {
                    clearInterval(loop);
                    // Tell Streamlit framework that setup timeline is complete
                    window.parent.postMessage({type: 'streamlit:set_page_config', loading_done: true}, '*');
                    document.getElementById('loading-screen').style.display = 'none';
                } else {
                    width++;
                    bar.style.width = width + '%';
                    txt.textContent = width + '%';
                }
            }, 35);
        </script>
        """,
        height=750,
    )
    # Block further Python processing until countdown hits 100
    st.session_state.loading_complete = True
    time.sleep(3.6)
    st.rerun()

# ==========================================
# GLOBAL SIDEBAR & LAYOUT CSS MODIFICATIONS
# ==========================================
st.markdown("""
    <style>
    :root {
        --background-color: #05070f;
        --secondary-background-color: #121626;
        --text-color: #e2e8f0;
    }
    
    header[data-testid="stHeader"], 
    [data-testid="stHeader"],
    .stHeader {
        display: flex !important;
        visibility: visible !important;
        background-color: #05070f !important;
    }
    
    /* Persistent open-state sliver rules for the standard Streamlit sidebar wrapper */
    [data-testid="stSidebar"] {
        min-width: 60px !important;
        transition: transform 0.3s ease !important;
    }
    
    [data-testid="sidebar-toggle"] {
        visibility: visible !important;
        display: block !important;
    }
    
    .block-container {
        padding-top: 3.5rem !important;
        padding-bottom: 1rem !important;
    }
    
    .stApp { background: linear-gradient(135deg, #05070f 0%, #0c0f1d 100%); color: #e2e8f0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    .cyber-logo { font-size: 3.2rem; font-weight: 900; background: linear-gradient(90deg, #00f2fe, #4facfe, #00f2fe); background-size: 200% auto; -webkit-background-clip: text; -webkit-text-fill-color: transparent; line-height: 1.1; font-family: 'Courier New', Courier, monospace; }
    .scanning-line { width: 100%; height: 4px; background: linear-gradient(90deg, transparent, #00f2fe, #4facfe, transparent); background-size: 200% 100%; animation: scanMove 2s linear infinite; margin-bottom: 20px; }
    @keyframes scanMove { 0% { background-position: -200% 0; } 100% { background-position: 200% 0; } }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div, .stNumberInput>div>div>input { background-color: #121626 !important; color: #ffffff !important; border: 1px solid #1f293d !important; border-radius: 10px !important; }
    .feature-card { background: rgba(18, 22, 38, 0.6); border: 1px solid #1f293d; border-radius: 16px; padding: 24px; margin-bottom: 20px; box-shadow: 0 4px 20px rgba(0, 242, 254, 0.05); }
    
    .live-clock { color: #00f2fe; font-family: 'Courier New', monospace; font-size: 1.2rem; font-weight: bold; background: rgba(0, 242, 254, 0.1); padding: 8px 16px; border-radius: 30px; border: 1px solid rgba(0, 242, 254, 0.3); display: inline-block; margin-top: 10px; margin-bottom: 15px; }
    .notification-banner { background: linear-gradient(90deg, #1e1b4b 0%, #311042 100%); border-left: 5px solid #a855f7; border-radius: 8px; padding: 15px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(168, 85, 247, 0.2); }
    .billing-card { background: #111827; border: 2px solid #3b82f6; border-radius: 12px; padding: 20px; text-align: center; }
    
    /* Custom Stylings for the New About Application Block UI */
    .about-app-details { background-color: #121626; border: 1px solid #1f293d; border-radius: 16px; padding: 30px; line-height: 1.6; }
    .about-app-details h2 { color: #ffffff; border-bottom: 1px solid #1f293d; padding-bottom: 12px; margin-top: 0; }
    .about-app-details h3 { color: #00f2fe; margin-top: 25px; margin-bottom: 8px; }
    .about-app-details ul, .about-app-details ol { padding-left: 22px; color: #94a3b8; }
    .about-app-details li { margin-bottom: 8px; }
    .about-app-details strong { color: #ffffff; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# GLOBAL PERSISTENT LANGUAGE SELECTION GRID
# ==========================================
col_lang1, col_lang2 = st.columns([3, 1])
with col_lang2:
    selected_language = st.selectbox("🌐 GLOBAL TRANSLATION LANGUAGE", ["English", "Français"], index=0, key="global_lang_selection_bar")
    st.session_state.lang = selected_language

tr = LANG_DATA.get(st.session_state.lang, LANG_DATA["English"])

# PINNED LIVE CLOCK ADJUSTED FOR TIMEZONE ACCURACY (WAT)
with col_lang1:
    clock_placeholder = st.empty()
    current_time_str = datetime.now(ZoneInfo('Africa/Lagos')).strftime("%Y-%m-%d %H:%M:%S")
    clock_placeholder.markdown(f"<div class='live-clock'>🕒 SYSTEM TIME: {current_time_str}</div>", unsafe_allow_html=True)

# Secure API Auto-Engine Connection
st.session_state.groq_key = os.environ.get("GROQ_API_KEY", "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")
client = Groq(api_key=st.session_state.groq_key)

# ==========================================
# SEAMLESS LOGIN GATE WITH DYNAMIC PIN ACTIVATION
# ==========================================
def render_security_gate():
    st.markdown("<div style='text-align: center; margin-top: 3%;'>", unsafe_allow_html=True)
    st.markdown("<div class='cyber-logo'>⚡ VEKTOR.AI</div>", unsafe_allow_html=True)
    st.caption(tr["gate_title"])
    st.markdown("</div>", unsafe_allow_html=True)
    
    _, center_col, _ = st.columns([1, 1.5, 1])
    with center_col:
        auth_mode = st.tabs([tr["signin"], tr["register"]])
        with auth_mode[0]:
            input_user = st.text_input(tr["username"], key="login_user")
            input_pass = st.text_input(tr["password"], type="password", key="login_pass")
            if st.button(tr["btn_auth"], use_container_width=True):
                vault = load_vault()
                if encode_cred(input_user) in vault and vault[encode_cred(input_user)] == encode_cred(input_pass):
                    
                    # TRIAL AND EXPIRY CHECK AGENT
                    metrics = load_admin_metrics()
                    u_key = encode_cred(input_user)
                    if u_key in metrics:
                        user_meta = metrics[u_key]
                        expiry_time_str = user_meta.get("license_expiry")
                        
                        is_unpaid = user_meta.get("payment_status", "Unpaid") != "Paid"
                        is_expired = False
                        if expiry_time_str:
                            is_expired = datetime.now(ZoneInfo('Africa/Lagos')) > datetime.strptime(expiry_time_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=ZoneInfo('Africa/Lagos'))
                        
                        if is_unpaid and is_expired:
                            st.error("🚨 Your Free Access License Has Expired!")
                            st.write("Please paste a valid structural verification activation key code below to update your operational window matrix.")
                            
                            activation_input = st.text_input("Enter Activation PIN (e.g., VK-XXXX-XXXX):", key="activation_pin_box")
                            if st.button("🔓 Authenticate & Apply Key", use_container_width=True):
                                pins_db = load_pins()
                                if activation_input in pins_db and pins_db[activation_input]["status"] == "Unused":
                                    pin_details = pins_db[activation_input]
                                    
                                    # Flag the token as redeemed
                                    pins_db[activation_input]["status"] = "Claimed"
                                    pins_db[activation_input]["claimed_by"] = input_user
                                    save_pins(pins_db)
                                    
                                    # Apply new timeline variables
                                    if pin_details["is_forever"]:
                                        metrics[u_key]["payment_status"] = "Paid"
                                    else:
                                        days_extension = pin_details["days_allotted"]
                                        new_expiry = datetime.now(ZoneInfo('Africa/Lagos')) + timedelta(days=days_extension)
                                        metrics[u_key]["license_expiry"] = new_expiry.strftime("%Y-%m-%d %H:%M:%S")
                                        metrics[u_key]["payment_status"] = "Unpaid"
                                        
                                    save_admin_metrics(metrics)
                                    st.success("🎉 Activation Successful! Access Window Granted. Please click Authorize Access again.")
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.error("🚨 Invalid or already claimed Activation PIN.")
                            st.stop()
                    
                    st.session_state.authenticated = True
                    st.session_state.current_user = input_user
                    track_user_activity(input_user, action="login")
                    user_history = load_history(input_user)
                    st.session_state.chat_history = user_history.get("chat", [])
                    for k in ["briefing", "draft", "structure", "cross", "tracker", "sandbox", "predictor", "indexer", "runway"]:
                        st.session_state[f"{k}_store"] = user_history.get(k, "")
                    st.rerun()
                else: st.error("🚨 Access Denied.")
        with auth_mode[1]:
            new_user = st.text_input(tr["username"], key="reg_user")
            new_pass = st.text_input(tr["password"], type="password", key="reg_pass")
            if st.button(tr["btn_reg"], use_container_width=True):
                if new_user.strip() != "" and len(new_pass) >= 4:
                    vault = load_vault()
                    if encode_cred(new_user) in vault: st.error("🚨 Account exists.")
                    else:
                        save_to_vault(new_user, new_pass)
                        st.success("Workspace Provisioned! You have been granted a 1-Week Free Trial balance.")
    st.stop()

if not st.session_state.authenticated: render_security_gate()

def query_standalone_engine(prompt):
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return completion.choices[0].message.content
    except Exception as e: return f"Cloud Connection Interrupted: {str(e)}"

track_user_activity(st.session_state.current_user, action="heartbeat")

# Sidebar Operations
with st.sidebar:
    st.markdown("<div class='cyber-logo' style='font-size: 1.8rem;'>⚡ VK-CORE</div>", unsafe_allow_html=True)
    st.caption(f"Logged as: **{st.session_state.current_user}**")
    
    # "ℹ️ About" option has been REMOVED from this dropdown selection menu
    module_selection = st.selectbox(tr["nav_lbl"], [
        tr["comp_panel"], tr["oracle_chat"], tr["exec_brief"], tr["composer"], tr["extractor"], 
        tr["cross_file"], tr["tracker"], tr["sandbox"], tr["predictor"], tr["indexer"], tr["runway_plan"]
    ])
    st.write("---")

    st.markdown("### 🏛️ Dedicated Workspaces")
    if st.button("📝 Open Fullscreen Notepad", use_container_width=True):
        st.session_state.active_view = "NOTEPAD"
        st.rerun()
    if st.button("🎨 Open Media & Vision Foundry", use_container_width=True):
        st.session_state.active_view = "FOUNDRY"
        st.rerun()
    if st.button("💳 Billing & Access Management", use_container_width=True):
        st.session_state.active_view = "BILLING"
        st.rerun()
    # NEW: Dedicated Standalone About Application Button in the Sidebar
    if st.button("ℹ️ About Application", use_container_width=True):
        st.session_state.active_view = "ABOUT"
        st.rerun()
        
    st.write("---")
    st.markdown("### 💾 Core Export Tools")
    export_filename = st.text_input(tr["save_fn"], value="vektor_report.txt")
    
    current_export_payload = f"Vektor AI Operational Log Archive\nUser: {st.session_state.current_user}\nModule Target: {module_selection}\n---\n"
    if module_selection == tr["oracle_chat"]: current_export_payload += json.dumps(st.session_state.get("chat_history", []), indent=2)
    elif module_selection == tr["exec_brief"]: current_export_payload += st.session_state.get("briefing_store", "")
    elif module_selection == tr["composer"]: current_export_payload += st.session_state.get("draft_store", "")
    elif module_selection == tr["extractor"]: current_export_payload += st.session_state.get("structure_store", "")
    elif module_selection == tr["cross_file"]: current_export_payload += st.session_state.get("cross_store", "")
    elif module_selection == tr["tracker"]: current_export_payload += st.session_state.get("tracker_store", "")
    elif module_selection == tr["sandbox"]: current_export_payload += st.session_state.get("sandbox_store", "")
    elif module_selection == tr["predictor"]: current_export_payload += st.session_state.get("predictor_store", "")
    elif module_selection == tr["indexer"]: current_export_payload += st.session_state.get("indexer_store", "")
    elif module_selection == tr["runway_plan"]: current_export_payload += st.session_state.get("runway_store", "")

    st.download_button(label=tr["dl_lbl"], data=current_export_payload, file_name=export_filename, mime="text/plain", use_container_width=True)
    st.write("---")
    if st.button(tr["clear_cache"], use_container_width=True):
        st.session_state.chat_history = []
        for key in ["briefing_store", "draft_store", "structure_store", "cross_store", "tracker_store", "sandbox_store", "predictor_store", "indexer_store", "runway_store"]:
            st.session_state[key] = ""
            save_history(st.session_state.current_user, key.replace("_store", ""), "")
        save_history(st.session_state.current_user, "chat", [])
        st.toast("Local persistent records flushed cleanly!")
        st.rerun()
    if st.button(tr["logout"], use_container_width=True):
        metrics = load_admin_metrics()
        u_key = encode_cred(st.session_state.current_user)
        if u_key in metrics:
            metrics[u_key]["status"] = "Inactive"
            save_admin_metrics(metrics)
        st.session_state.authenticated = False
        st.rerun()

# ==========================================
# CENTRALIZED AUTOMATED SYSTEM NOTIFICATION GENERATOR
# ==========================================
metrics_db = load_admin_metrics()
user_encoded_key = encode_cred(st.session_state.current_user)
if user_encoded_key in metrics_db:
    meta_info = metrics_db[user_encoded_key]
    exp_date_str = meta_info.get("license_expiry")
    payment_status = meta_info.get("payment_status", "Unpaid")
    
    if exp_date_str:
        exp_datetime = datetime.strptime(exp_date_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=ZoneInfo('Africa/Lagos'))
        time_delta = exp_datetime - datetime.now(ZoneInfo('Africa/Lagos'))
        
        if payment_status != "Paid":
            if time_delta.total_seconds() > 0:
                hours_left = int(time_delta.total_seconds() // 3600)
                days_left = hours_left // 24
                st.markdown(f"""
                    <div class='notification-banner'>
                        🔔 <b>SYSTEM ALERT / TRIAL STATUS COUNTER:</b> You are running on an evaluation workspace matrix profile. 
                        Your trial window expires in exactly <b>{days_left} Days ({hours_left} Hours)</b>. 
                        Please apply a permanent license activation token to keep cloud data lines uninterrupted.
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                    <div class='notification-banner' style='border-left: 5px solid #ef4444;'>
                        🚨 <b>CRITICAL NOTIFICATION:</b> Your local computation timeline runtime profile token has officially expired. 
                        Please navigate to the Billing & Access Module or consult administration immediately.
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div class='notification-banner' style='border-left: 5px solid #10b981; background: linear-gradient(90deg, #064e3b 0%, #022c22 100%);'>
                    ✅ <b>LICENSE MATRIX STATUS:</b> Verified Secure Sovereign Enterprise Channel. No ongoing pipeline interruptions detected.
                </div>
            """, unsafe_allow_html=True)

# SCREEN 1: DEDICATED FULLSCREEN NOTEPAD INTERFACE
if st.session_state.active_view == "NOTEPAD":
    st.markdown("<div class='cyber-logo'>📝 SECURE WORKSPACE NOTEPAD STORAGE</div>", unsafe_allow_html=True)
    st.caption("Auto-Saving Encryption Grid — Resizeable Viewport Block")
    
    notepad_pack = load_notepad(st.session_state.current_user)
    current_text = notepad_pack.get("current", "")
    saved_history = notepad_pack.get("history", [])
    
    box_height = st.slider("📐 Adjust Custom Workspace Height (Pixels):", 200, 800, 400, step=50)
    notepad_input = st.text_area("Write updates, code files, or business strategy details:", value=current_text, height=box_height)
    
    col_n1, col_n2 = st.columns(2)
    with col_n1:
        if st.button("💾 Securely Save & Sync Updates", use_container_width=True):
            if notepad_input.strip() != "" and notepad_input != current_text:
                if notepad_input not in saved_history:
                    saved_history.insert(0, notepad_input)
            save_notepad(st.session_state.current_user, notepad_input, saved_history)
            st.success("Changes synced securely to workspace state database!")
    with col_n2:
        if st.button("🏠 Return to System Dashboard", use_container_width=True):
            st.session_state.active_view = "HOME"
            st.rerun()
            
    st.write("---")
    st.markdown("### 📑 Recently Saved Memory Vault Logs")
    if saved_history:
        for index, historical_note in enumerate(saved_history[:5]):
            with st.expander(f"Log Memory File #{index + 1} — Snippet: {historical_note[:40]}..."):
                st.code(historical_note)
                if st.button(f"🔄 Reload Log File #{index + 1} Into Main Text Box", key=f"reload_note_{index}"):
                    save_notepad(st.session_state.current_user, historical_note, saved_history)
                    st.toast("Note loaded successfully into editor view!")
                    st.rerun()
    else:
        st.caption("No historical notes logged inside the local workspace matrix yet.")
    st.stop()

# SCREEN 2: MULTIMODAL MEDIA FOUNDRY & VISION STUDIO
elif st.session_state.active_view == "FOUNDRY":
    st.markdown("<div class='cyber-logo'>🎨 MULTIMODAL MEDIA CONTENT FOUNDRY & VISION CAMERA</div>", unsafe_allow_html=True)
    st.caption("High-Fidelity Real Image Generation, Text-to-Audio Scripting, and Photo Manipulation Matrix")
    
    if st.button("🏠 Return to System Dashboard", use_container_width=True):
        st.session_state.active_view = "HOME"
        st.rerun()
        
    st.write("---")
    col_m1, col_m2 = st.columns([2, 1])
    with col_m1:
        creative_prompt = st.text_input("Enter generation description details:", placeholder="e.g., Ultra-modern corporate high-rise office in Lagos, cyberpunk aesthetics")
    with col_m2:
        media_output_type = st.radio("Output Modality Targets:", ["Render Real AI Image", "Generate Audio voiceover Script"])

    if st.button("🔥 Initialize Media Generation Engine", use_container_width=True):
        if creative_prompt.strip() != "":
            st.markdown("<div class='scanning-line'></div>", unsafe_allow_html=True)
            if media_output_type == "Render Real AI Image":
                encoded_prompt = urllib.parse.quote(creative_prompt)
                real_image_url = f"https://image.pollinations.ai/p/{encoded_prompt}?width=1024&height=512&seed=42&nofeed=true"
                st.markdown(f"<div class='feature-card'><h4>🖼️ Output Image Generated Result Matrix:</h4></div>", unsafe_allow_html=True)
                st.image(real_image_url, use_container_width=True)
            else:
                audio_desc_prompt = f"Convert this description into a highly detailed voiceover text script with technical audio sound design cues: '{creative_prompt}'"
                simulated_audio_script = query_standalone_engine(audio_desc_prompt)
                st.markdown(f"<div class='feature-card'><h4>🔊 Immersive Audio Description Script:</h4><br>{simulated_audio_script}</div>", unsafe_allow_html=True)

    st.write("---")
    st.markdown("### 📷 Live Vision Shutter Engine & Photo Studio")
    camera_picture = st.camera_input("Position the item or face in front of your lens:")
    
    if camera_picture:
        st.success("📸 Picture snapshot taken successfully!")
        raw_img = Image.open(camera_picture)
        col_ed1, col_ed2 = st.columns([1, 2])
        
        with col_ed1:
            st.markdown("#### 🛠️ Photo Editing Tools")
            rotation = st.selectbox("Rotate Image:", [0, 90, 180, 240, 270])
            resize_scale = st.slider("Resize Scale (%):", 10, 100, 100)
            color_mode = st.radio("Apply Visual Filter:", ["Original Color", "Black & White (Grayscale)", "High Contrast Sepia"])
            
            edited_img = raw_img
            if rotation != 0:
                edited_img = edited_img.rotate(rotation, expand=True)
            if resize_scale < 100:
                new_w = int(edited_img.width * (resize_scale / 100.0))
                new_h = int(edited_img.height * (resize_scale / 100.0))
                edited_img = edited_img.resize((new_w, new_h))
            if color_mode == "Black & White (Grayscale)":
                edited_img = edited_img.convert("L")
            elif color_mode == "High Contrast Sepia":
                sepia_img = edited_img.convert("RGB")
                pixels = sepia_img.load()
                for y in range(sepia_img.height):
                    for x in range(sepia_img.width):
                        r, g, b = pixels[x, y]
                        tr = int(0.393 * r + 0.769 * g + 0.189 * b)
                        tg = int(0.349 * r + 0.686 * g + 0.168 * b)
                        tb = int(0.272 * r + 0.534 * g + 0.131 * b)
                        pixels[x, y] = (min(tr, 255), min(tg, 255), min(tb, 255))
                edited_img = sepia_img

        with col_ed2:
            st.markdown("#### 🖼️ Live Output Workspace")
            st.image(edited_img, caption="Edited Result Preview Target", use_container_width=True)
            
            img_buffer = io.BytesIO()
            edited_img.save(img_buffer, format="PNG")
            st.download_button(
                label="📥 Download Edited Picture Asset",
                data=img_buffer.getvalue(),
                file_name="edited_snapped_photo.png",
                mime="image/png",
                use_container_width=True
            )
        
        st.write("---")
        st.markdown("#### 🔬 AI Vision Analysis & Context Insights")
        vision_instruction = st.text_input(
            "What information would you like the AI to extract or evaluate about this item?", 
            value="Examine what this object/document is and provide an operational or industrial breakdown profile."
        )
        
        if st.button("🔍 Run Diagnostic Image Analysis", use_container_width=True):
            st.markdown("<div class='scanning-line'></div>", unsafe_allow_html=True)
            vision_analysis = query_standalone_engine(
                f"The user has captured an asset photo measuring {edited_img.width}x{edited_img.height} pixels using color filter template '{color_mode}'. "
                f"Based on their prompt request: '{vision_instruction}', provide an extensive professional evaluation, technical specification insights, "
                f"and strategic recommendations written in language {st.session_state.lang} reflecting 2026 guidelines."
            )
            st.markdown(f"<div class='feature-card'><h4>📡 Vision Node Diagnostic Report:</h4><br>{vision_analysis}</div>", unsafe_allow_html=True)
    st.stop()

# SCREEN 3: BILLING METHOD & LICENSE EXTENSION PORTAL
elif st.session_state.active_view == "BILLING":
    st.markdown("<div class='cyber-logo'>💳 CORE BILLING NODES & LICENSE ACCELERATOR</div>", unsafe_allow_html=True)
    st.caption("Provision Payments, Redeem Structural Activation Invoices, and View Account Lifespan Matrices")
    
    if st.button("🏠 Return to System Dashboard", use_container_width=True):
        st.session_state.active_view = "HOME"
        st.rerun()
        
    st.write("---")
    
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        st.markdown("### 📊 Active Subscription Parameter Metrics")
        user_meta_profile = load_admin_metrics().get(encode_cred(st.session_state.current_user), {})
        
        st.write(f"**Account Identity Space:** {st.session_state.current_user}")
        st.write(f"**Current Structural Tier Status:** `{user_meta_profile.get('payment_status', 'Unpaid')}`")
        st.write(f"**Computation Lifespan End Threshold:** `{user_meta_profile.get('license_expiry', 'N/A')}`")
        
    with col_b2:
        st.markdown("<div class='billing-card'>", unsafe_allow_html=True)

    st.markdown(
        "<h4>👑 Upgrade to Unlimited Sovereign Space</h4>",
        unsafe_allow_html=True
    )

    st.write(
        "Unlock unrestricted model context pipelines, unlimited local "
        "vector database indices, and premium risk tools.\n\n"
        "📞 Contact Management: +2348024300891\n"
        "For activation codes and payment bank details. Thank you."
    )

    st.markdown(
        """
        <h3 style='color:#3b82f6;'>$3.99 = #5,499 / Week</h3>
        <h3 style='color:#3b82f6;'>$11.99 = #16,599 / Month</h3>
        <h3 style='color:#3b82f6;'>$22.99 = #30,199 / 2 Months</h3>
        """,
        unsafe_allow_html=True
    )

    st.markdown("</div>", unsafe_allow_html=True)
        
    st.write("---")
    st.markdown("### 🔑 Apply New Strategic License Token Override")
    manual_invoice_pin = st.text_input("Input Generated Administration Activation Key (PIN):", placeholder="e.g., VK-XXXX-XXXX")
    if st.button("🔓 Submit Registration Renewal Block", use_container_width=True):
        if manual_invoice_pin.strip() != "":
            pins_database = load_pins()
            if manual_invoice_pin in pins_database and pins_database[manual_invoice_pin]["status"] == "Unused":
                pin_info = pins_database[manual_invoice_pin]
                user_hashed_key = encode_cred(st.session_state.current_user)
                all_metrics = load_admin_metrics()
                
                pins_database[manual_invoice_pin]["status"] = "Claimed"
                pins_database[manual_invoice_pin]["claimed_by"] = st.session_state.current_user
                save_pins(pins_database)
                
                if pin_info["is_forever"]:
                    all_metrics[user_hashed_key]["payment_status"] = "Paid"
                else:
                    added_days = pin_info["days_allotted"]
                    current_exp_str = all_metrics[user_hashed_key].get("license_expiry")
                    
                    if current_exp_str and datetime.strptime(current_exp_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=ZoneInfo('Africa/Lagos')) > datetime.now(ZoneInfo('Africa/Lagos')):
                        base_datetime = datetime.strptime(current_exp_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=ZoneInfo('Africa/Lagos'))
                    else:
                        base_datetime = datetime.now(ZoneInfo('Africa/Lagos'))
                        
                    new_computed_exp = base_datetime + timedelta(days=added_days)
                    all_metrics[user_hashed_key]["license_expiry"] = new_computed_exp.strftime("%Y-%m-%d %H:%M:%S")
                    all_metrics[user_hashed_key]["payment_status"] = "Unpaid"
                    
                save_admin_metrics(all_metrics)
                st.success("🎉 Matrix Timeline Extension Applied! Click below to return.")
                time.sleep(1)
                st.rerun()
            else:
                st.error("🚨 Specified verification key index string is invalid or already consumed.")
    st.stop()

# SCREEN 4: DEDICATED FULLSCREEN ABOUT APPLICATION VIEW
elif st.session_state.active_view == "ABOUT":
    st.markdown("<div class='cyber-logo'>ℹ️ ABOUT VEKTOR AI</div>", unsafe_allow_html=True)
    st.caption("Sovereign Information Portal — System Blueprint & Operations Manual")
    
    if st.button("🏠 Return to System Dashboard", use_container_width=True):
        st.session_state.active_view = "HOME"
        st.rerun()
        
    st.write("---")
    
    st.markdown(
        """
        <div class="about-app-details">
            <h2>About Vektor AI</h2>
            <p><strong>Version:</strong> 1.0.0 Stable Matrix</p>
            <p><strong>Architecture:</strong> Multi-Agent Autonomous Workspace System</p>
            <p>Vektor AI is a cutting-edge computing ecosystem engineered to streamline workflows, data management, and AI execution blocks. It bridges deep technical capability with functional, daily-use developer utilities, empowering users with instant command access through a unified local interface.</p>
            
            <h3>How to Navigate Around the App</h3>
            <ol>
                <li><strong>Core Engine Control</strong>: Use the drop-down box at the top of the left sidebar to cycle through modules like the Oracle Chat, Executive Briefing Engine, or Resource Predictor.</li>
                <li><strong>Dedicated Workspaces</strong>: Switch between fullscreen environments (Notepad, Vision Foundry, Billing Ledger, and this manual) by clicking their respective dedicated buttons in the sidebar.</li>
                <li><strong>Resetting Cache</strong>: If you ever need to clear local historical parameters, click <em>"Clear Cache Data"</em> in the sidebar to flush files cleanly.</li>
            </ol>

            <h3>Things the App Can Do</h3>
            <ul>
                <li><strong>Dynamic Pricing Oracle</strong>: Fetch current global market commodity evaluations instantly and convert values into any target currency.</li>
                <li><strong>Document Processing (PDF)</strong>: Ingest multi-page documents to execute context chats, cross-file audits, structural content extraction, and key milestone logging.</li>
                <li><strong>Multimodal Foundry</strong>: Render photorealistic generative imagery on demand, create custom narration scripts, and access real-time device camera feeds with dynamic filters and analysis.</li>
                <li><strong>Runway & Risk Simulators</strong>: Process liability spreadsheets, compute capitalization structures, and stress-test target portfolios against simulated macroeconomic shock scenarios.</li>
            </ul>

            <h3>How to Pay for the App</h3>
            <p>Vektor AI works on a flexible subscription model. Follow these simple steps to activate or renew your license:</p>
            <ol>
                <li><strong>Contact Admin</strong>: Reach out directly via WhatsApp or Phone to register your payment at <strong>+2348024300891</strong>.</li>
                <li><strong>Select a Billing Tier</strong>:
                    <ul>
                        <li><strong>1 Week Plan</strong>: $3.99 (~ ₦5,499)</li>
                        <li><strong>1 Month Plan</strong>: $11.99 (~ ₦16,599)</li>
                        <li><strong>2 Month Plan</strong>: $22.99 (~ ₦30,199)</li>
                    </ul>
                </li>
                <li><strong>Apply Your Key</strong>: Once payment is complete, the admin will generate a secure PIN (e.g., <code>VK-XXXX-XXXX</code>). Paste this code into either the login-block window or the <em>Billing & Access Management</em> portal to instantly extend your access matrix.</li>
            </ol>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.stop()

# SCREEN 5: MASTER DASHBOARD BASE PLATFORM
st.markdown(f"<div class='cyber-logo'>{tr['title']}</div>", unsafe_allow_html=True)
st.write("---")

st.markdown("### 🚀 Dynamic Workspace Hot-Keys")
col_panel1, col_panel2, col_panel3 = st.columns(3)
with col_panel1:
    if st.button("📝 Open Fullscreen Resizable Notepad Engine", use_container_width=True):
        st.session_state.active_view = "NOTEPAD"
        st.rerun()
with col_panel2:
    if st.button("🎨 Open Camera Snap & AI Image Content Foundry", use_container_width=True):
        st.session_state.active_view = "FOUNDRY"
        st.rerun()
with col_panel3:
    if st.button("💳 Open Billing & Subscription Ledger", use_container_width=True):
        st.session_state.active_view = "BILLING"
        st.rerun()

st.write("---")

st.subheader(tr["search_title"])
with st.container():
    col_s1, col_s2 = st.columns([3, 1])
    with col_s1: search_item = st.text_input("Look up global commodity pricing:", placeholder=tr["search_ph"], key="g_search_bar")
    with col_s2: target_currency = st.text_input(tr["curr_lbl"], value="₦ (NGN)", key="g_curr_bar")
    
    if st.button(tr["search_btn"], use_container_width=True):
        if search_item.strip() != "":
            st.markdown("<div class='scanning-line'></div>", unsafe_allow_html=True)
            res = query_standalone_engine(f"As an economy analyst, find the current global market pricing of '{search_item}' and convert it into {target_currency}. Provide a detailed breakdown in {st.session_state.lang} reflecting 2026 insights.")
            st.markdown(f"<div class='feature-card'><b>{tr['orac_res']}</b><br><br>{res}</div>", unsafe_allow_html=True)

st.write("---")
uploaded_files = st.file_uploader(tr["upload_lbl"], type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    if 'document_dict' not in st.session_state or len(st.session_state.document_dict) != len(uploaded_files):
        parsed_docs = {}
        full_raw_text = ""
        for file in uploaded_files:
            text_accumulator = ""
            try:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text: text_accumulator += page_text + "\n"
                parsed_docs[file.name] = text_accumulator
                full_raw_text += text_accumulator + "\n"
            except Exception as e: st.error(f"Error on {file.name}: {str(e)}")
        st.session_state.document_dict = parsed_docs
        st.session_state.raw_context = full_raw_text
        st.toast(tr["success_ac"], icon="🔥")

context_ready = 'raw_context' in st.session_state and st.session_state.raw_context.strip() != ""

# ========================================================
# CENTRALIZED MODULAR VIEWS (ROUTED VIA module_selection)
# ========================================================
if module_selection == tr["comp_panel"]:
    st.subheader(tr["comp_panel"])
    with st.expander("🛠 Rose Graph Configuration Studio", expanded=True):
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            chart_type = st.selectbox("Select Display Style:", ["Line Chart", "Bar Chart", "Area Chart"])
            x_label = st.text_input("Label X-Axis:", value="Timeline")
        with col_g2:
            y_label = st.text_input("Label Y-Axis:", value="Performance")
            custom_data_points = st.text_input(tr["metrics_lbl"], value="10, 25, 18, 35, 42, 38, 50")
    try:
        data_list = [float(i.strip()) for i in custom_data_points.split(",") if i.strip() != ""]
        chart_data = pd.DataFrame({x_label: range(1, len(data_list) + 1), y_label: data_list}).set_index(x_label)
        if chart_type == "Line Chart": st.line_chart(chart_data)
        elif chart_type == "Bar Chart": st.bar_chart(chart_data)
        elif chart_type == "Area Chart": st.area_chart(chart_data)
    except: st.error("🚨 Formatting Error.")

elif module_selection == tr["oracle_chat"]:
    st.subheader(tr["oracle_chat"])
    user_query = st.text_input("Query data context:", placeholder="What are our core operational findings?")
    if user_query:
        if not context_ready: st.error(tr["error_ingest"])
        else:
            st.markdown("<div class='scanning-line'></div>", unsafe_allow_html=True)
            prompt = f"Context:\n{st.session_state.raw_context[:4000]}\n\nQuestion: {user_query}\nAnswer in language {st.session_state.lang}:"
            reply = query_standalone_engine(prompt)
            st.session_state.chat_history.append((user_query, reply))
            save_history(st.session_state.current_user, "chat", st.session_state.chat_history)
    if st.session_state.get("chat_history"):
        for q, a in reversed(st.session_state.chat_history):
            st.markdown(f"<div class='feature-card'><b>❓ Query:</b> {q}<br><br><b>🤖 Answer:</b><br>{a}</div>", unsafe_allow_html=True)

elif module_selection == tr["exec_brief"]:
    st.subheader(tr["exec_brief"])
    if st.button(tr["run_diag"], use_container_width=True):
        if not context_ready: st.error(tr["error_ingest"])
        else:
            st.markdown("<div class='scanning-line'></div>", unsafe_allow_html=True)
            prompt = f"Using this text context:\n{st.session_state.raw_context[:4000]}\n\nProvide an executive briefing in language {st.session_state.lang}: 3 bullet summaries, key risk factors, and deadlines."
            st.session_state.briefing_store = query_standalone_engine(prompt)
            save_history(st.session_state.current_user, "briefing", st.session_state.briefing_store)
    if st.session_state.get("briefing_store"): st.markdown(f"<div class='feature-card'>{st.session_state.briefing_store}</div>", unsafe_allow_html=True)

elif module_selection == tr["composer"]:
    st.subheader(tr["composer"])
    style = st.selectbox("Style:", ["Professional Email", "Formal Memorandum", "Slack Alert"])
    notes = st.text_input("Special requests:", placeholder="Keep it direct.")
    if st.button(tr["calc_btn"], use_container_width=True):
        if not context_ready: st.error(tr["error_ingest"])
        else:
            st.markdown("<div class='scanning-line'></div>", unsafe_allow_html=True)
            prompt = f"Context:\n{st.session_state.raw_context[:4000]}\n\nCompose a {style} in language {st.session_state.lang}. Special Instruction: {notes}"
            st.session_state.draft_store = query_standalone_engine(prompt)
            save_history(st.session_state.current_user, "draft", st.session_state.draft_store)
    if st.session_state.get("draft_store"): st.markdown(f"<div class='feature-card'>{st.session_state.draft_store}</div>", unsafe_allow_html=True)

elif module_selection == tr["extractor"]:
    st.subheader(tr["extractor"])
    target = st.text_input("Data to mine:", value="Names, Dates, Key Figures")
    if st.button(tr["calc_btn"], use_container_width=True):
        if not context_ready: st.error(tr["error_ingest"])
        else:
            st.markdown("<div class='scanning-line'></div>", unsafe_allow_html=True)
            prompt = f"Context text:\n{st.session_state.raw_context[:4000]}\n\nExtract all information relating to {target} in language {st.session_state.lang}."
            st.session_state.structure_store = query_standalone_engine(prompt)
            save_history(st.session_state.current_user, "structure", st.session_state.structure_store)
    if st.session_state.get("structure_store"): st.markdown(f"<div class='feature-card'>{st.session_state.structure_store}</div>", unsafe_allow_html=True)

elif module_selection == tr["cross_file"]:
    st.subheader(tr["cross_file"])
    if not context_ready or len(st.session_state.get('document_dict', {})) < 2:
        st.warning("⚠️ Cross-File operations require at least two PDF files uploaded simultaneously.")
    else:
        audit_query = st.text_input("Audit Query:", value="Are there contradictions across these items?")
        if st.button(tr["calc_btn"], use_container_width=True):
            st.markdown("<div class='scanning-line'></div>", unsafe_allow_html=True)
            aggregated_context = ""
            for name, content in st.session_state.document_dict.items(): aggregated_context += f"--- FILE: {name} ---\n{content[:2000]}\n"
            prompt = f"Analyze these files in language {st.session_state.lang} for contradictions:\n{aggregated_context}\nDirective: {audit_query}"
            st.session_state.cross_store = query_standalone_engine(prompt)
            save_history(st.session_state.current_user, "cross", st.session_state.cross_store)
    if st.session_state.get("cross_store"): st.markdown(f"<div class='feature-card'>{st.session_state.cross_store}</div>", unsafe_allow_html=True)

elif module_selection == tr["tracker"]:
    st.subheader(tr["tracker"])
    if st.button(tr["calc_btn"], use_container_width=True):
        if not context_ready: st.error(tr["error_ingest"])
        else:
            st.markdown("<div class='scanning-line'></div>", unsafe_allow_html=True)
            prompt = f"Extract timelines and task actions in language {st.session_state.lang} from:\n{st.session_state.raw_context[:4000]}"
            st.session_state.tracker_store = query_standalone_engine(prompt)
            save_history(st.session_state.current_user, "tracker", st.session_state.tracker_store)
    if st.session_state.get("tracker_store"): st.markdown(f"<div class='feature-card'>{st.session_state.tracker_store}</div>", unsafe_allow_html=True)

elif module_selection == tr["sandbox"]:
    st.subheader(tr["sandbox"])
    idea = st.text_area("Drop design concept matrix coordinates:")
    if st.button(tr["calc_btn"], use_container_width=True) and idea:
        st.markdown("<div class='scanning-line'></div>", unsafe_allow_html=True)
        prompt = f"Act as an expert risk auditor. Stress-test this business idea in language {st.session_state.lang}: '{idea}'"
        st.session_state.sandbox_store = query_standalone_engine(prompt)
        save_history(st.session_state.current_user, "sandbox", st.session_state.sandbox_store)
    if st.session_state.get("sandbox_store"): st.markdown(f"<div class='feature-card'>{st.session_state.sandbox_store}</div>", unsafe_allow_html=True)

elif module_selection == tr["predictor"]:
    st.subheader(tr["predictor"])
    project_brief = st.text_area("Describe the project scope & technical requirements:")
    col_cfg1, col_cfg2 = st.columns(2)
    with col_cfg1: tier_profile = st.selectbox("Strategy Profile:", ["Lean Bootstrap Strategy", "Standard Competitive Infrastructure", "Aggressive Scale Enterprise"])
    with col_cfg2: contingency_buffer = st.slider("Buffer (%):", 5, 30, 15)
    if st.button(tr["calc_btn"], use_container_width=True) and project_brief:
        st.markdown("<div class='scanning-line'></div>", unsafe_allow_html=True)
        prompt = f"Act as a tech project architect. Analyze brief: '{project_brief}'. Strategy: {tier_profile} with {contingency_buffer}% buffer. Report structural ranges using currency {target_currency} written in language {st.session_state.lang}."
        st.session_state.predictor_store = query_standalone_engine(prompt)
        save_history(st.session_state.current_user, "predictor", st.session_state.predictor_store)
    if st.session_state.get("predictor_store"): st.markdown(f"<div class='feature-card'>{st.session_state.predictor_store}</div>", unsafe_allow_html=True)

elif module_selection == tr["indexer"]:
    st.subheader(tr["indexer"])
    if st.button(tr["calc_btn"], use_container_width=True):
        if not context_ready: st.error(tr["error_ingest"])
        else:
            st.markdown("<div class='scanning-line'></div>", unsafe_allow_html=True)
            prompt = f"Generate a technical index and metadata taxonomy tags in language {st.session_state.lang} for:\n{st.session_state.raw_context[:4000]}"
            st.session_state.indexer_store = query_standalone_engine(prompt)
            save_history(st.session_state.current_user, "indexer", st.session_state.indexer_store)
    if st.session_state.get("indexer_store"): st.markdown(f"<div class='feature-card'>{st.session_state.indexer_store}</div>", unsafe_allow_html=True)

elif module_selection == tr["runway_plan"]:
    st.subheader(tr["runway_plan"])
    financial_doc = st.file_uploader("Upload Revenue Statement (PDF)", type=["pdf"])
    total_liabilities = st.number_input("Enter Total Expenses/Liabilities:", value=0, step=100)
    if st.button(tr["calc_btn"], use_container_width=True):
        revenue_text = ""
        if financial_doc:
            pdf_read = PyPDF2.PdfReader(financial_doc)
            for page in pdf_read.pages:
                t = page.extract_text()
                if t: revenue_text += t + "\n"
        st.markdown("<div class='scanning-line'></div>", unsafe_allow_html=True)
        prompt = f"Act as a virtual corporate CFO. Statement: '{revenue_text[:2000]}'. Expenses: {total_liabilities} in {target_currency}. Map items sold, calculate net remainder growth capital, and list step-by-step optimization tactics in language {st.session_state.lang}."
        st.session_state.runway_store = query_standalone_engine(prompt)
        save_history(st.session_state.current_user, "runway", st.session_state.runway_store)
    if st.session_state.get("runway_store"): st.markdown(f"<div class='feature-card'>{st.session_state.runway_store}</div>", unsafe_allow_html=True)

st.write("---")
st.markdown("## 💎 Premium Asset Allocation & Macro Shock Simulator")
st.caption("Strategic Decision Engine for High-Net-Worth Portfolios and Enterprise Capital")

with st.container():
    col_inv1, col_inv2, col_inv3 = st.columns(3)
    with col_inv1:
        liquidity_reserve = st.number_input("Core Capital Reserve ($)", value=50000000, step=5000000)
        venture_allocation = st.slider("Venture & Growth Allocation (%)", 0, 100, 25)
    with col_inv2:
        commodity_hedge = st.slider("Commodity & Hard Asset Hedge (%)", 0, 100, 15)
        yield_target = st.slider("Target Internal Rate of Return (IRR %)", 5, 45, 18)
    with col_inv3:
        macro_shock_scenario = st.selectbox("Simulate Global Macro Economic Shock:", [
            "Baseline Stable Growth Economy",
            "Severe Global Supply Chain Disruption",
            "Rapid Hyper-Inflationary Surge",
            "Aggressive Interest Rate Hikes"
        ])

    if st.button("⚡ Run Portfolio Stress-Test & Core Diagnostics", use_container_width=True):
        st.markdown("<div class='scanning-line'></div>", unsafe_allow_html=True)
        
        growth_cap = liquidity_reserve * (venture_allocation / 100.0)
        hedge_cap = liquidity_reserve * (commodity_hedge / 100.0)
        conservative_remainder = liquidity_reserve - (growth_cap + hedge_cap)
        
        simulation_prompt = f"""
        Act as an elite sovereign wealth fund strategist and risk auditor. 
        Analyze the following corporate asset matrix:
        - Total Liquid Capital: ${liquidity_reserve:,}
        - Growth/Venture Risk Exposure: {venture_allocation}% (${growth_cap:,})
        - Commodity/Hedge Safeguard: {commodity_hedge}% (${hedge_cap:,})
        - Secure Cash/Yield Remainder: ${conservative_remainder:,}
        - Target Yield Expectation: {yield_target}%
        
        The user has initiated a stress-test against this specific macro environment: '{macro_shock_scenario}'.
        Provide an executive threat assessment, determine if the target IRR is mathematically viable under this shock, and outline the exact capital reallocation adjustments required to insulate this wealth.
        """
        risk_analysis = query_standalone_engine(simulation_prompt)
        st.markdown(f"<div class='feature-card'><h3>📊 Tactical Risk Matrix Diagnostic Output</h3><br>{risk_analysis}</div>", unsafe_allow_html=True)
        
        allocation_metrics = pd.DataFrame({
            "Asset Pillars": ["Venture Growth", "Hard Asset Hedge", "Conservative Cash"],
            "Capital Allocation ($)": [growth_cap, hedge_cap, conservative_remainder]
        }).set_index("Asset Pillars")
        st.bar_chart(allocation_metrics)
