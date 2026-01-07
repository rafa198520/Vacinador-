import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sqlite3
import hashlib

# --- 1. CONFIGURAÇÕES ---
st.set_page_config(page_title="PNI Elite 2026", layout="wide", page_icon="💉")

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

# --- 3. CSS RESPONSIVO ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
    
    /* REMOVE ERROS VISUAIS DE CABEÇALHO */
    header, [data-testid="stHeader"], [data-testid="collapsedControl"], .keyboard_double {
        display: none !important;
        visibility: hidden !important;
    }

    html, body, [class*="st-"] { font-family: 'Plus Jakarta Sans', sans-serif; color: #000000 !important; }
    .main .block-container { padding-top: 20px !important; }

    /* Banner */
    .hero-section { 
        background: linear-gradient(135deg, #013A71 0%, #001d3d 100%); 
        padding: 30px; border-radius: 15px; color: white; text-align: center; margin-bottom: 20px; 
    }

    /* Cards Estilizados */
    .tech-card { 
        background: white; padding: 20px; border-radius: 12px; border: 2px solid #e2e8f0; margin-bottom: 15px; 
    }
    .tech-item { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #f1f5f9; }
    .tech-label { color: #64748b; font-weight: 600; font-size: 14px; }
    .tech-value { color: #000000; font-weight: 800; text-align: right; }

    /* Botão de Ação */
    .stButton > button { 
        width: 100%; background: #013A71; color: white !important; font-weight: 800; border-radius: 10px; height: 3.5rem; border: none;
    }
    .stButton > button:hover { background: #00B4D8; }
    
    .disease-box { 
        background-color: #f0f7ff; padding: 15px; border-radius: 10px; border-left: 5px solid #00B4D8; margin-top: 10px; font-size: 14px;
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
            else: st.error("Acesso Negado")
else:
    # BANCO DE DADOS INTEGRAL 2026
    DADOS_PNI = {
        "GESTANTES": {
            "VSR (ABRYSVO)": {"via": "IM Profunda", "local": "Deltoide", "agulha": "25x0,6mm", "doses": ["Dose Única (28ª a 36ª sem)"], "ret": 0, "tipo": "INATIVADA", "previne": "Bronquiolite e Pneumonia em bebês pelo VSR."},
            "dTpa (ACELULAR)": {"via": "IM", "local": "Deltoide", "agulha": "25x0,6mm", "doses": ["A partir da 20ª sem"], "ret": 0, "tipo": "INATIVADA", "previne": "Difteria, Tétano e Coqueluche."},
            "HEPATITE B": {"via": "IM", "local": "Deltoide", "agulha": "25x0,6mm", "doses": ["Conforme histórico"], "ret": 30, "tipo": "INATIVADA", "previne": "Hepatite B."}
        },
        "INFANTIL (0-12m)": {
            "BCG": {"via": "ID", "local": "Deltoide Dir.", "agulha": "13x0,45mm", "doses": ["Única"], "ret": 0, "tipo": "ATENUADA", "previne": "Formas graves de Tuberculose."},
            "HEPATITE B (RN)": {"via": "IM", "local": "Vasto Lateral Dir.", "agulha": "20x0,55mm", "doses": ["Ao Nascer"], "ret": 30, "tipo": "INATIVADA", "previne": "Hepatite B."},
            "PENTAVALENTE": {"via": "IM", "local": "Vasto Lateral Esq.", "agulha": "20x0,55mm", "doses": ["1ª(2m)", "2ª(4m)", "3ª(6m)"], "ret": 60, "tipo": "INATIVADA", "previne": "Difteria, Tétano, Coqueluche, Hep B e Hib."},
            "VIP (POLIO)": {"via": "IM", "local": "Vasto Lateral Dir.", "agulha": "20x0,55mm", "doses": ["1ª", "2ª", "3ª", "Ref(15m)"], "ret": 60, "tipo": "INATIVADA", "previne": "Poliomielite."},
            "ROTAVÍRUS": {"via": "VO", "local": "Boca", "agulha": "Bisnaga", "doses": ["1ª", "2ª"], "ret": 60, "tipo": "ATENUADA", "previne": "Diarreia grave."},
            "FEBRE AMARELA": {"via": "SC", "local": "Deltoide", "agulha": "13x0,45mm", "doses": ["9m", "4a"], "ret": 1095, "tipo": "ATENUADA", "previne": "Febre Amarela."}
        },
        "CRIANÇAS E ADULTOS": {
            "HEPATITE A": {"via": "IM", "local": "Deltoide", "agulha": "20x0,55mm", "doses": ["Única (15m)"], "ret": 0, "tipo": "INATIVADA", "previne": "Hepatite A."},
            "DTP (TRÍPLICE)": {"via": "IM", "local": "Deltoide", "agulha": "20x0,55mm", "doses": ["Ref(15m)", "Ref(4a)"], "ret": 1095, "tipo": "INATIVADA", "previne": "Difteria, Tétano e Coqueluche."},
            "SCR (TRÍPLICE VIRAL)": {"via": "SC", "local": "Deltoide Esq.", "agulha": "13x0,45mm", "doses": ["12m", "15m"], "ret": 90, "tipo": "ATENUADA", "previne": "Sarampo, Caxumba e Rubéola."},
            "HPV": {"via": "IM", "local": "Deltoide", "agulha": "25x0,6mm", "doses": ["Única"], "ret": 0, "tipo": "INATIVADA", "previne": "Câncer e verrugas genitais."},
            "INFLUENZA": {"via": "IM", "local": "Deltoide", "agulha": "25x0,6mm", "doses": ["Anual"], "ret": 365, "tipo": "INATIVADA", "previne": "Gripe."}
        }
    }

    # TÍTULO
    st.markdown("""<div class='hero-section'><h1>SISTEMA IMUNIZAÇÃO 2026</h1><p>Versão Universal PC/Celular</p></div>""", unsafe_allow_html=True)
    
    # SELEÇÃO CENTRALIZADA
    st.write("📂 **ESCOLHA O GRUPO E A VACINA:**")
    c1, c2 = st.columns(2)
    with c1:
        grupo_sel = st.selectbox("Grupo:", list(DADOS_PNI.keys()), label_visibility="collapsed")
    with c2:
        vax_sel = st.selectbox("Vacina:", list(DADOS_PNI[grupo_sel].keys()), label_visibility="collapsed")
    
    v = DADOS_PNI[grupo_sel][vax_sel]

    # CONTEÚDO RESPONSIVO
    col_info, col_form = st.columns([1.5, 1], gap="large")

    with col_info:
        st.subheader(f"📌 {vax_sel}")
        st.markdown(f"""
            <div class="tech-card">
                <div class="tech-item"><span class="tech-label">VIA</span><span class="tech-value">{v['via']}</span></div>
                <div class="tech-item"><span class="tech-label">LOCAL</span><span class="tech-value">{v['local']}</span></div>
                <div class="tech-item"><span class="tech-label">AGULHA</span><span class="tech-value">{v['agulha']}</span></div>
                <div class="tech-item"><span class="tech-label">RETORNO</span><span class="tech-value">{v['ret']} dias</span></div>
                <div class="disease-box"><b>🛡️ Previne:</b> {v['previne']}</div>
            </div>
        """, unsafe_allow_html=True)
        
        

    with col_form:
        st.subheader("📝 Registro")
        nome = st.text_input("NOME DO PACIENTE").upper()
        dose = st.selectbox("DOSE:", v["doses"])
        if st.button("REGISTRAR ATENDIMENTO"):
            if nome:
                dt_ret = (datetime.now() + timedelta(days=v['ret'])).strftime("%d/%m/%Y") if v['ret'] > 0 else "OK"
                st.success(f"Registrado! Retorno: {dt_ret}")
                st.balloons()
            else: st.error("⚠️ Nome Obrigatório")

    # SAIR
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚪 SAIR DO SISTEMA"):
        st.session_state['logged_in'] = False
        st.rerun()

st.caption("PNI Master Elite 2026 - Mobile & Desktop Ready")
