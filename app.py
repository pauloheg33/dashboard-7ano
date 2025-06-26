
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

# Leitura dos arquivos CSV
arquivos = [
    "7_ANO_-_03_DE_DEZEMBRO_2025_2026_75993.csv",
    "7º_ANO_-_ANTONIO_DE_SOUSA_BARROS_2025_2026_76019.csv",
    "7º_ANO_A_-_21_DE_DEZEMBRO_2025_2026_71725.csv",
    "7º_ANO_A_-_FIRMINO_JOSE_2025_2026_76239.csv",
    "7º_ANO_B_-_21_DE_DEZEMBRO_2025_2026_71726.csv",
    "7º_ANO_C_-_21_DE_DEZEMBRO_2025_2026_71728.csv"
]
df = pd.concat([pd.read_csv(f) for f in arquivos], ignore_index=True)

# Leitura do gabarito
gabarito = pd.read_csv("gabarito_7ano_letras.csv")
gabarito_dict = {f'P. {int(row["Questão"])} Resposta': row["Gabarito"].strip().upper() for _, row in gabarito.iterrows()}
quest_cols = list(gabarito_dict.keys())

# Função para calcular taxa de acertos por questão
def calcular_taxa_acerto_por_questao(df_turma):
    total_alunos = len(df_turma)
    acertos = []
    for col in quest_cols:
        resposta_correta = gabarito_dict[col]
        respostas_alunos = df_turma[col].fillna('').astype(str).str.upper().str.strip()
        acertos_coluna = respostas_alunos == resposta_correta
        acertos.append(acertos_coluna.sum())
    taxas = [(ac / total_alunos) * 100 if total_alunos > 0 else 0 for ac in acertos]
    return taxas

# Instância do app Dash
app = Dash(__name__)
server = app.server  # Necessário para Render.com

# Layout do app
app.layout = html.Div([
    html.H2("📊 Desempenho por Questão - 7º Ano"),
    dcc.Dropdown(id='turma-dropdown',
                 options=[{"label": t, "value": t} for t in df["Nome da turma"].unique()],
                 value=df["Nome da turma"].iloc[0]),
    dcc.Graph(id='grafico')
])

# Callback do gráfico
@app.callback(Output("grafico", "figure"), Input("turma-dropdown", "value"))
def atualizar_grafico(turma):
    df_turma = df[df["Nome da turma"] == turma]
    taxas = calcular_taxa_acerto_por_questao(df_turma)
    quest_labels = [q.replace("P. ", "Q ").replace(" Resposta", "") for q in quest_cols]
    fig = px.bar(x=quest_labels, y=taxas,
                 labels={"x": "Questão", "y": "Taxa de Acerto (%)"},
                 text=[f"{t:.1f}%" for t in taxas])
    fig.update_traces(marker_color="black", textposition="outside",
                      textfont=dict(color="white", size=12), cliponaxis=False)
    fig.update_layout(yaxis_range=[0, 100], plot_bgcolor='white')
    return fig
