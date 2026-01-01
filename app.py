import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# 1. Configurações de Sistema
st.set_page_config(page_title="PNI Elite 2026", layout="wide", page_icon="💉")

# 2. CSS Master (Design Moderno, Botões Flutuantes e Letras Ultra Visíveis)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');

    /* Reset e Fundo */
    html, body, [class*="st-"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: #000000 !important;
    }
    .main { background-color: #f8fafc; }

    /* Barra Lateral - Contraste Máximo */
    [data-testid="stSidebar"] { background-color: #ffffff !important; border-right: 2px solid #e2e8f0; }
    [data-testid="stSidebar"] .stMarkdown p, label, .stRadio label {
        color: #000000 !important;
        font-weight: 800 !important;
        font-size: 15px !important;
    }

    /* Cabeçalho Moderno */
    .hero-section {
        background: linear-gradient(135deg, #013A71 0%, #001d3d 100%);
        padding: 40px;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    }

    /* Cartões de Informação Técnica */
    .tech-card {
        background: white;
        padding: 25px;
        border-radius: 16px;
        border: 2px solid #e2e8f0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .tech-item {
        display: flex;
        justify-content: space-between;
        padding: 12px 0;
        border-bottom: 1px solid #f1f5f9;
    }
    .tech-label { color: #475569; font-weight: 600; }
    .tech-value { color: #000000; font-weight: 800; }

    /* Botão Moderno */
    .stButton > button {
        width: 100%;
        background: #013A71;
        color: white !important;
        border: none;
        padding: 12px;
        border-radius: 10px;
        font-weight: 800;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        background: #00B4D8;
        transform: scale(1.02);
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Banner Principal
st.markdown("""
    <div class="hero-section">
        <h1 style="color: white; margin:0;">SISTEMA DE IMUNIZAÇÃO PROFISSIONAL 2026</h1>
        <p style="color: #00B4D8; font-size: 18px; font-weight:600;">Controle de Protocolos e Aprazamento</p>
    </div>
    """, unsafe_allow_html=True)

# 4. BANCO DE DADOS INTEGRAL (TODAS AS VACINAS DE VOLTA)
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

# 5. Barra Lateral
with st.sidebar:
    st.markdown("### 📋 SELEÇÃO TÉCNICA")
    cat = st.selectbox("GRUPO:", list(DADOS_PNI.keys()))
    vax = st.radio("VACINA:", list(DADOS_PNI[cat].keys()))
    v_info = DADOS_PNI[cat][vax]

# 6. Painel Principal
col_info, col_reg = st.columns([1.5, 1], gap="large")

with col_info:
    st.markdown(f"### 🛡️ Protocolo: {vax}")
    
    # Badge de Tipo
    if v_info["tipo"] == "ATENUADA":
        st.error(f"**ATENÇÃO:** {v_info['tipo']} (Vírus/Bactéria Vivo)")
    else:
        st.success(f"**TIPO:** {v_info['tipo']} (Inativada)")

    st.markdown(f"""
    <div class="tech-card">
        <div class="tech-item"><span class="tech-label">VIA</span><span class="tech-value">{v_info['via']}</span></div>
        <div class="tech-item"><span class="tech-label">LOCAL</span><span class="tech-value">{v_info['local']}</span></div>
        <div class="tech-item"><span class="tech-label">AGULHA</span><span class="tech-value">{v_info['agulha']}</span></div>
        <div class="tech-item" style="border:none;"><span class="tech-label">RETORNO</span><span class="tech-value">{v_info['ret']} dias</span></div>
    </div>
    """, unsafe_allow_html=True)

with col_reg:
    st.markdown("### ✍️ Atendimento")
    nome = st.text_input("NOME DO PACIENTE").upper()
    dose = st.selectbox("DOSE SELECIONADA", v_info["doses"])
    
    if st.button("REGISTRAR ATENDIMENTO"):
        if nome:
            retorno = (datetime.now() + timedelta(days=v_info['ret'])).strftime("%d/%m/%Y") if v_info['ret'] > 0 else "DOSE ÚNICA"
            st.info(f"✅ **REGISTRADO COM SUCESSO**")
            st.write(f"Paciente: **{nome}**")
            st.write(f"Próxima Visita: **{retorno}**")
        else:
            st.warning("⚠️ Digite o nome do paciente.")

st.markdown("---")
st.caption("PNI Master 2026 • Design Profissional de Alto Contraste • Versão Integral")
