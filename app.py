import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sqlite3
import hashlib
import os

# --- 1. CONFIGURAÇÕES DE PÁGINA ---
st.set_page_config(page_title="PNI Elite 2026 - Restrito", layout="wide", page_icon="💉")

# --- 2. FUNÇÕES DE SEGURANÇA E BANCO DE DADOS ---
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False

# Gerenciador de conexão segura
def get_connection():
    return sqlite3.connect('usuarios_vax.db', check_same_thread=False)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT PRIMARY KEY, password TEXT, role TEXT)')
    # Usuário Mestre Atualizado conforme sua solicitação
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

# --- 3. ESTILIZAÇÃO CSS (PROFISSIONAL) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
    html, body, [class*="st-"] { font-family: 'Plus Jakarta Sans', sans-serif; color: #000000 !important; }
    [data-testid="stSidebar"] { background-color: #ffffff !important; border-right: 2px solid #e2e8f0; }
    [data-testid="stSidebar"] .stMarkdown p, label, .stRadio label { color: #000000 !important; font-weight: 800 !important; font-size: 15px !important; }
    .hero-section { background: linear-gradient(135deg, #013A71 0%, #001d3d 100%); padding: 40px; border-radius: 20px; color: white; text-align: center; margin-bottom: 30px; }
    .tech-card { background: white; padding: 25px; border-radius: 16px; border: 2px solid #e2e8f0; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    .tech-item { display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #f1f5f9; }
    .tech-label { color: #475569; font-weight: 600; }
    .tech-value { color: #000000; font-weight: 800; }
    .stButton > button { width: 100%; background: #013A71; color: white !important; font-weight: 800; border-radius: 10px; border: none; height: 3em; }
    .stButton > button:hover { background: #00B4D8; border: none; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. LÓGICA DE LOGIN ---
init_db()

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['role'] = None
    st.session_state['username'] = None

if not st.session_state['logged_in']:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col_l, col_c, col_r = st.columns([1,1.2,1])
    with col_c:
        st.markdown("""
            <div style="background-color: white; padding: 30px; border-radius: 20px; border: 1px solid #e2e8f0; box-shadow: 0 10px 25px rgba(0,0,0,0.1);">
                <h2 style='text-align: center; color: #013A71; margin-bottom: 20px;'>🔒 LOGIN SISTEMA</h2>
            </div>
        """, unsafe_allow_html=True)
        user = st.text_input("Usuário", placeholder="Digite seu usuário")
        passwd = st.text_input("Senha", type='password', placeholder="Digite sua senha")
        if st.button("ACESSAR PORTAL"):
            hashed_pswd = make_hashes(passwd)
            result = login_user(user, hashed_pswd)
            if result:
                st.session_state['logged_in'] = True
                st.session_state['username'] = user
                st.session_state['role'] = result[0][2]
                st.rerun()
            else:
                st.error("Credenciais incorretas. Tente novamente.")
else:
    # --- CABEÇALHO DO SISTEMA LOGADO ---
    with st.sidebar:
        st.markdown(f"### 👤 Conectado")
        st.info(f"**Usuário:** {st.session_state['username']}\n\n**Perfil:** {st.session_state['role'].upper()}")
        if st.button("SAIR DO SISTEMA"):
            st.session_state['logged_in'] = False
            st.rerun()
        st.divider()

    # --- PÁGINAS ---
    if st.session_state['role'] == 'admin':
        tab_vax, tab_admin = st.tabs(["💉 SISTEMA VACINADOR", "⚙️ GESTÃO DE ACESSOS"])
    else:
        tab_vax = st.container()

    with tab_vax:
        st.markdown("""<div class='hero-section'><h1 style='color: white; margin:0;'>SISTEMA DE IMUNIZAÇÃO PROFISSIONAL 2026</h1><p style='color: #00B4D8; font-size: 18px; font-weight:600;'>Protocolos Oficiais e Aprazamento Automatizado</p></div>""", unsafe_allow_html=True)
        
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

        with st.sidebar:
            cat = st.selectbox("GRUPO DE ATENDIMENTO:", list(DADOS_PNI.keys()))
            vax = st.radio("SELECIONE A VACINA:", list(DADOS_PNI[cat].keys()))
            v_info = DADOS_PNI[cat][vax]

        col_info, col_reg = st.columns([1.5, 1], gap="large")
        with col_info:
            st.markdown(f"### 🛡️ Protocolo: {vax}")
            if v_info["tipo"] == "ATENUADA": st.error(f"**ATENÇÃO:** Vacina de Agente VIVO ({v_info['tipo']})")
            else: st.success(f"**TIPO:** Vacina Inativada")
            st.markdown(f"""<div class="tech-card"><h3>📋 Informações de Aplicação</h3><div class="tech-item"><span class="tech-label">VIA</span><span class="tech-value">{v_info['via']}</span></div><div class="tech-item"><span class="tech-label">LOCAL</span><span class="tech-value">{v_info['local']}</span></div><div class="tech-item"><span class="tech-label">AGULHA</span><span class="tech-value">{v_info['agulha']}</span></div><div class="tech-item" style="border:none;"><span class="tech-label">APRAZAMENTO</span><span class="tech-value">{v_info['ret']} dias</span></div></div>""", unsafe_allow_html=True)
            
            

        with col_reg:
            st.markdown("### ✍️ Registrar Dose")
            nome = st.text_input("NOME DO PACIENTE", placeholder="Ex: JOÃO DA SILVA").upper()
            dose = st.selectbox("DOSE APLICADA:", v_info["doses"])
            if st.button("CONFIRMAR REGISTRO"):
                if nome:
                    retorno = (datetime.now() + timedelta(days=v_info['ret'])).strftime("%d/%m/%Y") if v_info['ret'] > 0 else "ESQUEMA CONCLUÍDO / DOSE ÚNICA"
                    st.info(f"✅ **REGISTRO EFETUADO**")
                    st.markdown(f"""
                    **Paciente:** {nome}  
                    **Dose:** {dose}  
                    **Data de Retorno:** `{retorno}`
                    """)
                    st.balloons()
                else: st.warning("⚠️ O nome do paciente é obrigatório.")

    # --- PÁGINA DE ADMINISTRAÇÃO ---
    if st.session_state['role'] == 'admin':
        with tab_admin:
            st.markdown("## ⚙️ Painel de Controle de Acesso")
            col_add, col_list = st.columns(2, gap="large")
            with col_add:
                st.markdown("### 👤 Novo Usuário")
                new_user = st.text_input("Nome de Usuário", key="new_u")
                new_pass = st.text_input("Senha", type='password', key="new_p")
                new_role = st.selectbox("Nível de Acesso", ["vacinador", "admin"])
                if st.button("SALVAR NOVO ACESSO"):
                    if new_user and new_pass:
                        if add_user(new_user, make_hashes(new_pass), new_role):
                            st.success(f"Usuário '{new_user}' adicionado com sucesso!")
                            st.rerun()
                        else: st.error("Erro: Usuário já cadastrado ou falha no banco.")
                    else: st.warning("Preencha todos os campos.")
            
            with col_list:
                st.markdown("### 📋 Usuários Ativos")
                users = view_all_users()
                for u in users:
                    col_u, col_d = st.columns([3,1])
                    col_u.write(f"**{u[0]}** ({u[1].upper()})")
                    if u[0] != 'rafa198520': # Protege o admin principal
                        if col_d.button("Remover", key=f"del_{u[0]}"):
                            delete_user(u[0])
                            st.rerun()

st.divider()
st.caption("Sistema Master Elite 2026 • v9.0 • Camada de Segurança SQLite Ativa")
