import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# 1. Configuração da Página
st.set_page_config(
    page_title="PNI 2026 | Gestão de Imunização",
    page_icon="💉",
    layout="wide"
)

# 2. CSS Avançado para Design Institucional
st.markdown("""
    <style>
    /* Importação de fonte moderna */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap');

    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
    }

    /* Cabeçalho Superior Estilizado */
    .header-container {
        background: linear-gradient(135deg, #013A71 0%, #0259AB 100%);
        padding: 40px 20px;
        border-radius: 15px;
        margin-bottom: 35px;
        box-shadow: 0 10px 25px rgba(1, 58, 113, 0.2);
        text-align: center;
        border-bottom: 4px solid #00B4D8;
    }
    .header-title {
        color: white !important;
        font-weight: 800;
        font-size: 38px;
        text-transform: uppercase;
        letter-spacing: -1px;
        margin: 0;
    }
    .header-subtitle {
        color: #E0E0E0;
        font-size: 16px;
        margin-top: 10px;
        font-weight: 400;
        letter-spacing: 1px;
    }

    /* Estilização dos Cards Técnicos */
    .vax-card {
        background-color: #FFFFFF !important;
        padding: 30px;
        border-radius: 12px;
        border-left: 8px solid #013A71;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        margin-bottom: 25px;
    }
    .vax-card h3 { 
        color: #013A71 !important; 
        font-weight: 700;
        margin-bottom: 20px;
        border-bottom: 1px solid #eee;
        padding-bottom: 10px;
    }
    .vax-card p { 
        font-size: 16px; 
        line-height: 1.6;
        color: #333333 !important;
        margin: 10px 0;
    }
    .vax-card b { 
        color: #013A71; 
        font-weight: 700;
    }

    /* Ajustes da Sidebar */
    [data-testid="stSidebar"] {
        background-color: #f8fafc;
        border-right: 1px solid #e2e8f0;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Cabeçalho Visual
st.markdown("""
    <div class="header-container">
        <p class="header-title">SISTEMA DE IMUNIZAÇÃO PROFISSIONAL</p>
        <p class="header-subtitle">PROGRAMA NACIONAL DE IMUNIZAÇÃO • ATUALIZAÇÃO GOVERNAMENTAL 2026</p>
    </div>
    """, unsafe_allow_html=True)

# 4. Banco de Dados Integral 2026
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

# 5. Lógica da Interface
st.sidebar.markdown("### ⚙️ PARÂMETROS TÉCNICOS")
cat_sel = st.sidebar.selectbox("CATEGORIA ALVO:", list(DADOS_PNI.keys()))
vax_sel = st.sidebar.radio("IMUNOBIOLÓGICO:", list(DADOS_PNI[cat_sel].keys()))
v_info = DADOS_PNI[cat_sel][vax_sel]

col1, col2 = st.columns([1.6, 1])

with col1:
    st.markdown(f"#### Especificação de Protocolo: **{vax_sel}**")
    
    if v_info["tipo"] == "ATENUADA":
        st.error(f"☢️ **TIPO:** {v_info['tipo']} (Vírus/Bactéria Vivo)")
    else:
        st.success(f"🛡️ **TIPO:** {v_info['tipo']} (Inativada/Fragmentada)")

    st.markdown(f"""
        <div class="vax-card">
            <h3>📖 Orientações de Administração</h3>
            <p><b>📍 LOCAL DE APLICAÇÃO:</b> {v_info['local']}</p>
            <p><b>📏 CALIBRE DE AGULHA:</b> {v_info['agulha']}</p>
            <p><b>💉 VIA DE ADMINISTRAÇÃO:</b> {v_info['via']}</p>
            <p><b>🗓️ PRAZO PARA RETORNO:</b> {v_info['ret']} dias</p>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("#### 👤 Atendimento")
    with st.container():
        nome = st.text_input("NOME DO PACIENTE:").upper()
        dose = st.selectbox("DOSE DO ESQUEMA:", v_info["doses"])
        
        if st.button("🚀 REGISTRAR E APRAZAR"):
            if nome:
                retorno = (datetime.now() + timedelta(days=v_info['ret'])).strftime("%d/%m/%Y") if v_info['ret'] > 0 else "CONCLUÍDO"
                st.info("✅ Registro processado com sucesso.")
                st.markdown(f"""
                ---
                **Paciente:** {nome}  
                **Status:** {dose} aplicada  
                **Próximo Retorno:** `{retorno}`
                """)
            else:
                st.error("⚠️ Identificação obrigatória.")

st.markdown("---")
st.caption("Base normativa atualizada • Ministério da Saúde 2026")
