import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sqlite3
import hashlib
import os

# --- 1. CONFIGURAÇÕES DE PÁGINA ---
st.set_page_config(page_title="PNI Elite 2026 - Acesso Restrito", layout="wide", page_icon="💉")

# --- 2. FUNÇÕES DE SEGURANÇA E BANCO DE DADOS ---
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False

# Criar banco de dados de usuários
conn = sqlite3.connect('usuarios_vax.db', check_same_thread=False)
c = conn.cursor()

def init_db():
    c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT PRIMARY KEY, password TEXT, role TEXT)')
    # Usuário Mestre: admin / Senha: admin123 (MUDE DEPOIS)
    c.execute('INSERT OR IGNORE INTO userstable VALUES (?,?,?)', ('admin', make_hashes('admin123'), 'admin'))
    conn.commit()

def add_user(username, password, role):
    try:
        c.execute('INSERT INTO userstable(username,password,role) VALUES (?,?,?)', (username, password, role))
        conn.commit()
        return True
    except: return False

def login_user(username, password):
    c.execute('SELECT * FROM userstable WHERE username =? AND password =?', (username, password))
    return c.fetchall()

def view_all_users():
    c.execute('SELECT username, role FROM userstable')
    return c.fetchall()

def delete_user(username):
    c.execute('DELETE FROM userstable WHERE username=?', (username,))
    conn.commit()

