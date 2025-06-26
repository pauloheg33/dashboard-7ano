
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

# Lista de arquivos das turmas do 7º ano
arquivos = [
    "7_ANO_-_03_DE_DEZEMBRO_2025_2026_75993.csv",
    "7º_ANO_-_ANTONIO_DE_SOUSA_BARROS_2025_2026_76019.csv",
    "7º_ANO_A_-_21_DE_DEZEMBRO_2025_2026_71725.csv",
    "7º_ANO_A_-_FIRMINO_JOSE_2025_2026_76239.csv",
    "7º_ANO_B_-_21_DE_DEZEMBRO_2025_2026_71726.csv",
    "7º_ANO_C_-_21_DE_DEZEMBRO_2025_2026_71728.csv"
]

# Carrega e junta todos os arquivos
df = pd.concat([pd.read_csv(f) for f in arquivos], ignore_index=True)

# Selecionar colunas das questões
colunas_questoes = [col for col in df.columns if "Resposta" in col]

# Função de acerto: considera "Correta" como acerto
def contar_acertos(df_sub):
    return [df_sub[col].str.lower().str.strip().eq("correta").sum() for col in colunas_questoes]

# App
app = Dash(__name__)
app.title = "Desempenho por Questão"

# Layout
app.layout = html.Div(style={'fontFamily': 'Arial', 'padding': '30px'}, children=[
    html.H1("📚 Desempenho por Questão - Avaliação 7º Ano", style={'textAlign': 'center'}),

    html.Div([
        html.Label("Selecione uma turma:", style={'fontSize': '18px'}),
        dcc.Dropdown(
            id='turma-dropdown',
            options=[{'label': turma, 'value': turma} for turma in sorted(df['Nome da turma'].dropna().unique())],
            value=sorted(df['Nome da turma'].dropna().unique())[0],
            clearable=False,
            style={'width': '100%'}
        ),
    ], style={'width': '50%', 'margin': '0 auto'}),

    html.Br(),

    html.Div([
        dcc.Graph(id='grafico-questoes')
    ])
])

# Callback
@app.callback(
    Output('grafico-questoes', 'figure'),
    Input('turma-dropdown', 'value')
)
def atualizar_grafico(turma):
    df_turma = df[df['Nome da turma'] == turma]
    acertos = contar_acertos(df_turma)
    total = df_turma.shape[0]
    porcentagens = [(a / total) * 100 if total > 0 else 0 for a in acertos]
    labels = [col.replace("P. ", "Q").replace(" Resposta", "") for col in colunas_questoes]

    fig = px.bar(
        x=labels,
        y=porcentagens,
        labels={'x': 'Questão', 'y': 'Taxa de Acerto (%)'},
        title=f"Taxa de Acertos por Questão - {turma}",
        template='plotly',
        text=[f"{p:.1f}%" for p in porcentagens]
    )
    fig.update_traces(marker_color='#0077b6', textposition='outside')
    fig.update_layout(yaxis_range=[0, 100], title_font_size=22)

    return fig

# Executar app
if __name__ == '__main__':
    app.run(debug=True)

