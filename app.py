import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# 1. Configuração de Alta Performance
st.set_page_config(
    page_title="PNI 2026 | Gestão Profissional",
    page_icon="💉",
    layout="wide"
)

# 2. CSS DE ALTO NÍVEL (Design limpo, contraste máximo e tipografia séria)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');

    /* Reset Geral */
    html, body, [class*="st-"] {
        font-family: 'Roboto', sans-serif;
        color: #1e293b !important;
    }

    /* Estilização da Barra Lateral */
    [data-testid="stSidebar"] {
        background-color: #f1f5f9 !important;
        border-right: 1px solid #e2e8f0;
    }
    [data-testid="stSidebar"] .stMarkdown p, label {
        color: #0f172a !important;
        font-weight: 600 !important;
        font-size: 15px !important;
    }

    /* Título do Dashboard */
    .dashboard-header {
        background-color: #0f172a;
        padding: 40px;
        border-radius: 12px;
        margin-bottom: 30px;
        color: white !important;
        text-align: center;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    .dashboard-header h1 {
        color: #f8fafc !important;
        font-weight: 700;
        letter-spacing: -1px;
    }

    /* Cards de Informação Técnica */
    .info-card {
        background-color: #ffffff;
        padding: 30px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    .info-card h3 {
        color: #2563eb !important;
        border-bottom: 2px solid #f1f5f9;
        padding-bottom: 15px;
        margin-bottom: 20px;
    }
    .data-row {
        display: flex;
        justify-content: space-between;
        padding: 12px 0;
        border-bottom: 1px solid #f8fafc;
    }
    .label-tech { font-weight: 700; color: #64748b; }
    .value-tech { font-weight: 700; color: #0f172a; }

    /* Estilo de Sucesso e Erro (Inativada vs Atenuada) */
    .stAlert {
        border-radius: 8px !important;
        border: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Cabeçalho de Comando
st.markdown("""
    <div class="dashboard-header">
        <h1>GESTÃO DE IMUNIZAÇÃO PNI 2026</h1>
        <p style="color: #94a3b8;">SISTEMA TÉCNICO DE APOIO À DECISÃO CLÍNICA</p>
    </div>
    """, unsafe_allow_html=True)

# 4. Banco de Dados (Mantendo a integridade total solicitada)
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
    "CALENDÁRIO ADULTO": {
        "HPV QUADRIVALENTE": {"via": "IM", "local": "Deltoide", "agulha": "25 x 0,6mm", "doses": ["Dose Única (9-14 anos)"], "ret": 0, "tipo": "INATIVADA"},
        "MENINGO ACWY": {"via": "IM", "local": "Deltoide", "agulha": "25 x 0,6mm", "doses": ["Dose Única (11-14 anos)"], "ret": 0, "tipo": "INATIVADA"},
        "dT (DUPLA ADULTO)": {"via": "IM", "local": "Deltoide", "agulha": "25 x 0,6mm", "doses": ["Reforço a cada 10 anos"], "ret": 3650, "tipo": "INATIVADA"},
        "PNEUMO 23V": {"via": "IM/SC", "local": "Deltoide", "agulha": "25 x 0,6mm", "doses": ["Dose Única"], "ret": 1825, "tipo": "INATIVADA"}
    },
    "CALENDÁRIO GESTANTES": {
        "VSR (ABRYSVO)": {"via": "IM Profunda", "local": "Deltoide", "agulha": "25 x 0,6mm", "doses": ["24ª a 36ª semana"], "ret": 0, "tipo": "INATIVADA"},
        "dTpa": {"via": "IM", "local": "Deltoide", "agulha": "25 x 0,6mm", "doses": ["A partir da 20ª semana"], "ret": 0, "tipo": "INATIVADA"}
    },
    "CAMPANHAS SAZONAIS": {
        "INFLUENZA": {"via": "IM", "local": "Deltoide", "agulha": "25 x 0,6mm", "doses": ["Dose Anual"], "ret": 365, "tipo": "INATIVADA"},
        "DENGUE": {"via": "SC", "local": "Deltoide", "agulha": "13 x 0,45mm", "doses": ["1ª Dose", "2ª Dose"], "ret": 90, "tipo": "ATENUADA"},
        "COVID-19 XBB": {"via": "IM", "local": "Deltoide", "agulha": "25 x 0,6mm", "doses": ["Dose Anual"], "ret": 365, "tipo": "INATIVADA"}
    }
}

# 5. Menu Lateral
st.sidebar.markdown("### 🛠️ CONFIGURAÇÃO DO ATENDIMENTO")
cat_sel = st.sidebar.selectbox("CATEGORIA", list(DADOS_PNI.keys()))
vax_sel = st.sidebar.radio("IMUNOBIOLÓGICO", list(DADOS_PNI[cat_sel].keys()))
v_info = DADOS_PNI[cat_sel][vax_sel]

# 6. Painel Principal (Grid Layout)
col_dados, col_form = st.columns([1.5, 1], gap="large")

with col_dados:
    st.subheader(f"🔍 Protocolo Clínico: {vax_sel}")
    
    # Status de Tipo
    if v_info["tipo"] == "ATENUADA":
        st.error(f"**ALERTA:** Vacina de Agente Etiológico VIVO (Atenuada)")
    else:
        st.success(f"**STATUS:** Vacina de Agente INATIVADO")

    # Card com informações tabuladas
    st.markdown(f"""
        <div class="info-card">
            <h3>Especificações de Administração</h3>
            <div class="data-row"><span class="label-tech">VIA DE ADMINISTRAÇÃO</span><span class="value-tech">{v_info['via']}</span></div>
            <div class="data-row"><span class="label-tech">LOCAL DE ELEIÇÃO</span><span class="value-tech">{v_info['local']}</span></div>
            <div class="data-row"><span class="label-tech">AGULHA RECOMENDADA</span><span class="value-tech">{v_info['agulha']}</span></div>
            <div class="data-row"><span class="label-tech">INTERVALO PARA RETORNO</span><span class="value-tech">{v_info['ret']} dias</span></div>
        </div>
    """, unsafe_allow_html=True)
    
    

with col_form:
    st.subheader("📋 Registro de Dose")
    with st.container():
        nome = st.text_input("IDENTIFICAÇÃO DO PACIENTE").upper()
        dose = st.selectbox("DOSE DO ESQUEMA", v_info["doses"])
        
        if st.button("CONFIRMAR E GERAR APRAZAMENTO", use_container_width=True):
            if nome:
                retorno = (datetime.now() + timedelta(days=v_info['ret'])).strftime("%d/%m/%Y") if v_info['ret'] > 0 else "CONCLUÍDO"
                st.info(f"**Registro de Atendimento Confirmado**")
                st.write(f"Paciente: **{nome}**")
                st.write(f"Data de Retorno: **{retorno}**")
            else:
                st.warning("⚠️ Nome do paciente é obrigatório para o registro.")

st.markdown("---")
st.caption("Documento Técnico PNI 2026 | Desenvolvido para Alta Performance em Sala de Vacina")
