import streamlit as st
import pandas as pd
import joblib

# Carregar modelo
modelo = joblib.load("modelo.pkl")

st.title("Predição de Obesidade")
st.write("Preencha os dados abaixo:")

# Inputs

col1, col2 = st.columns(2)

with col1:
    genero = st.selectbox("Gênero", ["Masculino", "Feminino"])
    idade = st.slider("Idade", 1, 120, 25)
    altura_m = st.slider("Altura (m)", 1.0, 2.5, 1.70)
    peso_kg = st.slider("Peso (kg)", 20, 300, 70)

with col2:
    hist_familiar_obesidade = st.selectbox("Possue histórico familiar de obesidade?", ["Sim", "Não"])
    fumante = st.selectbox("É fumante?", ["Sim", "Não"])
    monitor_calorias = st.selectbox("Costuma monitorar as calorias?", ["Sim", "Não"])
    lanches_entre_refeicoes = st.selectbox("Consome algum lanche entre as refeições?", ["nunca", "pouco", "sempre"])

st.markdown("---")

col3, col4 = st.columns(2)

with col3:
    freq_alimentos_caloricos = st.slider("Qual a frequencia de consumo de alimentos calóricos (0-3)", 0, 3, 1)
    freq_vegetais = st.slider("Qual a frequencia de consumo de vegetais?", 0, 3, 2)
    num_refeicoes_dia = st.slider("Quantas refeicoes faz por dia? (1-4)", 1, 4, 3)

with col4:
    consumo_agua = st.slider("Toma água com frequencia? (0-3)", 0, 3, 2)
    freq_exercicios_semana = st.slider("Qual a frequencia que costumar praticar exercicios? (0-3)", 0, 3, 1)
    tempo_tela_diario = st.slider("Tempo diário de tela? (0-3)", 0, 3, 1)

st.markdown("---")

col5, col6 = st.columns(2)

with col5:
    consumo_alcool = st.selectbox("Cosumo de Álcool", ["nunca", "pouco", "sempre"])
with col6:
    meio_transporte = st.selectbox("Qual meio de transporte costuma usar?", ["carro", "caminhar", "moto", "transporte publico"])

# Pré-processamento como o modelo espera

IMC = peso_kg / (altura_m ** 2)

df = pd.DataFrame([{
    "genero": 1 if genero == "Masculino" else 0,
    "idade": idade,
    "altura_m": altura_m,
    "peso_kg": peso_kg,
    "IMC": IMC,
    "hist_familiar_obesidade": 1 if hist_familiar_obesidade == "Sim" else 0,
    "freq_alimentos_caloricos": freq_alimentos_caloricos,
    "freq_vegetais": freq_vegetais,
    "num_refeicoes_dia": num_refeicoes_dia,
    "lanches_entre_refeicoes": lanches_entre_refeicoes,
    "fumante": 1 if fumante == "Sim" else 0,
    "consumo_agua": consumo_agua,
    "monitor_calorias": 1 if monitor_calorias == "Sim" else 0,
    "freq_exercicios_semana": freq_exercicios_semana,
    "tempo_tela_diario": tempo_tela_diario,
    "consumo_alcool": consumo_alcool,
    "meio_transporte": meio_transporte
}])

st.markdown("---")

if "classe_prevista" not in st.session_state:
    st.session_state["classe_prevista"] = None

if st.button("PREVER RESULTADO"):
    if IMC >= 40:
        pred = "Obesidade tipo 3"
    else:
        pred = modelo.predict(df)[0]

    st.session_state["perfil_usuario"] = df
    st.session_state["IMC_usuario"] = IMC
    st.session_state["classe_prevista"] = pred

    st.success(f"## Resultado previsto: **{pred.upper()}**")
    st.info(f"IMC calculado: **{IMC:.2f}**")
else:
    if st.session_state.get("classe_prevista") is not None:
        st.info(f"Ultima previsão: **{st.session_state['classe_prevista']}**")
        st.info(f"Ultimo IMC calculado: **{st.session_state.get('IMC_usuario'):.2f}**")

    else:
        st.write("Aperte **Prever** para gerar a previsao e salvar um perfil para o dashboard personalizado")

st.markdown("---")