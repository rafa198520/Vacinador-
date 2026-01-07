import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sqlite3
import hashlib
import os

# --- 1. CONFIGURAÇÕES DE PÁGINA ---
st.set_page_config(page_title="PNI Elite 2026 - Epidemiologia", layout="wide", page_icon="💉")

# --- 2. FUNÇÕES DE SEGURANÇA E BANCO DE DADOS ---
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False

def get_connection():
    return sqlite3.connect('usuarios_vax.db', check_same_thread=False)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT PRIMARY KEY, password TEXT, role TEXT)')
    c.execute('INSERT OR IGNORE INTO userstable VALUES (?,?,?)', ('rafa198520', make_hashes('002566Rafa@'), 'admin'))
    conn.commit()
    conn.close()

def add_user(username, password, role):
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute('INSERT INTO userstable(username,password,role) VALUES (?,?,?)', (username, password, role))
        conn.commit()
        conn.close()
        return True
    except: return False

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

def delete_user(username):
    conn = get_connection()
    c = conn.cursor()
    c.execute('DELETE FROM userstable WHERE username=?', (username,))
    conn.commit()
    conn.close()

# --- 3. ESTILIZAÇÃO CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
    html, body, [class*="st-"] { font-family: 'Plus Jakarta Sans', sans-serif; color: #000000 !important; }
    [data-testid="stSidebar"] { background-color: #ffffff !important; border-right: 2px solid #e2e8f0; }
    [data-testid="stSidebar"] .stMarkdown p, label, .stRadio label { color: #000000 !important; font-weight: 800 !important; font-size: 15px !important; }
    .hero-section { background: linear-gradient(135deg, #013A71 0%, #001d3d 100%); padding: 40px; border-radius: 20px; color: white; text-align: center; margin-bottom: 30px; }
    .tech-card { background: white; padding: 25px; border-radius: 16px; border: 2px solid #e2e8f0; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    .tech-item { display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #f1f5f9; align-items: center; }
    .tech-label { color: #475569; font-weight: 600; flex: 1; }
    .tech-value { color: #000000; font-weight: 800; flex: 2; text-align: right; }
    .stButton > button { width: 100%; background: #013A71; color: white !important; font-weight: 800; border-radius: 10px; height: 3.5em; }
    .disease-box { background-color: #f0f7ff; padding: 15px; border-radius: 10px; border-left: 5px solid #00B4D8; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. INICIALIZAÇÃO E LOGIN ---
init_db()

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['role'] = None

if not st.session_state['logged_in']:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col_l, col_c, col_r = st.columns([1,1.2,1])
    with col_c:
        st.markdown("<h2 style='text-align: center; color: #013A71;'>🔒 ACESSO PNI 2026</h2>", unsafe_allow_html=True)
        user = st.text_input("Usuário")
        passwd = st.text_input("Senha", type='password')
        if st.button("ACESSAR SISTEMA"):
            if login_user(user, make_hashes(passwd)):
                st.session_state['logged_in'] = True
                st.session_state['username'] = user
                st.session_state['role'] = login_user(user, make_hashes(passwd))[0][2]
                st.rerun()
            else: st.error("Acesso negado.")
else:
    # --- INTERFACE LOGADA ---
    with st.sidebar:
        st.info(f"👤 {st.session_state['username']} | {st.session_state['role'].upper()}")
        if st.button("LOGOUT"):
            st.session_state['logged_in'] = False
            st.rerun()

    if st.session_state['role'] == 'admin':
        tab_vax, tab_admin = st.tabs(["💉 VACINAÇÃO", "⚙️ USUÁRIOS"])
    else: tab_vax = st.container()

    with tab_vax:
        st.markdown("""<div class='hero-section'><h1 style='color: white; margin:0;'>SISTEMA DE IMUNIZAÇÃO PROFISSIONAL</h1><p style='color: #00B4D8; font-size: 18px; font-weight:600;'>Protocolos Clínicos e Prevenção de Doenças</p></div>""", unsafe_allow_html=True)
        
        # BANCO DE DADOS DETALHADO COM DOENÇAS
        DADOS_PNI = {
            "CALENDÁRIO INFANTIL (0-12 meses)": {
                "BCG": {"via": "ID", "local": "Deltoide Direito", "agulha": "13 x 0,45mm", "doses": ["Dose Única"], "ret": 0, "tipo": "ATENUADA", "previne": "Formas graves de Tuberculose (Miliar e Meníngea)."},
                "HEPATITE B (RN)": {"via": "IM", "local": "Vasto Lateral Dir.", "agulha": "20 x 0,55mm", "doses": ["Dose ao Nascer"], "ret": 30, "tipo": "INATIVADA", "previne": "Infecção pelo vírus da Hepatite B (transmissão vertical e sanguínea)."},
                "PENTAVALENTE": {"via": "IM", "local": "Vasto Lateral Esq.", "agulha": "20 x 0,55mm", "doses": ["1ª (2m)", "2ª (4m)", "3ª (6m)"], "ret": 60, "tipo": "INATIVADA", "previne": "Difteria, Tétano, Coqueluche, Hepatite B e Meningite/Infecções por Haemophilus influenzae tipo b."},
                "VIP (POLIO INJETÁVEL)": {"via": "IM", "local": "Vasto Lateral Dir.", "agulha": "20 x 0,55mm", "doses": ["1ª (2m)", "2ª (4m)", "3ª (6m)", "Reforço (15m)"], "ret": 60, "tipo": "INATIVADA", "previne": "Poliomielite (Paralisia Infantil) causada pelos sorotipos 1, 2 e 3."},
                "PNEUMO 10V": {"via": "IM", "local": "Vasto Lateral Dir.", "agulha": "20 x 0,55mm", "doses": ["1ª (2m)", "2ª (4m)", "Reforço (12m)"], "ret": 60, "tipo": "INATIVADA", "previne": "Pneumonia, Meningite, Otite e Sinusite causadas por 10 sorotipos de Pneumococos."},
                "ROTAVÍRUS": {"via": "VO", "local": "Boca", "agulha": "Bisnaga", "doses": ["1ª (2m)", "2ª (4m)"], "ret": 60, "tipo": "ATENUADA", "previne": "Diarreia grave e desidratação causadas por Rotavírus."},
                "MENINGOCÓCICA C": {"via": "IM", "local": "Vasto Lateral Esq.", "agulha": "20 x 0,55mm", "doses": ["1ª (3m)", "2ª (5m)", "Reforço (12m)"], "ret": 60, "tipo": "INATIVADA", "previne": "Doença Meningocócica invasiva (Meningite e Meningococcemia) pelo sorogrupo C."},
                "FEBRE AMARELA": {"via": "SC", "local": "Deltoide (Braço)", "agulha": "13 x 0,45mm", "doses": ["9 meses", "4 anos (Reforço)"], "ret": 1095, "tipo": "ATENUADA", "previne": "Infecção pelo vírus da Febre Amarela (forma urbana e silvestre)."}
            },
            "CALENDÁRIO CRIANÇAS (1-4 anos)": {
                "HEPATITE A": {"via": "IM", "local": "Deltoide/Vasto", "agulha": "20 x 0,55mm", "doses": ["Dose Única (15 meses)"], "ret": 0, "tipo": "INATIVADA", "previne": "Hepatite A (transmissão fecal-oral)."},
                "DTP (TRÍPLICE INFANTIL)": {"via": "IM", "local": "Deltoide/Vasto", "agulha": "20 x 0,55mm", "doses": ["1º Ref (15m)", "2º Ref (4 anos)"], "ret": 1095, "tipo": "INATIVADA", "previne": "Difteria, Tétano e Coqueluche (Reforço)."},
                "TRÍPLICE VIRAL (SCR)": {"via": "SC", "local": "Deltoide Esq.", "agulha": "13 x 0,45mm", "doses": ["12 meses", "15 meses"], "ret": 90, "tipo": "ATENUADA", "previne": "Sarampo, Caxumba e Rubéola."},
                "VARICELA": {"via": "SC", "local": "Deltoide Esq.", "agulha": "13 x 0,45mm", "doses": ["15 meses", "4 anos"], "ret": 1095, "tipo": "ATENUADA", "previne": "Varicela (Catapora) e complicações secundárias."}
            },
            "CALENDÁRIO ADULTO E ADOLESCENTE": {
                "HPV QUADRIVALENTE": {"via": "IM", "local": "Deltoide", "agulha": "25 x 0,6mm", "doses": ["Dose Única (9-14 anos)"], "ret": 0, "tipo": "INATIVADA", "previne": "Câncer de colo do útero, vulva, vagina, ânus e verrugas genitais (HPV 6, 11, 16, 18)."},
                "MENINGO ACWY": {"via": "IM", "local": "Deltoide", "agulha": "25 x 0,6mm", "doses": ["Dose Única (11-14 anos)"], "ret": 0, "tipo": "INATIVADA", "previne": "Meningites e doenças invasivas pelos sorogrupos A, C, W e Y."},
                "dT (DUPLA ADULTO)": {"via": "IM", "local": "Deltoide", "agulha": "25 x 0,6mm", "doses": ["Reforço a cada 10 anos"], "ret": 3650, "tipo": "INATIVADA", "previne": "Difteria e Tétano (prevenção do tétano acidental e neonatal)."},
                "PNEUMO 23V": {"via": "IM/SC", "local": "Deltoide", "agulha": "25 x 0,6mm", "doses": ["Dose Única (Idosos/Acamados)"], "ret": 1825, "tipo": "INATIVADA", "previne": "Doenças pneumocócicas sistêmicas severas em grupos de risco."}
            },
            "CALENDÁRIO GESTANTES": {
                "VSR (ABRYSVO)": {"via": "IM Profunda", "local": "Deltoide", "agulha": "25 x 0,6mm", "doses": ["24ª a 36ª semana"], "ret": 0, "tipo": "INATIVADA", "previne": "Bronquiolite e Pneumonia em bebês (via proteção transplacentária) pelo Vírus Sincicial Respiratório."},
                "dTpa (ACELULAR)": {"via": "IM", "local": "Deltoide", "agulha": "25 x 0,6mm", "doses": ["A partir da 20ª semana"], "ret": 0, "tipo": "INATIVADA", "previne": "Difteria, Tétano e Coqueluche (protege o recém-nascido da coqueluche)."},
                "HEPATITE B (GESTANTE)": {"via": "IM", "local": "Deltoide", "agulha": "25 x 0,6mm", "doses": ["Conforme histórico"], "ret": 30, "tipo": "INATIVADA", "previne": "Hepatite B e prevenção da transmissão vertical."}
            },
            "CAMPANHAS SAZONAIS": {
                "INFLUENZA (GRIPE)": {"via": "IM", "local": "Deltoide", "agulha": "25 x 0,6mm", "doses": ["Dose Anual"], "ret": 365, "tipo": "INATIVADA", "previne": "Gripe sazonal e suas complicações respiratórias graves."},
                "DENGUE (QDENGA)": {"via": "SC", "local": "Deltoide", "agulha": "13 x 0,45mm", "doses": ["1ª Dose", "2ª Dose"], "ret": 90, "tipo": "ATENUADA", "previne": "Dengue causada pelos quatro sorotipos do vírus."},
                "COVID-19 XBB": {"via": "IM", "local": "Deltoide", "agulha": "25 x 0,6mm", "doses": ["Dose Anual"], "ret": 365, "tipo": "INATIVADA", "previne": "Formas graves de COVID-19 causadas por subvariantes XBB da Ômicron."}
            }
        }

        with st.sidebar:
            cat = st.selectbox("GRUPO:", list(DADOS_PNI.keys()))
            vax = st.radio("VACINA:", list(DADOS_PNI[cat].keys()))
            v_info = DADOS_PNI[cat][vax]

        col_info, col_reg = st.columns([1.6, 1], gap="large")
        with col_info:
            st.markdown(f"### 🛡️ Protocolo Técnico: {vax}")
            if v_info["tipo"] == "ATENUADA": st.error(f"**ALERTA BIOLÓGICO:** Vacina de Agente Vivo")
            else: st.success(f"**TIPO:** Vacina Inativada")
            
            st.markdown(f"""
            <div class="tech-card">
                <h3>📖 Dados de Administração</h3>
                <div class="tech-item"><span class="tech-label">VIA</span><span class="tech-value">{v_info['via']}</span></div>
                <div class="tech-item"><span class="tech-label">LOCAL</span><span class="tech-value">{v_info['local']}</span></div>
                <div class="tech-item"><span class="tech-label">AGULHA</span><span class="tech-value">{v_info['agulha']}</span></div>
                <div class="tech-item"><span class="tech-label">RETORNO</span><span class="tech-value">{v_info['ret']} dias</span></div>
                <div class="disease-box">
                    <b>🦠 PROTEÇÃO (DOENÇAS):</b><br>{v_info['previne']}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            

        with col_reg:
            st.markdown("### ✍️ Atendimento")
            nome = st.text_input("NOME DO PACIENTE").upper()
            dose = st.selectbox("DOSE SELECIONADA", v_info["doses"])
            if st.button("REGISTRAR DOSE"):
                if nome:
                    retorno = (datetime.now() + timedelta(days=v_info['ret'])).strftime("%d/%m/%Y") if v_info['ret'] > 0 else "DOSE ÚNICA / CONCLUÍDO"
                    st.info(f"✅ **REGISTRADO**")
                    st.write(f"Paciente: **{nome}** | Retorno: **{retorno}**")
                    st.balloons()
                else: st.warning("⚠️ Informe o nome.")

    if st.session_state['role'] == 'admin':
        with tab_admin:
            st.subheader("⚙️ Gestão de Logins")
            col_a, col_b = st.columns(2)
            with col_a:
                nu = st.text_input("Novo Usuário")
                np = st.text_input("Senha", type='password')
                if st.button("SALVAR"):
                    if add_user(nu, make_hashes(np), "vacinador"):
                        st.success("Criado!"); st.rerun()
            with col_b:
                for u in view_all_users():
                    if u[0] != 'rafa198520':
                        st.write(f"👤 {u[0]}")
                        if st.button(f"Excluir {u[0]}"): delete_user(u[0]); st.rerun()

st.caption("PNI Master Elite 2026 • v10.0 • Conteúdo Epidemiológico Completo")
