import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# 1. Configuração da Página
st.set_page_config(
    page_title="Vacinador Master Elite 2025",
    page_icon="💉",
    layout="wide"
)

# 2. Estilo CSS para melhorar a aparência
st.markdown("""
    <style>
    .main { background-color: #F0F2F5; }
    .stMetric { background-color: #ffffff; padding: 10px; border-radius: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    .vax-card { padding: 20px; border-radius: 10px; border-left: 5px solid #0057B7; background-color: white; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# 3. Banco de Dados Técnico Atualizado (PNI 2025/2026)
DADOS_PNI = {
    "🍼 BEBÊS (0-12 meses) 🧸": {
        "BCG": {"via": "ID", "local": "Deltoide Direito", "agulha": "13 x 0,45mm", "doses": ["Dose Única"], "ret": 0, "tipo": "ATENUADA"},
        "HEPATITE B (RN)": {"via": "IM", "local": "Vasto Lateral Dir.", "agulha": "20 x 0,55mm", "doses": ["Dose Única"], "ret": 0, "tipo": "INATIVADA"},
        "PENTAVALENTE": {"via": "IM", "local": "Vasto Lateral Esq.", "agulha": "20 x 0,55mm", "doses": ["1ª Dose (2m)", "2ª Dose (4m)", "3ª Dose (6m)"], "ret": 60, "tipo": "INATIVADA"},
        "VIP (POLIO INJETÁVEL)": {"via": "IM", "local": "Vasto Lateral Dir.", "agulha": "20 x 0,55mm", "doses": ["1ª (2m)", "2ª (4m)", "3ª (6m)", "Reforço (15m)"], "ret": 60, "tipo": "INATIVADA"},
        "PNEUMO 10V": {"via": "IM", "local": "Vasto Lateral Dir.", "agulha": "20 x 0,55mm", "doses": ["1ª Dose (2m)", "2ª Dose (4m)", "Reforço (12m)"], "ret": 60, "tipo": "INATIVADA"},
        "MENINGO C": {"via": "IM", "local": "Vasto Lateral Esq.", "agulha": "20 x 0,55mm", "doses": ["1ª Dose (3m)", "2ª Dose (5m)", "Reforço (12m)"], "ret": 60, "tipo": "INATIVADA"},
        "ROTAVÍRUS": {"via": "VO", "local": "Boca", "agulha": "Bisnaga", "doses": ["1ª Dose (2m)", "2ª Dose (4m)"], "ret": 60, "tipo": "ATENUADA"},
        "FEBRE AMARELA": {"via": "SC", "local": "Deltoide (Face Ext.)", "agulha": "13 x 0,45mm", "doses": ["9 meses", "4 anos (Reforço)"], "ret": 1095, "tipo": "ATENUADA"}
    },
    "🧒 CRIANÇAS (1-4 anos) 🎈": {
        "HEPATITE A": {"via": "IM", "local": "Deltoide/Vasto", "agulha": "20 x 0,55mm", "doses": ["Dose Única (15 meses)"], "ret": 0, "tipo": "INATIVADA"},
        "DTP (TRÍPLICE INFANTIL)": {"via": "IM", "local": "Deltoide/Vasto", "agulha": "20 x 0,55mm", "doses": ["1º Reforço (15m)", "2º Reforço (4 anos)"], "ret": 1095, "tipo": "INATIVADA"},
        "SCR (TRÍPLICE VIRAL)": {"via": "SC", "local": "Deltoide Esq.", "agulha": "13 x 0,45mm", "doses": ["12 meses (1ª Dose)", "15 meses (2ª Dose)"], "ret": 90, "tipo": "ATENUADA"},
        "VARICELA": {"via": "SC", "local": "Deltoide Esq.", "agulha": "13 x 0,45mm", "doses": ["15 meses", "4 anos"], "ret": 1095, "tipo": "ATENUADA"}
    },
    "🧑‍🎓 ADOLESCENTES E ADULTOS 🧗": {
        "HPV QUADRIVALENTE": {"via": "IM", "local": "Deltoide", "agulha": "25 x 0,6mm", "doses": ["Dose Única (9-14 anos)"], "ret": 0, "tipo": "INATIVADA"},
        "MENINGO ACWY": {"via": "IM", "local": "Deltoide", "agulha": "25 x 0,6mm", "doses": ["Dose Única (11-14 anos)"], "ret": 0, "tipo": "INATIVADA"},
        "dT (DUPLA ADULTO)": {"via": "IM", "local": "Deltoide", "agulha": "25 x 0,6mm", "doses": ["Reforço a cada 10 anos"], "ret": 3650, "tipo": "INATIVADA"},
        "PNEUMO 23V": {"via": "IM/SC", "local": "Deltoide", "agulha": "25 x 0,6mm", "doses": ["Dose Única (Idosos/Acamados)"], "ret": 1825, "tipo": "INATIVADA"}
    },
    "🤰 GESTANTES 🌸": {
        "VSR (ABRYSVO)": {"via": "IM Profunda", "local": "Deltoide", "agulha": "25 x 0,6mm", "doses": ["A partir da 24ª semana"], "ret": 0, "tipo": "INATIVADA"},
        "dTpa (TRÍPLICE ACELULAR)": {"via": "IM", "local": "Deltoide", "agulha": "25 x 0,6mm", "doses": ["A partir da 20ª semana"], "ret": 0, "tipo": "INATIVADA"}
    },
    "📢 CAMPANHAS E ESPECIAIS 📢": {
        "INFLUENZA (GRIPE)": {"via": "IM", "local": "Deltoide", "agulha": "25 x 0,6mm", "doses": ["Dose Anual"], "ret": 365, "tipo": "INATIVADA"},
        "DENGUE (QDENGA)": {"via": "SC", "local": "Deltoide", "agulha": "13 x 0,45mm", "doses": ["1ª Dose", "2ª Dose"], "ret": 90, "tipo": "ATENUADA"},
        "COVID-19 XBB": {"via": "IM", "local": "Deltoide", "agulha": "25 x 0,6mm", "doses": ["Dose Anual"], "ret": 365, "tipo": "INATIVADA"}
    }
}

# 4. Lógica de Armazenamento
def registrar_log(nome, vacina, dose, retorno):
    arquivo = "historico_vacinas.csv"
    novo_item = pd.DataFrame([[datetime.now().strftime("%d/%m/%Y"), nome, vacina, dose, retorno]], 
                             columns=["Data Registro", "Paciente", "Vacina", "Dose", "Retorno Previsto"])
    if not os.path.isfile(arquivo):
        novo_item.to_csv(arquivo, index=False)
    else:
        novo_item.to_csv(arquivo, mode='a', header=False, index=False)

# --- INTERFACE ---
st.title("🌈 SISTEMA VACINADOR MASTER 2025")
st.markdown(f"**Data Atual:** {datetime.now().strftime('%d/%m/%Y')}")

# Barra Lateral
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2864/2864448.png", width=100)
st.sidebar.title("MENU TÉCNICO")
cat_sel = st.sidebar.selectbox("CATEGORIA:", list(DADOS_PNI.keys()))
vax_sel = st.sidebar.radio("VACINA:", list(DADOS_PNI[cat_sel].keys()))

v_info = DADOS_PNI[cat_sel][vax_sel]

# Colunas Principais
col_tecnica, col_registro = st.columns([1.5, 1])

with col_tecnica:
    st.subheader(f"💉 Ficha Técnica: {vax_sel}")
    
    # Alerta de Tipo
    if v_info["tipo"] == "ATENUADA":
        st.error(f"⚠️ TIPO: {v_info['tipo']} (Microrganismos Vivos)")
    else:
        st.success(f"✅ TIPO: {v_info['tipo']} (Microrganismos Inativados)")

    st.markdown(f"""
    <div class="vax-card">
        <h4>📋 Orientações de Aplicação</h4>
        <p><b>📍 LOCAL:</b> {v_info['local']}</p>
        <p><b>📏 AGULHA:</b> {v_info['agulha']}</p>
        <p><b>💉 VIA:</b> {v_info['via']}</p>
        <p><b>🗓️ INTERVALO:</b> {v_info['ret']} dias</p>
    </div>
    """, unsafe_allow_html=True)
    
    

with col_registro:
    st.subheader("📝 Registro do Paciente")
    with st.form("form_registro", clear_on_submit=True):
        nome = st.text_input("NOME DO PACIENTE:").upper()
        dose = st.selectbox("DOSE APLICADA:", v_info["doses"])
        data_aplicada = st.date_input("DATA DA APLICAÇÃO:", datetime.now())
        
        btn = st.form_submit_button("REGISTRAR E APRAZAR")
        
        if btn:
            if nome:
                ret_calculado = (data_aplicada + timedelta(days=v_info['ret'])).strftime("%d/%m/%Y") if v_info['ret'] > 0 else "ESQUEMA CONCLUÍDO"
                registrar_log(nome, vax_sel, dose, ret_calculado)
                st.balloons()
                st.success(f"**REGISTRADO!**\n\n📅 PRÓXIMO RETORNO: **{ret_calculado}**")
            else:
                st.warning("⚠️ Digite o nome do paciente.")

st.divider()

# Histórico
if st.checkbox("Visualizar Histórico de Atendimentos"):
    if os.path.isfile("historico_vacinas.csv"):
        df = pd.read_csv("historico_vacinas.csv")
        st.table(df)
        st.download_button("Exportar para Excel (CSV)", df.to_csv(index=False), "historico.csv", "text/csv")
    else:
        st.info("Nenhum registro encontrado.")

st.caption("Sistema Master v5.0 - Atualizado conforme PNI 2025/2026")