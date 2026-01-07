import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sqlite3
import hashlib

# --- 1. CONFIGURAÇÕES ---
st.set_page_config(page_title="PNI Elite Especialista", layout="wide", page_icon="💉")

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

# --- 3. CSS BLINDADO ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
    header, [data-testid="stHeader"], [data-testid="collapsedControl"], .keyboard_double { display: none !important; }
    html, body, [class*="st-"] { font-family: 'Plus Jakarta Sans', sans-serif; color: #000000 !important; }
    .hero-section { background: linear-gradient(135deg, #013A71 0%, #001d3d 100%); padding: 25px; border-radius: 12px; color: white; text-align: center; margin-bottom: 20px; }
    .tech-card { background: white; padding: 18px; border-radius: 12px; border: 2px solid #e2e8f0; margin-bottom: 15px; }
    .stButton > button { width: 100%; background: #013A71; color: white !important; font-weight: 800; border-radius: 10px; height: 3.5rem; border: none; }
    .quiz-container { background: #ffffff; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0; margin-bottom: 15px; }
    .score-banner { text-align: center; padding: 30px; background: #f0f7ff; border-radius: 20px; border: 3px solid #013A71; }
    </style>
    """, unsafe_allow_html=True)

init_db()

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.markdown("<h2 style='text-align: center; color: #013A71;'>🔒 PORTAL ESPECIALISTA</h2>", unsafe_allow_html=True)
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
    tab_pni, tab_quiz = st.tabs(["💉 SISTEMA VACINADOR", "🧠 SUPER QUIZ (40 QUESTÕES)"])

    with tab_pni:
        st.markdown("<div class='hero-section'><h1>SISTEMA IMUNIZAÇÃO 2026</h1></div>", unsafe_allow_html=True)
        st.info("Consulte os protocolos ou registre doses na aba ao lado.")
        # [Seu código de dados_pni original entra aqui de forma íntegra]

    with tab_quiz:
        st.markdown("## 🧠 Desafio 40 Questões: Nível Especialista")
        
        perguntas = [
            ("Qual o período gestacional da VSR (Abrysvo)?", ["20-30 sem", "28-36 sem", "12-24 sem"], "28-36 sem"),
            ("Via e local da BCG?", ["SC/Esq", "ID/Dir", "IM/Coxa"], "ID/Dir"),
            ("Agulha IM em lactentes?", ["13x0,45", "25x0,6", "20x0,55"], "20x0,55"),
            ("Pentavalente protege contra?", ["DTP+HB+Hib", "SCR", "Dengue"], "DTP+HB+Hib"),
            ("Intervalo doses Dengue?", ["30d", "60d", "90d"], "90d"),
            ("Via do Rotavírus?", ["Oral", "IM", "SC"], "Oral"),
            ("Febre Amarela é...", ["Inativada", "Atenuada", "Sintética"], "Atenuada"),
            ("Temperatura Rede de Frio?", ["0 a 10°C", "+2 a +8°C", "-2 a +2°C"], "+2 a +8°C"),
            ("Via da VIP?", ["ID", "SC", "IM"], "IM"),
            ("Cuspe no Rotavírus?", ["Repetir", "Não repetir", "Dar meia dose"], "Não repetir"),
            ("Meningo ACWY idade?", ["2 meses", "11 a 14 anos", "Idosos"], "11 a 14 anos"),
            ("Via da SCR?", ["IM", "SC", "ID"], "SC"),
            ("Via do HPV?", ["ID", "IM", "Oral"], "IM"),
            ("Intervalo entre 2 atenuadas?", ["15d", "30d", "60d"], "30d"),
            ("Hepatite B ao nascer?", ["Vasto Lat. Dir", "Deltoide", "Glúteo"], "Vasto Lat. Dir"),
            ("Onde descartar agulhas?", ["Lixo comum", "Lixo infectante", "Descarpack"], "Descarpack"),
            ("Pneumo 10 é feita em qual via?", ["IM", "SC", "ID"], "IM"),
            ("Dose da BCG?", ["0,1 ml", "0,5 ml", "1,0 ml"], "0,1 ml"),
            ("O que é EAPV?", ["Exame de sangue", "Evento Adverso Pós-Vacinal", "Escala de dor"], "Evento Adverso Pós-Vacinal"),
            ("Vacina para recém-nascido?", ["Penta", "BCG e HepB", "Febre Amarela"], "BCG e HepB"),
            ("Intervalo entre doses de HPV?", ["Dose Única", "2 doses", "3 doses"], "Dose Única"),
            ("Local da Pentavalente?", ["Deltoide", "Vasto Lateral Esq", "Vasto Lateral Dir"], "Vasto Lateral Esq"),
            ("SCR protege contra?", ["Sarampo, Caxumba, Rubéola", "Sífilis", "Catapora"], "Sarampo, Caxumba, Rubéola"),
            ("Meningo C é feita aos?", ["3 e 5 meses", "2 e 4 meses", "Ao nascer"], "3 e 5 meses"),
            ("Pneumo 10 é feita aos?", ["2 e 4 meses", "3 e 5 meses", "Ao nascer"], "2 e 4 meses"),
            ("Reforço da DTP idade?", ["15 meses e 4 anos", "10 anos", "6 meses"], "15 meses e 4 anos"),
            ("Hepatite A idade (PNI)?", ["15 meses", "12 meses", "2 anos"], "15 meses"),
            ("Varicela idade (PNI)?", ["15 meses e 4 anos", "Ao nascer", "10 anos"], "15 meses e 4 anos"),
            ("Febre Amarela em idoso?", ["Sempre faz", "Avaliação médica", "Nunca faz"], "Avaliação médica"),
            ("Gestante pode fazer atenuada?", ["Sim", "Não (Contraindicado)", "Apenas no 1º mês"], "Não (Contraindicado)"),
            ("Dose da Influenza no PNI?", ["0,1 ml", "0,5 ml", "1,0 ml"], "0,5 ml"),
            ("A vacina dT protege contra?", ["Difteria e Tétano", "Dengue", "Diarreia"], "Difteria e Tétano"),
            ("Intervalo dT?", ["Anual", "10 em 10 anos", "Única"], "10 em 10 anos"),
            ("Soro Antitetânico é...", ["Vacina", "Imunidade Passiva", "Atenuada"], "Imunidade Passiva"),
            ("Via da Varicela?", ["IM", "SC", "ID"], "SC"),
            ("VOP (gotinha) ainda existe no PNI 2026?", ["Sim", "Não (Substituída por VIP)", "Apenas em campanhas"], "Não (Substituída por VIP)"),
            ("Febre Amarela previne contra?", ["Forma urbana e silvestre", "Dengue", "Malária"], "Forma urbana e silvestre"),
            ("Qual vacina causa nódulo e supuração?", ["Penta", "BCG", "Influenza"], "BCG"),
            ("Via da COVID-19 XBB?", ["IM", "SC", "Oral"], "IM"),
            ("Dose da Hepatite B em ml?", ["0,1 ml", "0,5 ml", "1,0 ml"], "0,5 ml")
        ]

        pontos = 0
        for i, (p, op, cor) in enumerate(perguntas):
            st.markdown(f"<div class='quiz-container'><b>{i+1}. {p}</b></div>", unsafe_allow_html=True)
            esc = st.radio("Selecione:", ["-"] + op, key=f"q{i}", label_visibility="collapsed")
            if esc == cor: pontos += 1

        if st.button("📊 FINALIZAR DESAFIO 40Q"):
            perc = (pontos / 40) * 100
            st.progress(pontos / 40)
            st.markdown(f"<div class='score-banner'><h2>Nota: {perc:.1f}%</h2><h3>Acertos: {pontos} de 40</h3></div>", unsafe_allow_html=True)
            if pontos == 40: st.balloons(); st.snow(); st.success("VOCÊ É UM ESPECIALISTA MASTER!")
            elif pontos >= 30: st.balloons(); st.warning("ÓTIMO DESEMPENHO!")
            else: st.error("Continue estudando o Manual de Normas.")

    if st.button("🚪 LOGOUT"):
        st.session_state['logged_in'] = False
        st.rerun()
