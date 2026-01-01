import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# Configuração da Página
st.set_page_config(page_title="SISTEMA VACINADOR PROFISSIONAL 2026", layout="wide")

# CSS para garantir legibilidade e visual técnico
st.markdown("""
    <style>
    .vax-card {
        background-color: #FFFFFF !important;
        color: #1A1A1A !important;
        padding: 25px;
        border-radius: 8px;
        border: 1px solid #BDBDBD;
        margin-bottom: 20px;
        box-shadow: 0px 2px 4px rgba(0,0,0,0.05);
    }
    .vax-card h3, .vax-card p, .vax-card b {
        color: #1A1A1A !important;
    }
    .main-title { 
        color: #013A71 !important; 
        text-align: center; 
        font-weight: bold;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)

# BANCO DE DADOS INTEGRAL 2026
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

st.markdown('<h1 class="main-title">SISTEMA DE IMUNIZAÇÃO PROFISSIONAL - PNI 2026</h1>', unsafe_allow_html=True)

# Lógica da Interface
st.sidebar.header("CONTROLE TÉCNICO")
cat_sel = st.sidebar.selectbox("CATEGORIA:", list(DADOS_PNI.keys()))
vax_sel = st.sidebar.radio("VACINA:", list(DADOS_PNI[cat_sel].keys()))
v_info = DADOS_PNI[cat_sel][vax_sel]

col1, col2 = st.columns([1.5, 1])

with col1:
    st.subheader(f"Especificação: {vax_sel}")
    if v_info["tipo"] == "ATENUADA":
        st.error(f"TIPO: {v_info['tipo']} (Vírus/Bactéria Vivo)")
    else:
        st.success(f"TIPO: {v_info['tipo']} (Inativada/Fragmentada)")

    st.markdown(f"""
        <div class="vax-card">
            <h3 style="margin-top:0;">Orientações de Administração</h3>
            <p><b>📍 LOCAL DE APLICAÇÃO:</b> {v_info['local']}</p>
            <p><b>📏 CALIBRE DE AGULHA:</b> {v_info['agulha']}</p>
            <p><b>💉 VIA:</b> {v_info['via']}</p>
            <p><b>🗓️ PRAZO PARA RETORNO:</b> {v_info['ret']} dias</p>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.subheader("Registro de Atendimento")
    nome = st.text_input("NOME DO PACIENTE (Letras Maiúsculas):").upper()
    dose = st.selectbox("DOSE SELECIONADA:", v_info["doses"])
    if st.button("REGISTRAR E CALCULAR RETORNO"):
        if nome:
            retorno = (datetime.now() + timedelta(days=v_info['ret'])).strftime("%d/%m/%Y") if v_info['ret'] > 0 else "CONCLUÍDO / DOSE ÚNICA"
            st.info(f"REGISTRO EFETUADO COM SUCESSO")
            st.write(f"Paciente: **{nome}**")
            st.write(f"Próximo Retorno: **{retorno}**")
        else:
            st.error("ERRO: Preencha o nome do paciente para continuar.")

st.markdown("---")
st.caption("Base de dados atualizada conforme normativas do Ministério da Saúde 2026.")
