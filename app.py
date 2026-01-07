import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sqlite3
import hashlib

# --- 1. CONFIGURAÇÕES ---
st.set_page_config(page_title="SISTEMA VACINADOR 2026", layout="wide", page_icon="💉")

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

# --- 3. CSS UNIVERSAL (PC/CELULAR + SEM ERROS VISUAIS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
    
    header, [data-testid="stHeader"], [data-testid="collapsedControl"], .keyboard_double {
        display: none !important;
    }

    html, body, [class*="st-"] { font-family: 'Plus Jakarta Sans', sans-serif; color: #000000 !important; }
    .main .block-container { padding-top: 15px !important; }

    .hero-section { 
        background: linear-gradient(135deg, #013A71 0%, #001d3d 100%); 
        padding: 25px; border-radius: 12px; color: white; text-align: center; margin-bottom: 20px; 
    }

    .tech-card { 
        background: white; padding: 18px; border-radius: 12px; border: 2px solid #e2e8f0; margin-bottom: 15px; 
    }
    .tech-item { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #f1f5f9; }
    .tech-label { color: #64748b; font-weight: 600; font-size: 13px; }
    .tech-value { color: #000000; font-weight: 800; text-align: right; font-size: 15px; }

    .stButton > button { 
        width: 100%; background: #013A71; color: white !important; font-weight: 800; border-radius: 8px; height: 3.5rem;
    }
    
    .disease-box { 
        background-color: #f0f7ff; padding: 12px; border-radius: 8px; border-left: 5px solid #00B4D8; margin-top: 10px; font-size: 14px;
    }

    /* Estilo para perguntas do Quiz */
    .quiz-question { background: #f8fafc; padding: 15px; border-radius: 10px; margin-bottom: 20px; border: 1px solid #cbd5e1; }
    </style>
    """, unsafe_allow_html=True)

init_db()

# --- 4. LÓGICA DE LOGIN ---
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
                st.session_state['username'] = user
                st.rerun()
            else: st.error("Incorreto.")
else:
    # BANCO DE DADOS INTEGRAL
    DADOS_PNI = {
        "GESTANTES": {
            "VSR (ABRYSVO)": {"via": "IM Profunda", "local": "Deltoide", "agulha": "25x0,6mm", "doses": ["28ª a 36ª sem"], "ret": 0, "tipo": "INATIVADA", "previne": "Bronquiolite no RN."},
            "dTpa": {"via": "IM", "local": "Deltoide", "agulha": "25x0,6mm", "doses": ["A partir da 20ª sem"], "ret": 0, "tipo": "INATIVADA", "previne": "Difteria, Tétano e Coqueluche."},
            "HEPATITE B": {"via": "IM", "local": "Deltoide", "agulha": "25x0,6mm", "doses": ["3 Doses"], "ret": 30, "tipo": "INATIVADA", "previne": "Hepatite B."}
        },
        "INFANTIL": {
            "BCG": {"via": "ID", "local": "Deltoide Dir.", "agulha": "13x0,45mm", "doses": ["Dose Única"], "ret": 0, "tipo": "ATENUADA", "previne": "Tuberculose."},
            "PENTAVALENTE": {"via": "IM", "local": "Vasto Lateral Esq.", "agulha": "20x0,55mm", "doses": ["2, 4 e 6 meses"], "ret": 60, "tipo": "INATIVADA", "previne": "DTP + HepB + Hib."},
            "VIP (POLIO)": {"via": "IM", "local": "Vasto Lateral Dir.", "agulha": "20x0,55mm", "doses": ["2, 4, 6m e 15m"], "ret": 60, "tipo": "INATIVADA", "previne": "Paralisia Infantil."},
            "ROTAVÍRUS": {"via": "VO", "local": "Boca", "agulha": "Bisnaga", "doses": ["2 e 4 meses"], "ret": 60, "tipo": "ATENUADA", "previne": "Diarreia grave."}
        }
    }

    tab1, tab2 = st.tabs(["💉 REGISTRO E CONSULTA", "🧠 SUPER QUIZ TÉCNICO"])

    with tab1:
        st.markdown("<div class='hero-section'><h1>SISTEMA IMUNIZAÇÃO 2026</h1></div>", unsafe_allow_html=True)
        g_sel = st.selectbox("GRUPO:", list(DADOS_PNI.keys()))
        v_sel = st.selectbox("VACINA:", list(DADOS_PNI[g_sel].keys()))
        v = DADOS_PNI[g_sel][v_sel]

        c_info, c_reg = st.columns([1,1])
        with c_info:
            st.markdown(f"""<div class="tech-card">
                <div class="tech-item"><span class="tech-label">VIA</span><span class="tech-value">{v['via']}</span></div>
                <div class="tech-item"><span class="tech-label">LOCAL</span><span class="tech-value">{v['local']}</span></div>
                <div class="tech-item"><span class="tech-label">AGULHA</span><span class="tech-value">{v['agulha']}</span></div>
                <div class="disease-box"><b>Previne:</b> {v['previne']}</div>
            </div>""", unsafe_allow_html=True)
        with c_reg:
            paciente = st.text_input("NOME PACIENTE").upper()
            if st.button("REGISTRAR DOSE"):
                st.success(f"Dose de {v_sel} registrada para {paciente}")

    with tab2:
        st.markdown("## 🧠 Desafio Vacinador Master")
        st.write("Responda às questões técnicas baseadas no PNI 2026.")
        
        # --- BLOCO DE QUESTÕES ---
        pontos = 0
        
        with st.container():
            st.markdown("<div class='quiz-question'>", unsafe_allow_html=True)
            q1 = st.radio("1. Qual o período ideal para a vacina VSR (Abrysvo) em gestantes?", 
                         ["20 a 30 semanas", "28 a 36 semanas", "12 a 24 semanas"], key="q1")
            if q1 == "28 a 36 semanas": pontos += 1
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div class='quiz-question'>", unsafe_allow_html=True)
            q2 = st.radio("2. Qual a via e local da vacina BCG?", 
                         ["Subcutânea / Deltoide Esq", "Intradérmica / Deltoide Dir", "Intramuscular / Vasto Lateral"], key="q2")
            if q2 == "Intradérmica / Deltoide Dir": pontos += 1
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div class='quiz-question'>", unsafe_allow_html=True)
            q3 = st.radio("3. Qual agulha é padrão para vacinas IM em bebês (vasto lateral)?", 
                         ["13 x 0,45mm", "25 x 0,6mm", "20 x 0,55mm"], key="q3")
            if q3 == "20 x 0,55mm": pontos += 1
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div class='quiz-question'>", unsafe_allow_html=True)
            q4 = st.radio("4. Se a criança cuspir a vacina de Rotavírus, qual o procedimento?", 
                         ["Repetir a dose imediatamente", "Não repetir a dose", "Agendar para o dia seguinte"], key="q4")
            if q4 == "Não repetir a dose": pontos += 1
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div class='quiz-question'>", unsafe_allow_html=True)
            q5 = st.radio("5. A vacina Pentavalente protege contra quais doenças?", 
                         ["Difteria, Tétano, Coqueluche, HepB e Hib", "Sarampo, Caxumba e Rubéola", "Polio e Rotavírus"], key="q5")
            if q5 == "Difteria, Tétano, Coqueluche, HepB e Hib": pontos += 1
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div class='quiz-question'>", unsafe_allow_html=True)
            q6 = st.radio("6. Qual a temperatura ideal de conservação das vacinas na geladeira?", 
                         ["0°C a +10°C", "+2°C a +8°C", "-2°C a +2°C"], key="q6")
            if q6 == "+2°C a +8°C": pontos += 1
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div class='quiz-question'>", unsafe_allow_html=True)
            q7 = st.radio("7. Qual o intervalo mínimo entre duas vacinas de vírus vivos (Atenuadas) se não aplicadas no mesmo dia?", 
                         ["15 dias", "30 dias", "60 dias"], key="q7")
            if q7 == "30 dias": pontos += 1
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div class='quiz-question'>", unsafe_allow_html=True)
            q8 = st.radio("8. A vacina VIP (Poliomielite Inativada) é administrada por qual via?", 
                         ["Oral", "Subcutânea", "Intramuscular"], key="q8")
            if q8 == "Intramuscular": pontos += 1
            st.markdown("</div>", unsafe_allow_html=True)

        if st.button("FINALIZAR QUIZ E VER RESULTADO"):
            st.write(f"### Você acertou {pontos} de 8 perguntas!")
            if pontos == 8: st.balloons(); st.success("Excelente! Você é um Vacinador Master!")
            elif pontos >= 5: st.warning("Bom trabalho, mas revise os protocolos das que errou.")
            else: st.error("Atenção! É necessário estudar mais o manual da Rede de Frio.")

    if st.button("🚪 LOGOUT"):
        st.session_state['logged_in'] = False
        st.rerun()

st.caption("PNI Master Elite 2026 - v14.0")
