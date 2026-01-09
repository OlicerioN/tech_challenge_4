import streamlit as st
import pandas as pd
import joblib
import io
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
import matplotlib.pyplot as plt
from reportlab.lib.units import cm
from reportlab.lib import colors
from datetime import datetime


# Carregar modelo
modelo = joblib.load("modelo.pkl")

st.title("Predição de Obesidade")
st.write("Preencha os dados abaixo:")

@st.cache_data
def carregar_base():
        return pd.read_csv("obesity_modelado.csv")

df_base = carregar_base()

def grafico_valores_reais(perfil):
    labels = ["Exercícios/sem", "Água (L)", "Tela (h)", "Vegetais", "Alim. Calóricos"]
    valores = [
        perfil["freq_exercicios_semana"],
        perfil["consumo_agua"],
        perfil["tempo_tela_diario"],
        perfil["freq_vegetais"],
        perfil["freq_alimentos_caloricos"]
    ]

    plt.figure(figsize=(6,3))
    plt.bar(labels, valores)
    plt.ylabel("FREQUÊNCIA)")
    plt.title("Hábitos do Paciente (Valores Reais)")
    plt.tight_layout()

    caminho = "grafico_valores_reais.png"
    plt.savefig(caminho)
    plt.close()

    return caminho

def gerar_pdf_usuario(perfil_df, imc, classe_prevista, nome_paciente, df_base):

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()

    #ESTILOS
    styles.add(ParagraphStyle(name="Titulo", fontSize=20, leading=24, alignment=1))
    styles.add(ParagraphStyle(name="Subtitulo", fontSize=14, leading=18))
    styles.add(ParagraphStyle(name="Texto", fontSize=11, leading=15))
    styles.add(ParagraphStyle(name="Rodape", fontSize=9, leading=12, textColor="grey"))

    story = []

    perfil = perfil_df.iloc[0]
    data = datetime.now().strftime("%d/%m/%Y")

    #CABECALHO
    story.append(Paragraph("Relatório de Avaliação Corporal", styles["Titulo"]))
    story.append(Spacer(1, 8))
    linha_info = Table([[f"Paciente: {nome_paciente}", f"Data: {data}"]], colWidths=[10*cm, 4*cm])

    linha_info.setStyle(TableStyle([
        ("ALIGN", (0,0), (0,0), "LEFT"),
        ("ALIGN", (1,0), (1,0), "RIGHT"),
        ("FONTSIZE", (0,0), (-1,-1), 13),
        ("FONTNAME", (0,0), (-1,-1), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10)
    ]))

    story.append(linha_info)
    story.append(Spacer(1, 18))

    #Ponto Atencao
    if perfil["freq_alimentos_caloricos"] >= 3:
        ponto_atencao = "Consumo elevado de alimentos calóricos"
    elif perfil["freq_exercicios_semana"] < 2:
        ponto_atencao = "Baixa prática de atividade física"
    elif perfil["tempo_tela_diario"] >= 4:
        ponto_atencao = "Sedentarismo"
    else:
        ponto_atencao = "Sem pontos críticos aparentes"

    #SCORE
    score = 0
    if perfil["freq_alimentos_caloricos"] < 2:
        score += 1
    if perfil["freq_exercicios_semana"] >= 3:
        score += 1
    if perfil["tempo_tela_diario"] < 4:
        score += 1
    if perfil["consumo_agua"] >= 2:
        score += 1

    if score >= 3:
        nivel_habitos = "Bons"
    elif score == 2:
        nivel_habitos = "Regulares"
    else:
        nivel_habitos = "Precisam melhorar"

    #Tabela  FALTA COLOCAR A VARIAVEL GENERO
    tabela = Table([
        ["DADOS DO PACIENTE", "RESULTADO DA ANÁLISE"],
        [f"Idade: {perfil['idade']}", f"IMC: {imc:.2f}"],
        [f"Gênero: {genero}", f"Classificação prevista: {classe_prevista.upper()}"],
        [f"Altura: {perfil['altura_m']} m", f"Nível geral de hábitos: {ponto_atencao}"],
        ], colWidths=[6*cm, 10*cm])
    
    tabela.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("GRID", (0,0), (-1,-1), 0.7, colors.grey),
        ("FONT", (0,0), (-1,0), "Helvetica-Bold"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
        ("RIGHTPADDING", (0,0), (-1,-1), 8),
        ("BACKGROUND", (1,1), (1,-1), colors.whitesmoke)
    ]))

    story.append(tabela)

    #GRÁFICOS
        #IMC
    fig, ax = plt.subplots(figsize=(6, 3))

    ax.hist(df_base["IMC"], bins=25, alpha=0.7)
    ax.axvline(imc, linewidth=2, linestyle="--", label="IMC do usuário")

    ax.set_title("Distribuição do IMC na população")
    ax.set_xlabel("IMC")
    ax.set_ylabel("Frequência")
    ax.legend()

    img_buffer = io.BytesIO()
    plt.tight_layout()
    plt.savefig(img_buffer, format="png")
    plt.close()
    img_buffer.seek(0)

    story.append(Spacer(1, 20))
    story.append(Image(img_buffer, width=15*cm, height=5*cm))

        #Grafico dos valores reais
    story.append(Image(grafico_valores_reais(perfil), width=14*cm, height=6*cm))

    #Recomendações
    story.append(Spacer(1, 20))

    story.append(Paragraph("Recomendações Gerais", styles["Subtitulo"]))
    story.append(Paragraph(
        "O gráfico acima destaca os principais fatores que contribuem para o perfil atual do paciente, auxiliando na priorização de mudanças de hábitos.",
        styles["Normal"]
    ))

    dicas = []
    if perfil["freq_alimentos_caloricos"] >= 3:
        dicas.append("Reduzir alimentos altamente calóricos pode ajudar no controle do peso.")

    if perfil["freq_exercicios_semana"] < 2:
        dicas.append("Aumentar a prática de atividades físicas semanais pode trazer benefícios à saúde.")

    if perfil["tempo_tela_diario"] >= 4:
        dicas.append("Reduzir o tempo em frente às telas pode ajudar a combater o sedentarismo.")

    if perfil["consumo_agua"] < 2:
        dicas.append("Aumentar a ingestão de água ao longo do dia pode favorecer o equilíbrio corporal.")

    if perfil["monitor_calorias"] == 0:
        dicas.append("Monitorar a ingestão calórica pode ajudar na criação de hábitos mais conscientes.")

    if not dicas:
        dicas.append("Os hábitos informados indicam um bom equilíbrio geral. Manter essa rotina é recomendado.")

    for dica in dicas:
        story.append(Paragraph(f"• {dica}", styles["Texto"]))

    #RODAPÉ
    story.append(Spacer(1, 25))
    story.append(Paragraph(
        "Este relatório foi gerado automaticamente por um sistema de apoio à decisão e " 
        "não substitui avaliação médica ou nutricional profissional.",
        styles["Rodape"]
        )
    )
    story.append(Paragraph(
        "PROJETO TECH CHALLENGE FASE 4", styles["Rodape"]
    ))

    doc.build(story)
    buffer.seek(0)

    return buffer




# Inputs

nome_paciente = st.text_input("Nome do Paciente")

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
    st.session_state["nome_paciente"] = nome_paciente

    st.success(f"## Resultado previsto: **{pred.upper()}**")
    st.info(f"IMC calculado: **{IMC:.2f}**")
else:
    st.write("Aperte **Prever** para gerar a previsao e salvar um perfil para o dashboard personalizado")

#BOTÂO PARA GERAR PDF
if st.session_state.get("classe_prevista") is not None:
    pdf_buffer = gerar_pdf_usuario(
        st.session_state["perfil_usuario"],
        st.session_state["IMC_usuario"],
        st.session_state["classe_prevista"],
        st.session_state["nome_paciente"],
        df_base
    )

    st.download_button(
        label="📄 Baixar relatório em PDF",
        data=pdf_buffer,
        file_name="relatorio_obesidade.pdf",
        mime="application/pdf"
    )

st.markdown("---")