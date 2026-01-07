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

# --- 3. CSS "BLINDADO" (PC/CELULAR) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
    header, [data-testid="stHeader"], [data-testid="collapsedControl"], .keyboard_double { display: none !important; }
    html, body, [class*="st-"] { font-family: 'Plus Jakarta Sans', sans-serif; color: #000000 !important; }
    .hero-section { background: linear-gradient(135deg, #013A71 0%, #001d3d 100%); padding: 25px; border-radius: 12px; color: white; text-align: center; margin-bottom: 20px; }
    .tech-card { background: white; padding: 18px; border-radius: 12px; border: 2px solid #e2e8f0; margin-bottom: 15px; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); }
    .tech-item { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #f1f5f9; }
    .tech-label { color: #64748b; font-weight: 600; font-size: 13px; }
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
    # --- BANCO DE DADOS RESTAURADO ---
    DADOS_PNI = {
        "GESTANTES": {
            "VSR (ABRYSVO)": {"via": "IM Profunda", "local": "Deltoide", "agulha": "25x0,6mm", "doses": ["Dose Única (28ª a 36ª sem)"], "ret": 0, "previne": "Bronquiolite e Pneumonia (VSR) no recém-nascido."},
            "dTpa (Acelular)": {"via": "IM", "local": "Deltoide", "agulha": "25x0,6mm", "doses": ["A partir da 20ª sem"], "ret": 0, "previne": "Difteria, Tétano e Coqueluche."},
            "Hepatite B": {"via": "IM", "local": "Deltoide", "agulha": "25x0,6mm", "doses": ["1ª Dose", "2ª Dose", "3ª Dose"], "ret": 30, "previne": "Hepatite B e transmissão vertical."}
        },
        "INFANTIL (0-12m)": {
            "BCG": {"via": "ID", "local": "Deltoide Dir.", "agulha": "13x0,45mm", "doses": ["Dose Única"], "ret": 0, "previne": "Tuberculose Miliar e Meníngea."},
            "PENTAVALENTE": {"via": "IM", "local": "Vasto Lat. Esq.", "agulha": "20x0,55mm", "doses": ["1ª (2m)", "2ª (4m)", "3ª (6m)"], "ret": 60, "previne": "Difteria, Tétano, Coqueluche, Hep B e Hib."},
            "VIP (Pólio)": {"via": "IM", "local": "Vasto Lat. Dir.", "agulha": "20x0,55mm", "doses": ["1ª (2m)", "2ª (4m)", "3ª (6m)"], "ret": 60, "previne": "Paralisia Infantil (Poliomielite)."},
            "ROTAVÍRUS": {"via": "VO", "local": "Boca", "agulha": "Bisnaga", "doses": ["1ª (2m)", "2ª (4m)"], "ret": 60, "previne": "Diarreia grave por Rotavírus."}
        },
        "ADULTO / IDOSO": {
            "HPV": {"via": "IM", "local": "Deltoide", "agulha": "25x0,6mm", "doses": ["Dose Única"], "ret": 0, "previne": "Câncer de colo do útero e verrugas."},
            "DENGUE (Qdenga)": {"via": "SC", "local": "Deltoide", "agulha": "13x0,45mm", "doses": ["1ª Dose", "2ª Dose"], "ret": 90, "previne": "Dengue (Sorotipos 1, 2, 3 e 4)."},
            "INFLUENZA": {"via": "IM", "local": "Deltoide", "agulha": "25x0,6mm", "doses": ["Anual"], "ret": 365, "previne": "Gripe e complicações respiratórias."}
        }
    }

    tab_pni, tab_quiz = st.tabs(["💉 SISTEMA VACINADOR", "🧠 SUPER QUIZ (40 QUESTÕES)"])

    with tab_pni:
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
                    <div class="tech-item"><span class="tech-label">APRAZAMENTO</span><span class="tech-value">{v['ret']} dias</span></div>
                    <div class="disease-box"><b>🛡️ Previne:</b> {v['previne']}</div>
                </div>
            """, unsafe_allow_html=True)
        with col_f:
            st.subheader("📝 Registro")
            nome_p = st.text_input("NOME DO PACIENTE").upper()
            lote_p = st.text_input("LOTE/VALIDADE")
            dose_p = st.selectbox("DOSE:", v["doses"])
            if st.button("REGISTRAR ATENDIMENTO"):
                if nome_p: st.success(f"Registrado: {vacina_nome} para {nome_p}")
                else: st.error("Informe o nome.")

    with tab_quiz:
        st.markdown("## 🧠 Desafio Master: 40 Questões Técnicas")
        st.write("Responda com atenção. Use a opção '-' para limpar a seleção.")

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
            ("Qual a dose (volume) da BCG?", ["0,1 ml", "0,5 ml", "1,0 ml"], "0,1 ml"),
            ("O que significa a sigla EAPV?", ["Exame de sangue", "Evento Adverso Pós-Vacinal", "Escala de dor"], "Evento Adverso Pós-Vacinal"),
            ("Vacinas obrigatórias ao recém-nascido?", ["Penta", "BCG e HepB", "Febre Amarela"], "BCG e HepB"),
            ("Novo esquema HPV 2024/2026?", ["Dose Única", "2 doses", "3 doses"], "Dose Única"),
            ("Músculo local da Pentavalente?", ["Deltoide", "Vasto Lateral Esq", "Vasto Lateral Dir"], "Vasto Lateral Esq"),
            ("SCR protege contra?", ["Sarampo, Caxumba, Rubéola", "Sífilis", "Catapora"], "Sarampo, Caxumba, Rubéola"),
            ("Meningo C é feita aos?", ["3 e 5 meses", "2 e 4 meses", "Ao nascer"], "3 e 5 meses"),
            ("Pneumo 10 é feita aos?", ["2 e 4 meses", "3 e 5 meses", "Ao nascer"], "2 e 4 meses"),
            ("Reforço da DTP (Tríplice Infantil)?", ["15 meses e 4 anos", "10 anos", "6 meses"], "15 meses e 4 anos"),
            ("Idade da Hepatite A (PNI)?", ["15 meses", "12 meses", "2 anos"], "15 meses"),
            ("Idade da Varicela no PNI?", ["15 meses e 4 anos", "Ao nascer", "10 anos"], "15 meses e 4 anos"),
            ("Febre Amarela em idoso (>60 anos)?", ["Sempre faz", "Avaliação médica", "Nunca faz"], "Avaliação médica"),
            ("Gestante pode fazer vacina atenuada?", ["Sim", "Não (Contraindicado)", "Apenas no 1º mês"], "Não (Contraindicado)"),
            ("Volume da dose da Influenza?", ["0,1 ml", "0,5 ml", "1,0 ml"], "0,5 ml"),
            ("A vacina dT (Dupla Adulto) protege contra?", ["Difteria e Tétano", "Dengue", "Diarreia"], "Difteria e Tétano"),
            ("Validade do reforço da dT?", ["Anual", "10 em 10 anos", "Única"], "10 em 10 anos"),
            ("Soro Antitetânico é considerado...", ["Vacina", "Imunidade Passiva", "Atenuada"], "Imunidade Passiva"),
            ("Via da vacina Varicela?", ["IM", "SC", "ID"], "SC"),
            ("VOP (gotinha) foi substituída por?", ["VIP (injetável)", "Rotavírus", "Penta"], "VIP (injetável)"),
            ("Febre Amarela protege contra?", ["Formas urbana e silvestre", "Dengue", "Malária"], "Formas urbana e silvestre"),
            ("Vacina que causa nódulo e supuração natural?", ["Penta", "BCG", "Influenza"], "BCG"),
            ("Via da vacina COVID-19 (XBB)?", ["IM", "SC", "Oral"], "IM"),
            ("Dose padrão da Hepatite B (ml)?", ["0,1 ml", "0,5 ml", "1,0 ml"], "0,5 ml")
        ]

        pontos = 0
        for i, (p, op, cor) in enumerate(perguntas):
            st.markdown(f"<div class='quiz-container'><b>{i+1}. {p}</b></div>", unsafe_allow_html=True)
            esc = st.radio("Selecione:", ["-"] + op, key=f"q{i}", label_visibility="collapsed")
            if esc == cor: pontos += 1

        st.divider()
        if st.button("📊 FINALIZAR DESAFIO 40Q"):
            perc = (pontos / 40) * 100
            st.progress(pontos / 40)
            st.markdown(f"<div class='score-banner'><h2>Nota Final: {perc:.1f}%</h2><h3>Acertos: {pontos} de 40</h3></div>", unsafe_allow_html=True)
            if pontos == 40: 
                st.balloons(); st.snow(); st.success("🏆 EXCELENTE! Você é um Vacinador Especialista!")
            elif pontos >= 30: 
                st.balloons(); st.warning("👏 ÓTIMO DESEMPENHO! Continue assim.")
            else: 
                st.error("📚 É PRECISO REVISAR. Consulte o manual da Rede de Frio e do PNI.")

    st.markdown("<br>")
    if st.button("🚪 SAIR DO SISTEMA"):
        st.session_state['logged_in'] = False
        st.rerun()

st.caption("PNI Master Elite 2026 - v16.0 (Integral)")