# --- 3. ESTILIZAÇÃO CSS (PROFISSIONAL) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
    html, body, [class*="st-"] { font-family: 'Plus Jakarta Sans', sans-serif; color: #000000 !important; }
    [data-testid="stSidebar"] { background-color: #ffffff !important; border-right: 2px solid #e2e8f0; }
    [data-testid="stSidebar"] .stMarkdown p, label, .stRadio label { color: #000000 !important; font-weight: 800 !important; font-size: 15px !important; }
    .hero-section { background: linear-gradient(135deg, #013A71 0%, #001d3d 100%); padding: 40px; border-radius: 20px; color: white; text-align: center; margin-bottom: 30px; }
    .tech-card { background: white; padding: 25px; border-radius: 16px; border: 2px solid #e2e8f0; margin-bottom: 20px; }
    .tech-item { display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #f1f5f9; }
    .tech-label { color: #475569; font-weight: 600; }
    .tech-value { color: #000000; font-weight: 800; }
    .stButton > button { width: 100%; background: #013A71; color: white !important; font-weight: 800; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. LÓGICA DE LOGIN ---
init_db()

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['role'] = None

if not st.session_state['logged_in']:
    st.markdown("<h2 style='text-align: center; color: #013A71;'>🔒 ACESSO AO SISTEMA VACINADOR</h2>", unsafe_allow_html=True)
    with st.container():
        col_l, col_c, col_r = st.columns([1,1,1])
        with col_c:
            user = st.text_input("Usuário")
            passwd = st.text_input("Senha", type='password')
            if st.button("ENTRAR NO SISTEMA"):
                hashed_pswd = make_hashes(passwd)
                result = login_user(user, check_hashes(passwd, hashed_pswd))
                if result:
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = user
                    st.session_state['role'] = result[0][2]
                    st.rerun()
                else:
                    st.error("Usuário ou Senha inválidos")
else:
    # --- CABEÇALHO DO SISTEMA LOGADO ---
    st.sidebar.info(f"Usuário: {st.session_state['username']} ({st.session_state['role']})")
    if st.sidebar.button("LOGOUT / SAIR"):
        st.session_state['logged_in'] = False
        st.rerun()

    # --- PÁGINAS ---
    if st.session_state['role'] == 'admin':
        tab_vax, tab_admin = st.tabs(["💉 SISTEMA VACINADOR", "⚙️ CONTROLE DE ACESSOS"])
    else:
        tab_vax = st.container() # Vacinador comum só vê a vacina

    with tab_vax:
        # --- O SEU CÓDIGO DAS VACINAS (INTEGRO) ---
        st.markdown("""<div class='hero-section'><h1 style='color: white; margin:0;'>SISTEMA DE IMUNIZAÇÃO PROFISSIONAL 2026</h1><p style='color: #00B4D8; font-size: 18px; font-weight:600;'>Controle de Protocolos e Aprazamento</p></div>""", unsafe_allow_html=True)
        
        DADOS_PNI = {
            "CALENDÁRIO INFANTIL (0-12 meses)": {
                "BCG": {"via": "ID", "local": "Deltoide Direito", "agulha": "13 x 0,45mm", "doses": ["Dose Única"], "ret": 0, "tipo": "ATENUADA"},
                "HEPATITE B (RN)": {"via": "IM", "local": "Vasto Lateral Dir.", "agulha": "20 x 0,55mm", "doses": ["Dose ao Nascer"], "ret": 30, "tipo": "INATIVADA"},
                "PENTAVALENTE": {"via": "IM", "local": "Vasto Lateral Esq.", "agulha": "20 x 0,55mm", "doses": ["1ª (2m)", "2ª (4m)", "3ª (6m)"], "ret": 60, "tipo": "INATIVADA"},
                "VIP (POLIO INJETÁVEL)": {"via": "IM", "local": "Vasto Lateral Dir.", "agulha": "20 x 0,55mm", "doses": ["1ª (2m)", "2ª (4m)", "3ª (6m)", "Reforço (15m)"], "ret": 60, "tipo": "INATIVADA"},
                "PNEUMO 10V": {"via": "IM", "local": "Vasto Lateral Dir.", "agulha": "20 x 0,55mm", "doses": ["1ª (2m)", "2ª (4m)", "Reforço (12m)"], "ret": 60, "tipo": "INATIVADA"},
                "ROTAVÍRUS": {"via": "VO", "local": "Boca", "agulha": "Bisnaga", "doses": ["1ª (2m)", "2ª (4m)"], "ret": 60, "tipo": "ATENUADA"},
                "MENINGOCÓCICA C": {"via": "IM", "local": "Vasto Lateral Esq.", "agulha": "20 x 0,55mm", "doses": ["1ª (3m)", "2ª (5m)", "Reforço (12m)"], "ret": 60, "tipo": "INATIVADA"},
                "FEBRE AMARELA": {"via": "SC", "local": "Deltoide (Braço)", "agulha": "13 x 0,45mm", "doses": ["9 meses", "4 anos (Reforço)"], "ret": 1095, "tipo": "ATENUADA"}
            },
            "CALENDÁRIO CRIANÇAS (1-4 anos)": {
                "HEPATITE A": {"via": "IM", "local": "Deltoide/Vasto", "agulha": "20 x 0,55mm", "doses": ["Dose Única (15 meses)"], "ret": 0, "tipo": "INATIVADA"},
                "DTP (TRÍPLICE INFANTIL)": {"via": "IM", "local": "Deltoide/Vasto", "agulha": "20 x 0,55mm", "doses": ["1º Ref (15m)", "2º Ref (4 anos)"], "ret": 1095, "tipo": "INATIVADA"},
                "TRÍPLICE VIRAL (SCR)": {"via": "SC", "local": "Deltoide Esq.", "agulha": "13 x 0,45mm", "doses": ["12 meses", "15 meses"], "ret": 90, "tipo": "ATENUADA"},
                "VARICELA": {"via": "SC", "local": "Deltoide Esq.", "agulha": "13 x 0,45mm", "doses": ["15 meses", "4 anos"], "ret": 1095, "tipo": "ATENUADA"}
            },
            "CALENDÁRIO ADULTO E ADOLESCENTE": {
                "HPV QUADRIVALENTE": {"via": "IM", "local": "Deltoide", "agulha": "25 x 0,6mm", "doses": ["Dose Única (9-14 anos)"], "ret": 0, "tipo": "INATIVADA"},
                "MENINGO ACWY": {"via": "IM", "local": "Deltoide", "agulha": "25 x 0,6mm", "doses": ["Dose Única (11-14 anos)"], "ret": 0, "tipo": "INATIVADA"},
                "dT (DUPLA ADULTO)": {"via": "IM", "local": "Deltoide", "agulha": "25 x 0,6mm", "doses": ["Reforço a cada 10 anos"], "ret": 3650, "tipo": "INATIVADA"},
                "PNEUMO 23V": {"via": "IM/SC", "local": "Deltoide", "agulha": "25 x 0,6mm", "doses": ["Dose Única (Idosos/Acamados)"], "ret": 1825, "tipo": "INATIVADA"}
            },
            "CALENDÁRIO GESTANTES": {
                "VSR (ABRYSVO)": {"via": "IM Profunda", "local": "Deltoide", "agulha": "25 x 0,6mm", "doses": ["24ª a 36ª semana"], "ret": 0, "tipo": "INATIVADA"},
                "dTpa (ACELULAR)": {"via": "IM", "local": "Deltoide", "agulha": "25 x 0,6mm", "doses": ["A partir da 20ª semana"], "ret": 0, "tipo": "INATIVADA"},
                "HEPATITE B (GESTANTE)": {"via": "IM", "local": "Deltoide", "agulha": "25 x 0,6mm", "doses": ["Conforme histórico"], "ret": 30, "tipo": "INATIVADA"}
            },
            "CAMPANHAS SAZONAIS": {
                "INFLUENZA (GRIPE)": {"via": "IM", "local": "Deltoide", "agulha": "25 x 0,6mm", "doses": ["Dose Anual"], "ret": 365, "tipo": "INATIVADA"},
                "DENGUE (QDENGA)": {"via": "SC", "local": "Deltoide", "agulha": "13 x 0,45mm", "doses": ["1ª Dose", "2ª Dose"], "ret": 90, "tipo": "ATENUADA"},
                "COVID-19 XBB": {"via": "IM", "local": "Deltoide", "agulha": "25 x 0,6mm", "doses": ["Dose Anual"], "ret": 365, "tipo": "INATIVADA"}
            }
        }

        # Sidebar interna
        cat = st.sidebar.selectbox("GRUPO:", list(DADOS_PNI.keys()))
        vax = st.sidebar.radio("VACINA:", list(DADOS_PNI[cat].keys()))
        v_info = DADOS_PNI[cat][vax]

        col_info, col_reg = st.columns([1.5, 1], gap="large")
        with col_info:
            st.markdown(f"### 🛡️ Protocolo: {vax}")
            if v_info["tipo"] == "ATENUADA": st.error(f"**ATENÇÃO:** {v_info['tipo']} (Vivo)")
            else: st.success(f"**TIPO:** {v_info['tipo']} (Inativada)")
            st.markdown(f"""<div class="tech-card"><div class="tech-item"><span class="tech-label">VIA</span><span class="tech-value">{v_info['via']}</span></div><div class="tech-item"><span class="tech-label">LOCAL</span><span class="tech-value">{v_info['local']}</span></div><div class="tech-item"><span class="tech-label">AGULHA</span><span class="tech-value">{v_info['agulha']}</span></div><div class="tech-item" style="border:none;"><span class="tech-label">RETORNO</span><span class="tech-value">{v_info['ret']} dias</span></div></div>""", unsafe_allow_html=True)
        with col_reg:
            st.markdown("### ✍️ Atendimento")
            nome = st.text_input("NOME DO PACIENTE").upper()
            dose = st.selectbox("DOSE SELECIONADA", v_info["doses"])
            if st.button("REGISTRAR ATENDIMENTO"):
                if nome:
                    retorno = (datetime.now() + timedelta(days=v_info['ret'])).strftime("%d/%m/%Y") if v_info['ret'] > 0 else "DOSE ÚNICA"
                    st.info(f"✅ **REGISTRADO COM SUCESSO**")
                    st.write(f"Paciente: **{nome}** | Retorno: **{retorno}**")
                else: st.warning("⚠️ Digite o nome.")

    # --- PÁGINA DE ADMINISTRAÇÃO (APENAS ADMIN) ---
    if st.session_state['role'] == 'admin':
        with tab_admin:
            st.subheader("⚙️ Gestão de Usuários Remotos")
            col_add, col_list = st.columns(2)
            with col_add:
                st.markdown("### Criar Novo Acesso")
                new_user = st.text_input("Novo Usuário")
                new_pass = st.text_input("Senha Temporária", type='password')
                new_role = st.selectbox("Perfil", ["vacinador", "admin"])
                if st.button("ADICIONAR USUÁRIO"):
                    if add_user(new_user, make_hashes(new_pass), new_role):
                        st.success(f"Usuário {new_user} criado!")
                        st.rerun()
                    else: st.error("Erro ou usuário já existe.")
            with col_list:
                st.markdown("### Usuários Ativos")
                users = view_all_users()
                for u in users:
                    col_u, col_d = st.columns([3,1])
                    col_u.write(f"👤 {u[0]} [{u[1]}]")
                    if u[0] != 'admin':
                        if col_d.button("Excluir", key=u[0]):
                            delete_user(u[0])
                            st.rerun()

st.caption("Sistema Master Elite 2026 • Controle de Acesso Seguro Ativado")
