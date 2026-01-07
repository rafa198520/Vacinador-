import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sqlite3
import hashlib

# --- 1. CONFIGURAÇÕES ---
st.set_page_config(page_title="PNI Master Elite 2026", layout="wide", page_icon="💉")

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

# --- 3. CSS "BLINDADO" ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
    header, [data-testid="stHeader"], [data-testid="collapsedControl"], .keyboard_double { display: none !important; }
    html, body, [class*="st-"] { font-family: 'Plus Jakarta Sans', sans-serif; color: #000000 !important; }
    .hero-section { background: linear-gradient(135deg, #013A71 0%, #001d3d 100%); padding: 25px; border-radius: 12px; color: white; text-align: center; margin-bottom: 20px; }
    .tech-card { background: white; padding: 18px; border-radius: 12px; border: 2px solid #e2e8f0; margin-bottom: 15px; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); }
    .tech-item { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #f1f5f9; }
    .tech-label { color: #475569; font-weight: 600; font-size: 13px; }
    .tech-value { color: #000000; font-weight: 800; text-align: right; font-size: 15px; }
    .stButton > button { width: 100%; background: #013A71; color: white !important; font-weight: 800; border-radius: 10px; height: 3.5rem; border: none; }
    .quiz-container { background: #ffffff; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0; margin-bottom: 15px; }
    .score-banner { text-align: center; padding: 30px; background: #f0f7ff; border-radius: 20px; border: 3px solid #013A71; margin-top: 20px; }
    .disease-box { background-color: #f0f7ff; padding: 12px; border-radius: 8px; border-left: 5px solid #00B4D8; margin-top: 10px; font-size: 14px; }
    </style>
    """, unsafe_allow_html=True)

init_db()

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.markdown("<h2 style='text-align: center; color: #013A71;'>🔒 ACESSO PORTAL</h2>", unsafe_allow_html=True)
    col_l, col_c, col_r = st.columns([0.1, 0.8, 0.1])
    with col_c:
        user = st.text_input("Usuário")
        passwd = st.text_input("Senha", type='password')
        if st.button("ACESSAR"):
            if login_user(user, make_hashes(passwd)):
                st.session_state['logged_in'] = True
                st.rerun()
            else: st.error("Incorreto.")
else:
    # --- BANCO DE DADOS INTEGRAL 2026 ---
    DADOS_PNI = {
        "CALENDÁRIO INFANTIL (0-12 meses)": {
            "BCG": {"via": "ID", "local": "Deltoide Direito", "agulha": "13 x 0,45mm", "doses": ["Dose Única"], "ret": 0, "tipo": "ATENUADA", "previne": "Formas graves de Tuberculose."},
            "HEPATITE B (RN)": {"via": "IM", "local": "Vasto Lateral Dir.", "agulha": "20 x 0,55mm", "doses": ["Ao Nascer"], "ret": 30, "tipo": "INATIVADA", "previne": "Hepatite B."},
            "PENTAVALENTE": {"via": "IM", "local": "Vasto Lateral Esq.", "agulha": "20 x 0,55mm", "doses": ["1ª (2m)", "2ª (4m)", "3ª (6m)"], "ret": 60, "tipo": "INATIVADA", "previne": "Difteria, Tétano, Coqueluche, Hepatite B e Hib."},
            "VIP (POLIO INJETÁVEL)": {"via": "IM", "local": "Vasto Lateral Dir.", "agulha": "20 x 0,55mm", "doses": ["1ª (2m)", "2ª (4m)", "3ª (6m)"], "ret": 60, "tipo": "INATIVADA", "previne": "Poliomielite."},
            "PNEUMO 10V": {"via": "IM", "local": "Vasto Lateral Dir.", "agulha": "20 x 0,55mm", "doses": ["1ª (2m)", "2ª (4m)", "Reforço (12m)"], "ret": 60, "tipo": "INATIVADA", "previne": "Pneumonias e Meningites."},
            "ROTAVÍRUS": {"via": "VO", "local": "Boca", "agulha": "Bisnaga", "doses": ["1ª (2m)", "2ª (4m)"], "ret": 60, "tipo": "ATENUADA", "previne": "Diarreia por Rotavírus."},
            "MENINGOCÓCICA C": {"via": "IM", "local": "Vasto Lateral Esq.", "agulha": "20 x 0,55mm", "doses": ["1ª (3m)", "2ª (5m)", "Reforço (12m)"], "ret": 60, "tipo": "INATIVADA", "previne": "Meningite C."},
            "FEBRE AMARELA": {"via": "SC", "local": "Deltoide", "agulha": "13 x 0,45mm", "doses": ["9 meses", "4 anos (Reforço)"], "ret": 1095, "tipo": "ATENUADA", "previne": "Febre Amarela."}
        },
        "CALENDÁRIO CRIANÇAS (1-4 anos)": {
            "HEPATITE A": {"via": "IM", "local": "Deltoide/Vasto", "agulha": "20 x 0,55mm", "doses": ["Dose Única (15m)"], "ret": 0, "tipo": "INATIVADA", "previne": "Hepatite A."},
            "DTP (TRÍPLICE INFANTIL)": {"via": "IM", "local": "Deltoide/Vasto", "agulha": "20 x 0,55mm", "doses": ["Ref (15m)", "Ref (4 anos)"], "ret": 1095, "tipo": "INATIVADA", "previne": "Difteria, Tétano e Coqueluche."},
            "TRÍPLICE VIRAL (SCR)": {"via": "SC", "local": "Deltoide Esq.", "agulha": "13 x 0,45mm", "doses": ["12 meses", "15 meses"], "ret": 90, "tipo": "ATENUADA", "previne": "Sarampo, Caxumba e Rubéola."},
            "VARICELA": {"via": "SC", "local": "Deltoide Esq.", "agulha": "13 x 0,45mm", "doses": ["15 meses", "4 anos"], "ret": 1095, "tipo": "ATENUADA", "previne": "Varicela (Catapora)."}
        },
        "ADULTO E ADOLESCENTE": {
            "HPV QUADRIVALENTE": {"via": "IM", "local": "Deltoide", "agulha": "25 x 0,6mm", "doses": ["Dose Única"], "ret": 0, "tipo": "INATIVADA", "previne": "Câncer e Verrugas genitais."},
            "MENINGO ACWY": {"via": "IM", "local": "Deltoide", "agulha": "25 x 0,6mm", "doses": ["Dose Única (11-14 anos)"], "ret": 0, "tipo": "INATIVADA", "previne": "Meningites A, C, W, Y."},
            "dT (DUPLA ADULTO)": {"via": "IM", "local": "Deltoide", "agulha": "25 x 0,6mm", "doses": ["Reforço 10 em 10 anos"], "ret": 3650, "tipo": "INATIVADA", "previne": "Difteria e Tétano."},
            "PNEUMO 23V": {"via": "IM/SC", "local": "Deltoide", "agulha": "25 x 0,6mm", "doses": ["Dose Única"], "ret": 1825, "tipo": "INATIVADA", "previne": "Doenças Pneumocócicas."}
        },
        "CALENDÁRIO GESTANTES": {
            "VSR (ABRYSVO)": {"via": "IM Profunda", "local": "Deltoide", "agulha": "25 x 0,6mm", "doses": ["Dose Única (28ª a 36ª sem)"], "ret": 0, "tipo": "INATIVADA", "previne": "Bronquiolite no RN."},
            "dTpa (ACELULAR)": {"via": "IM", "local": "Deltoide", "agulha": "25 x 0,6mm", "doses": ["A partir da 20ª sem"], "ret": 0, "tipo": "INATIVADA", "previne": "DTP no bebê."},
            "HEPATITE B": {"via": "IM", "local": "Deltoide", "agulha": "25 x 0,6mm", "doses": ["3 doses"], "ret": 30, "tipo": "INATIVADA", "previne": "Hepatite B."}
        },
        "CAMPANHAS SAZONAIS": {
            "INFLUENZA": {"via": "IM", "local": "Deltoide", "agulha": "25 x 0,6mm", "doses": ["Anual"], "ret": 365, "tipo": "INATIVADA", "previne": "Gripe."},
            "DENGUE (QDENGA)": {"via": "SC", "local": "Deltoide", "agulha": "13 x 0,45mm", "doses": ["1ª Dose", "2ª Dose"], "ret": 90, "tipo": "ATENUADA", "previne": "Dengue."},
            "COVID-19 XBB": {"via": "IM", "local": "Deltoide", "agulha": "25 x 0,6mm", "doses": ["Anual"], "ret": 365, "tipo": "INATIVADA", "previne": "COVID-19."}
        }
    }

    tab_vax, tab_quiz = st.tabs(["💉 SISTEMA VACINADOR", "🧠 SUPER QUIZ (40 QUESTÕES)"])

    with tab_vax:
        st.markdown("<div class='hero-section'><h1>SISTEMA IMUNIZAÇÃO 2026</h1></div>", unsafe_allow_html=True)
        c_sel1, c_sel2 = st.columns(2)
        with c_sel1: grupo = st.selectbox("GRUPO:", list(DADOS_PNI.keys()))
        with c_sel2: vacina_nome = st.selectbox("VACINA:", list(DADOS_PNI[grupo].keys()))
        v = DADOS_PNI[grupo][vacina_nome]
        
        col_t, col_f = st.columns([1.5, 1], gap="large")
        with col_t:
            st.markdown(f"""
                <div class="tech-card">
                    <h3>📌 {vacina_nome}</h3>
                    <div class="tech-item"><span class="tech-label">VIA</span><span class="tech-value">{v['via']}</span></div>
                    <div class="tech-item"><span class="tech-label">LOCAL</span><span class="tech-value">{v['local']}</span></div>
                    <div class="tech-item"><span class="tech-label">AGULHA</span><span class="tech-value">{v['agulha']}</span></div>
                    <div class="tech-item"><span class="tech-label">RETORNO</span><span class="tech-value">{v['ret']} dias</span></div>
                    <div class="disease-box"><b>🛡️ Previne:</b> {v['previne']}</div>
                </div>
            """, unsafe_allow_html=True)
        with col_f:
            st.subheader("📝 Registro")
            nome_p = st.text_input("NOME DO PACIENTE").upper()
            dose_p = st.selectbox("DOSE:", v["doses"])
            if st.button("REGISTRAR DOSE"):
                if nome_p: st.success(f"Registrado: {vacina_nome}")
                else: st.error("Nome obrigatório.")

    with tab_quiz:
        st.markdown("## 🧠 Desafio Master: 40 Questões Técnicas")
        perguntas = [
            ("Qual o período gestacional da VSR (Abrysvo)?", ["20-30 sem", "28-36 sem", "12-24 sem"], "28-36 sem"),
            ("Via e local da BCG?", ["SC/Esq", "ID/Dir", "IM/Coxa"], "ID/Dir"),
            ("Agulha IM em lactentes (Vasto Lateral)?", ["13x0,45", "25x0,6", "20x0,55"], "20x0,55"),
            ("Pentavalente protege contra?", ["DTP+HB+Hib", "SCR", "Dengue"], "DTP+HB+Hib"),
            ("Intervalo entre doses da Dengue?", ["30d", "60d", "90d"], "90d"),
            ("Via de administração do Rotavírus?", ["Oral", "IM", "SC"], "Oral"),
            ("A vacina Febre Amarela é...", ["Inativada", "Atenuada", "Sintética"], "Atenuada"),
            ("Temperatura ideal da Rede de Frio?", ["0 a 10°C", "+2 a +8°C", "-2 a +2°C"], "+2 a +8°C"),
            ("Via da VIP (Polio Injetável)?", ["ID", "SC", "IM"], "IM"),
            ("Cuspe no Rotavírus, o que fazer?", ["Repetir", "Não repetir", "Dar meia dose"], "Não repetir"),
            ("Idade da Meningo ACWY no PNI?", ["2 meses", "11 a 14 anos", "Idosos"], "11 a 14 anos"),
            ("Via da Tríplice Viral (SCR)?", ["IM", "SC", "ID"], "SC"),
            ("HPV é feito em qual via?", ["ID", "IM", "Oral"], "IM"),
            ("Intervalo entre 2 vacinas atenuadas?", ["15d", "30d", "60d"], "30d"),
            ("Local da Hepatite B ao nascer?", ["Vasto Lat. Dir", "Deltoide", "Glúteo"], "Vasto Lat. Dir"),
            ("Onde descartar agulhas e seringas?", ["Lixo comum", "Lixo infectante", "Descarpack"], "Descarpack"),
            ("Pneumo 10 é feita em qual via?", ["IM", "SC", "ID"], "IM"),
            ("Dose (volume) da BCG?", ["0,1 ml", "0,5 ml", "1,0 ml"], "0,1 ml"),
            ("O que significa a sigla EAPV?", ["Exame", "Evento Adverso Pós-Vacinal", "Escala"], "Evento Adverso Pós-Vacinal"),
            ("Vacinas ao recém-nascido?", ["Penta", "BCG e HepB", "Febre Amarela"], "BCG e HepB"),
            ("Esquema HPV atual?", ["Dose Única", "2 doses", "3 doses"], "Dose Única"),
            ("Músculo da Pentavalente?", ["Deltoide", "Vasto Lateral Esq", "Vasto Lateral Dir"], "Vasto Lateral Esq"),
            ("SCR protege contra?", ["Sarampo, Caxumba, Rubéola", "Sífilis", "Catapora"], "Sarampo, Caxumba, Rubéola"),
            ("Meningo C doses?", ["3 e 5 meses", "2 e 4 meses", "Nascer"], "3 e 5 meses"),
            ("Pneumo 10 doses?", ["2 e 4 meses", "3 e 5 meses", "Nascer"], "2 e 4 meses"),
            ("Reforço DTP?", ["15 meses e 4 anos", "10 anos", "6 meses"], "15 meses e 4 anos"),
            ("Hepatite A idade?", ["15 meses", "12 meses", "2 anos"], "15 meses"),
            ("Varicela PNI?", ["15 meses e 4 anos", "Nascer", "10 anos"], "15 meses e 4 anos"),
            ("Febre Amarela > 60 anos?", ["Faz", "Avaliação médica", "Nunca"], "Avaliação médica"),
            ("Gestante e Atenuada?", ["Sim", "Não", "Só no 1º mês"], "Não"),
            ("Volume Influenza?", ["0,1 ml", "0,5 ml", "1,0 ml"], "0,5 ml"),
            ("dT protege contra?", ["Difteria/Tétano", "Dengue", "Gripe"], "Difteria/Tétano"),
            ("Reforço dT?", ["Anual", "10 em 10 anos", "5 anos"], "10 em 10 anos"),
            ("Soro Antitetânico é...", ["Vacina", "Imunidade Passiva", "Atenuada"], "Imunidade Passiva"),
            ("Via Varicela?", ["IM", "SC", "ID"], "SC"),
            ("VOP substituída por?", ["VIP", "Rotavírus", "Penta"], "VIP"),
            ("Febre Amarela protege contra?", ["Urbana/Silvestre", "Dengue", "Malária"], "Urbana/Silvestre"),
            ("BCG causa supuração?", ["Não", "Sim (Natural)", "Apenas erro"], "Sim (Natural)"),
            ("Via COVID (XBB)?", ["IM", "SC", "Oral"], "IM"),
            ("Dose Hepatite B?", ["0,1 ml", "0,5 ml", "1,0 ml"], "0,5 ml")
        ]
        pontos = 0
        for i, (p, op, cor) in enumerate(perguntas):
            st.markdown(f"<div class='quiz-container'><b>{i+1}. {p}</b></div>", unsafe_allow_html=True)
            esc = st.radio("Escolha:", ["-"] + op, key=f"q{i}", label_visibility="collapsed")
            if esc == cor: pontos += 1
        if st.button("📊 FINALIZAR"):
            st.progress(pontos/40); st.success(f"Nota: {(pontos/40)*100}%")

    if st.button("🚪 SAIR"):
        st.session_state['logged_in'] = False
        st.rerun()
