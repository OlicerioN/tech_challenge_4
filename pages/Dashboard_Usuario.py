import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

st.title("Perfil do Usuário", text_alignment="center")

if "perfil_usuario" not in st.session_state:
    st.warning("Faça uma previsão na página principal para ver seu dashboard personalizado")
    st.stop()

df = pd.read_csv("obesity_modelado.csv")

user = st.session_state["perfil_usuario"].iloc[0]
imc_user = st.session_state["IMC_usuario"]
classe_prevista = st.session_state["classe_prevista"]
nome_cliente = st.session_state["nome_paciente"]

st.markdown(f"#### 👤 {nome_cliente.upper()}")
st.markdown(f"#### 🔶 **Classe Prevista:** {classe_prevista.upper()}")

st.markdown("---")

st.metric("Seu IMC", f"{imc_user:.2f}")

st.markdown("---")

# COmparação do IMC com população e classe
col1, col2 = st.columns(2)
col1.metric("IMC médio da população", f"{df['IMC'].mean():.2f}")
col2.metric(
    f"IMC médio da classe '{classe_prevista}'",
    f"{df[df['nivel_obesidade'] == classe_prevista]['IMC'].mean():.2f}"
)

st.markdown("---")

st.subheader("Onde voce se encontra na distribuição geral de IMC", text_alignment="center")

fig_hist = px.histogram(df, x="IMC", nbins=40, title="Distribuição Geral de IMC")
fig_hist.add_vline(x=imc_user, line_width=3, line_color="red")
st.plotly_chart(fig_hist, use_container_width=True)

st.markdown("---")

st.subheader("Seu perfil de hábitos vs Média da População", text_alignment="center")

habitos = [
    "freq_vegetais",
    "freq_alimentos_caloricos",
    "freq_exercicios_semana",
    "tempo_tela_diario",
    "consumo_agua"
]

habitos_labels = {
    "freq_vegetais": "Consumo de Vegetais",
    "freq_alimentos_caloricos": "Alimentos Calóricos",
    "freq_exercicios_semana": "Exercícios por Semana",
    "tempo_tela_diario": "Tempo de Tela (h/dia)",
    "consumo_agua": "Consumo de Água (L)"
}

labels_exibicao = [habitos_labels[h] for h in habitos]

valores_user = [user[h] for h in habitos]
valores_media = [df[h].mean() for h in habitos]

fig_radar = go.Figure()

fig_radar.add_trace(go.Scatterpolar(
    r=valores_user,
    theta=labels_exibicao,
    fill='toself',
    name='Voce'
))

fig_radar.update_layout(
    polar=dict(radialaxis=dict(visible=True)),
    showlegend=True,
    title="Comparacao de Hábitos"
)

st.plotly_chart(fig_radar, use_container_width=True)

st.markdown("---")

st.subheader("Como voce se compara com pessoas da mesma classe?", text_alignment="center")

classe_df = df[df["nivel_obesidade"] == classe_prevista]

colA, colB = st.columns(2)
colA.metric("IMC Médio da Classe", f"{classe_df['IMC'].mean():.2f}")
colB.metric("IMC Máximo da Classe", f"{classe_df['IMC'].max():.2f}")

fig_box = px.box(
    classe_df,
    y="IMC",
    title=f"Seu IMC vs Distribuição da classe {classe_prevista}"
)

fig_box.add_hline(y=imc_user, line_width=3, line_color="red")
st.plotly_chart(fig_box, use_container_width=True)
