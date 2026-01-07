import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sqlite3
import hashlib
import os

# --- 1. CONFIGURAÇÕES DE PÁGINA ---
st.set_page_config(page_title="PNI Elite Mobile", layout="wide", page_icon="💉")

# --- 2. SEGURANÇA E BANCO DE DADOS ---
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

def view_all_users():
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT username, role FROM userstable')
    data = c.fetchall()
    conn.close()
    return data

# --- 3. ESTILIZAÇÃO CSS (FOCO EM CELULAR) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
    
    /* Ajuste de Texto Geral */
    html, body, [class*="st-"] { 
        font-family: 'Plus Jakarta Sans', sans-serif; 
        color: #000000 !important; 
        font-size: 16px; 
    }

    /* Ajuste de Margens para Mobile */
    .main .block-container {
        padding-top: 2rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }

    /* Banner Principal - Reduzido para Mobile */
    .hero-section { 
        background: linear-gradient(135deg, #013A71 0%, #001d3d 100%); 
        padding: 25px 15px; 
        border-radius: 15px; 
        color: white; 
        text-align: center; 
        margin-bottom: 20px; 
    }
    .hero-section h1 { font-size: 1.5rem !important; margin-bottom: 5px; }

    /* Cards Técnicos Responsivos */
    .tech-card { 
        background: white; 
        padding: 15px; 
        border-radius: 12px; 
        border: 2px solid #e2e8f0; 
        margin-bottom: 15px; 
    }
    .tech-item { 
        display: flex; 
        flex-direction: column; /* Empilha no celular */
        padding: 10px 0; 
        border-bottom: 1px solid #f1f5f9; 
    }
    .tech-label { color: #64748b; font-weight: 600; font-size: 13px; text-transform: uppercase; }
    .tech-value { color: #000000; font-weight: 800; font-size: 16px; margin-top: 2px; }

    /* Botões Grandes para o Polegar */
    .stButton > button { 
        width: 100%; 
        height: 55px !important; 
        background: #013A71; 
        color: white !important; 
        font-weight: 800; 
        border-radius: 12px; 
        font-size: 18px !important;
    }

    /* Disease Box Mobile */
    .disease-box { 
        background-color: #f0f7ff; 
        padding: 12px; 
        border-radius: 10px; 
        border-left: 4px solid #00B4D8; 
        margin-top: 10px;
        font-size: 14px;
    }
    
    /* Esconder elementos que poluem o celular */
    [data-testid="stDecoration"] { display: none; }
    </style>
    """, unsafe_allow_html=True)

init_db()

# --- 4. LÓGICA DE LOGIN ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.markdown("<h2 style='text-align: center; color: #013A71;'>🔒 ACESSO PORTAL</h2>", unsafe_allow_html=True)
    user = st.text_input("Usuário")
    passwd = st.text_input("Senha", type='password')
    if st.button("ENTRAR"):
        if login_user(user, make_hashes(passwd)):
            st.session_state['logged_in'] = True
            st.session_state['username'] = user
            st.session_state['role'] = login_user(user, make_hashes(passwd))[0][2]
            st.rerun()
        else: st.error("Usuário/Senha incorretos")
else:
    # --- INTERFACE PRINCIPAL ---
    with st.sidebar:
        st.write(f"👤 **{st.session_state['username']}**")
        if st.button("SAIR"):
            st.session_state['logged_in'] = False
            st.rerun()
        st.divider()
        
        # BANCO DE DADOS (DADOS_PNI permanece igual ao anterior para não tirar nada)
        DADOS_PNI = {
            "CALENDÁRIO INFANTIL (0-12 meses)": {
                "BCG": {"via": "ID", "local": "Deltoide Direito", "agulha": "13 x 0,45mm", "doses": ["Dose Única"], "ret": 0, "tipo": "ATENUADA", "previne": "Formas graves de Tuberculose (Miliar e Meníngea)."},
                "HEPATITE B (RN)": {"via": "IM", "local": "Vasto Lateral Dir.", "agulha": "20 x 0,55mm", "doses": ["Dose ao Nascer"], "ret": 30, "tipo": "INATIVADA", "previne": "Infecção pelo vírus da Hepatite B."},
                "PENTAVALENTE": {"via": "IM", "local": "Vasto Lateral Esq.", "agulha": "20 x 0,55mm", "doses": ["1ª (2m)", "2ª (4m)", "3ª (6m)"], "ret": 60, "tipo": "INATIVADA", "previne": "Difteria, Tétano, Coqueluche, Hep B e Meningite por Hib."},
                "VIP (POLIO)": {"via": "IM", "local": "Vasto Lateral Dir.", "agulha": "20 x 0,55mm", "doses": ["1ª (2m)", "2ª (4m)", "3ª (6m)", "Ref (15m)"], "ret": 60, "tipo": "INATIVADA", "previne": "Poliomielite (Paralisia Infantil)."},
                "PNEUMO 10V": {"via": "IM", "local": "Vasto Lateral Dir.", "agulha": "20 x 0,55mm", "doses": ["1ª (2m)", "2ª (4m)", "Ref (12m)"], "ret": 60, "tipo": "INATIVADA", "previne": "Pneumonia, Meningite e Otite por Pneumococos."},
                "ROTAVÍRUS": {"via": "VO", "local": "Boca", "agulha": "Bisnaga", "doses": ["1ª (2m)", "2ª (4m)"], "ret": 60, "tipo": "ATENUADA", "previne": "Diarreia grave por Rotavírus."},
                "MENINGOCÓCICA C": {"via": "IM", "local": "Vasto Lateral Esq.", "agulha": "20 x 0,55mm", "doses": ["1ª (3m)", "2ª (5m)", "Ref (12m)"], "ret": 60, "tipo": "INATIVADA", "previne": "Doença Meningocócica invasiva sorogrupo C."},
                "FEBRE AMARELA": {"via": "SC", "local": "Deltoide (Braço)", "agulha": "13 x 0,45mm", "doses": ["9 meses", "4 anos"], "ret": 1095, "tipo": "ATENUADA", "previne": "Febre Amarela."}
            },
            "CALENDÁRIO CRIANÇAS (1-4 anos)": {
                "HEPATITE A": {"via": "IM", "local": "Deltoide/Vasto", "agulha": "20 x 0,55mm", "doses": ["Dose Única (15m)"], "ret": 0, "tipo": "INATIVADA", "previne": "Hepatite A."},
                "DTP (TRÍPLICE)": {"via": "IM", "local": "Deltoide/Vasto", "agulha": "20 x 0,55mm", "doses": ["1º Ref (15m)", "2º Ref (4a)"], "ret": 1095, "tipo": "INATIVADA", "previne": "Difteria, Tétano e Coqueluche."},
                "TRÍPLICE VIRAL (SCR)": {"via": "SC", "local": "Deltoide Esq.", "agulha": "13 x 0,45mm", "doses": ["12m", "15m"], "ret": 90, "tipo": "ATENUADA", "previne": "Sarampo, Caxumba e Rubéola."},
                "VARICELA": {"via": "SC", "local": "Deltoide Esq.", "agulha": "13 x 0,45mm", "doses": ["15m", "4a"], "ret": 1095, "tipo": "ATENUADA", "previne": "Varicela (Catapora)."}
            },
            "ADULTO E ADOLESCENTE": {
                "HPV QUADRIVALENTE": {"via": "IM", "local": "Deltoide", "agulha": "25 x 0,6mm", "doses": ["Dose Única"], "ret": 0, "tipo": "INATIVADA", "previne": "Câncer de colo do útero, vulva, vagina, ânus e verrugas genitais."},
                "MENINGO ACWY": {"via": "IM", "local": "Deltoide", "agulha": "25 x 0,6mm", "doses": ["Dose Única"], "ret": 0, "tipo": "INATIVADA", "previne": "Meningites sorogrupos A, C, W e Y."},
                "dT (DUPLA ADULTO)": {"via": "IM", "local": "Deltoide", "agulha": "25 x 0,6mm", "doses": ["Reforço 10 anos"], "ret": 3650, "tipo": "INATIVADA", "previne": "Difteria e Tétano."},
                "PNEUMO 23V": {"via": "IM/SC", "local": "Deltoide", "agulha": "25 x 0,6mm", "doses": ["Dose Única"], "ret": 1825, "tipo": "INATIVADA", "previne": "Doenças pneumocócicas sistêmicas severas."}
            },
            "CALENDÁRIO GESTANTES": {
                "VSR (ABRYSVO)": {"via": "IM Profunda", "local": "Deltoide", "agulha": "25 x 0,6mm", "doses": ["24ª a 36ª sem"], "ret": 0, "tipo": "INATIVADA", "previne": "Bronquiolite e Pneumonia em bebês pelo Vírus Sincicial Respiratório."},
                "dTpa": {"via": "IM", "local": "Deltoide", "agulha": "25 x 0,6mm", "doses": ["A partir da 20ª sem"], "ret": 0, "tipo": "INATIVADA", "previne": "Difteria, Tétano e Coqueluche."},
                "HEPATITE B": {"via": "IM", "local": "Deltoide", "agulha": "25 x 0,6mm", "doses": ["Histórico"], "ret": 30, "tipo": "INATIVADA", "previne": "Hepatite B."}
            },
            "CAMPANHAS SAZONAIS": {
                "INFLUENZA": {"via": "IM", "local": "Deltoide", "agulha": "25 x 0,6mm", "doses": ["Anual"], "ret": 365, "tipo": "INATIVADA", "previne": "Gripe e complicações graves."},
                "DENGUE": {"via": "SC", "local": "Deltoide", "agulha": "13 x 0,45mm", "doses": ["1ª Dose", "2ª Dose"], "ret": 90, "tipo": "ATENUADA", "previne": "Dengue (Sorotipos 1, 2, 3 e 4)."},
                "COVID-19 XBB": {"via": "IM", "local": "Deltoide", "agulha": "25 x 0,6mm", "doses": ["Anual"], "ret": 365, "tipo": "INATIVADA", "previne": "Formas graves de COVID-19."}
            }
        }
        
        cat = st.selectbox("GRUPO:", list(DADOS_PNI.keys()))
        vax = st.radio("VACINA:", list(DADOS_PNI[cat].keys()))
        v_info = DADOS_PNI[cat][vax]

    # --- PÁGINA DE VACINAÇÃO (MOBILE FRIENDLY) ---
    st.markdown("""<div class='hero-section'><h1>SISTEMA VACINADOR 2026</h1><p>Protocolos e Prevenção</p></div>""", unsafe_allow_html=True)
    
    st.subheader(vax)
    if v_info["tipo"] == "ATENUADA": st.error(f"⚠️ Agente Vivo")
    else: st.success(f"🛡️ Inativada")

    st.markdown(f"""
        <div class="tech-card">
            <div class="tech-item"><span class="tech-label">VIA</span><span class="tech-value">{v_info['via']}</span></div>
            <div class="tech-item"><span class="tech-label">LOCAL</span><span class="tech-value">{v_info['local']}</span></div>
            <div class="tech-item"><span class="tech-label">AGULHA</span><span class="tech-value">{v_info['agulha']}</span></div>
            <div class="tech-item"><span class="tech-label">RETORNO</span><span class="tech-value">{v_info['ret']} dias</span></div>
            <div class="disease-box"><b>Previne:</b> {v_info['previne']}</div>
        </div>
    """, unsafe_allow_html=True)
    
    

    st.markdown("---")
    st.subheader("Registrar Dose")
    nome = st.text_input("NOME DO PACIENTE").upper()
    dose = st.selectbox("DOSE:", v_info["doses"])
    if st.button("REGISTRAR ATENDIMENTO"):
        if nome:
            ret = (datetime.now() + timedelta(days=v_info['ret'])).strftime("%d/%m/%Y") if v_info['ret'] > 0 else "CONCLUÍDO"
            st.warning(f"REGISTRADO! Retorno: {ret}")
            st.balloons()
        else: st.error("Informe o nome!")

st.caption("Elite Mobile 2026")
