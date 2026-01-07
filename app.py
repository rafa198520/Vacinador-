import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sqlite3
import hashlib

# --- 1. CONFIGURAÇÕES DE PÁGINA ---
st.set_page_config(page_title="PNI Elite Pro", layout="wide", page_icon="💉")

# --- 2. SEGURANÇA ---
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def get_connection():
    return sqlite3.connect('usuarios_vax.db', check_same_thread=False)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT PRIMARY KEY, password TEXT, role TEXT)')
    c.execute('INSERT OR IGNORE INTO userstable VALUES (?,?,?)', ('rafa198520', make_hashes('002566Rafa@'), 'admin'))
    conn.commit()
    conn.close()

def login_user(username, password):
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM userstable WHERE username =? AND password =?', (username, password))
    data = c.fetchall()
    conn.close()
    return data

# --- 3. CSS PARA CORRIGIR ERROS VISUAIS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
    
    /* ESCONDE O ERRO KEYBOARD_DOUBLE E O BOTÃO PADRÃO QUE ESTÁ FALHANDO */
    button[kind="headerNoPadding"] { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }
    span:contains("keyboard_double") { display: none !important; }
    .st-emotion-cache-1vt4y6f { display: none !important; }

    html, body, [class*="st-"] { 
        font-family: 'Plus Jakarta Sans', sans-serif; 
        color: #000000 !important; 
    }

    .hero-section { 
        background: linear-gradient(135deg, #013A71 0%, #001d3d 100%); 
        padding: 25px; 
        border-radius: 15px; 
        color: white; 
        text-align: center; 
        margin-bottom: 20px; 
    }

    .tech-card { 
        background: white; 
        padding: 20px; 
        border-radius: 12px; 
        border: 2px solid #e2e8f0; 
        margin-bottom: 15px; 
    }

    .tech-item { 
        display: flex; 
        justify-content: space-between;
        padding: 10px 0; 
        border-bottom: 1px solid #f1f5f9; 
    }
    .tech-label { color: #64748b; font-weight: 600; font-size: 14px; }
    .tech-value { color: #000000; font-weight: 800; text-align: right; }

    .stButton > button { 
        width: 100%; 
        background: #013A71; 
        color: white !important; 
        font-weight: 800; 
        border-radius: 10px; 
        height: 3.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

init_db()

# --- 4. LOGIN ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.markdown("<h2 style='text-align: center; color: #013A71;'>🔒 ACESSO PORTAL</h2>", unsafe_allow_html=True)
    col_l, col_c, col_r = st.columns([1,2,1])
    with col_c:
        user = st.text_input("Usuário")
        passwd = st.text_input("Senha", type='password')
        if st.button("ENTRAR"):
            if login_user(user, make_hashes(passwd)):
                st.session_state['logged_in'] = True
                st.session_state['username'] = user
                st.session_state['role'] = login_user(user, make_hashes(passwd))[0][2]
                st.rerun()
            else: st.error("Incorreto.")
else:
    # BANCO DE DADOS INTEGRAL
    DADOS_PNI = {
        "INFANTIL (0-12m)": {
            "BCG": {"via": "ID", "local": "Deltoide Dir.", "agulha": "13 x 0,45mm", "doses": ["Única"], "ret": 0, "tipo": "ATENUADA", "previne": "Formas graves de Tuberculose."},
            "HEPATITE B (RN)": {"via": "IM", "local": "Vasto Lateral Dir.", "agulha": "20 x 0,55mm", "doses": ["Dose ao Nascer"], "ret": 30, "tipo": "INATIVADA", "previne": "Hepatite B."},
            "PENTAVALENTE": {"via": "IM", "local": "Vasto Lateral Esq.", "agulha": "20 x 0,55mm", "doses": ["1ª (2m)", "2ª (4m)", "3ª (6m)"], "ret": 60, "tipo": "INATIVADA", "previne": "Difteria, Tétano, Coqueluche, Hep B e Hib."},
            "VIP (POLIO)": {"via": "IM", "local": "Vasto Lateral Dir.", "agulha": "20 x 0,55mm", "doses": ["1ª", "2ª", "3ª", "Ref (15m)"], "ret": 60, "tipo": "INATIVADA", "previne": "Paralisia Infantil."},
            "ROTAVÍRUS": {"via": "VO", "local": "Boca", "agulha": "Bisnaga", "doses": ["1ª (2m)", "2ª (4m)"], "ret": 60, "tipo": "ATENUADA", "previne": "Diarreia grave."},
            "FEBRE AMARELA": {"via": "SC", "local": "Deltoide", "agulha": "13 x 0,45mm", "doses": ["9m", "4a"], "ret": 1095, "tipo": "ATENUADA", "previne": "Febre Amarela."}
        },
        "CRIANÇAS (1-4 anos)": {
            "HEPATITE A": {"via": "IM", "local": "Deltoide", "agulha": "20 x 0,55mm", "doses": ["Única (15m)"], "ret": 0, "tipo": "INATIVADA", "previne": "Hepatite A."},
            "DTP (TRÍPLICE)": {"via": "IM", "local": "Deltoide", "agulha": "20 x 0,55mm", "doses": ["Ref (15m)", "Ref (4a)"], "ret": 1095, "tipo": "INATIVADA", "previne": "Difteria, Tétano e Coqueluche."},
            "SCR (TRÍPLICE VIRAL)": {"via": "SC", "local": "Deltoide Esq.", "agulha": "13 x 0,45mm", "doses": ["12m", "15m"], "ret": 90, "tipo": "ATENUADA", "previne": "Sarampo, Caxumba e Rubéola."}
        },
        "ADULTO / GESTANTE": {
            "HPV": {"via": "IM", "local": "Deltoide", "agulha": "25 x 0,6mm", "doses": ["Dose Única"], "ret": 0, "tipo": "INATIVADA", "previne": "Câncer de Colo e Verrugas."},
            "dTpa": {"via": "IM", "local": "Deltoide", "agulha": "25 x 0,6mm", "doses": ["A partir 20ª sem"], "ret": 0, "tipo": "INATIVADA", "previne": "Difteria, Tétano e Coqueluche."},
            "VSR (ABRYSVO)": {"via": "IM", "local": "Deltoide", "agulha": "25 x 0,6mm", "doses": ["24ª-36ª sem"], "ret": 0, "tipo": "INATIVADA", "previne": "Bronquiolite no RN."}
        }
    }

    # SELETOR DE VACINAS NO TOPO (Para não depender só da barra lateral que some)
    st.markdown("""<div class='hero-section'><h1>SISTEMA IMUNIZAÇÃO 2026</h1></div>""", unsafe_allow_html=True)
    
    with st.expander("📂 SELECIONAR OUTRA VACINA", expanded=False):
        grupo = st.selectbox("CATEGORIA:", list(DADOS_PNI.keys()))
        vacina_nome = st.radio("IMUNOBIOLÓGICO:", list(DADOS_PNI[grupo].keys()))
    
    # Se não selecionou nada ainda, pega a primeira
    v = DADOS_PNI[grupo][vacina_nome]

    # --- EXIBIÇÃO ---
    st.subheader(f"📌 {vacina_nome}")
    
    col_t, col_f = st.columns([1,1])
    with col_t:
        st.markdown(f"""
            <div class="tech-card">
                <div class="tech-item"><span class="tech-label">VIA</span><span class="tech-value">{v['via']}</span></div>
                <div class="tech-item"><span class="tech-label">LOCAL</span><span class="tech-value">{v['local']}</span></div>
                <div class="tech-item"><span class="tech-label">AGULHA</span><span class="tech-value">{v['agulha']}</span></div>
                <div class="tech-item"><span class="tech-label">RETORNO</span><span class="tech-value">{v['ret']} dias</span></div>
            </div>
        """, unsafe_allow_html=True)
        st.info(f"**Protege contra:** {v['previne']}")

    with col_f:
        nome = st.text_input("PACIENTE").upper()
        dose = st.selectbox("DOSE", v["doses"])
        if st.button("REGISTRAR"):
            if nome:
                dt = (datetime.now() + timedelta(days=v['ret'])).strftime("%d/%m/%Y") if v['ret'] > 0 else "OK"
                st.success(f"Retorno: {dt}")
            else: st.error("Nome?")

    if st.sidebar.button("LOGOUT"):
        st.session_state['logged_in'] = False
        st.rerun()
