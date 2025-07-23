import os
import glob
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

BASE_PATH = os.path.dirname(__file__)

# Carregar todos os arquivos CSV das turmas (7º ano + results_*)
arquivos_7ano = [
    "7_ANO_-_03_DE_DEZEMBRO_2025_2026_75993.csv",
    "7º_ANO_-_ANTONIO_DE_SOUSA_BARROS_2025_2026_76019.csv",
    "7º_ANO_A_-_21_DE_DEZEMBRO_2025_2026_71725.csv",
    "7º_ANO_A_-_FIRMINO_JOSE_2025_2026_76239.csv",
    "7º_ANO_B_-_21_DE_DEZEMBRO_2025_2026_71726.csv",
    "7º_ANO_C_-_21_DE_DEZEMBRO_2025_2026_71728.csv"
]
dfs = []
for nome_arquivo in arquivos_7ano:
    caminho = os.path.join(BASE_PATH, nome_arquivo)
    if os.path.exists(caminho):
        dfs.append(pd.read_csv(caminho))

# Novos arquivos das pastas results_*
for arquivo in glob.glob(os.path.join(BASE_PATH, "results_*", "*.csv")):
    dfs.append(pd.read_csv(arquivo))

df = pd.concat(dfs, ignore_index=True)

# Gabaritos por série e componente
gabaritos = {}
for serie in df['Ano/Série'].unique():
    for componente in df['Componente'].unique():
        gabarito_nome = f"gabarito_{serie.lower().replace('º ano','').replace(' ','').replace('/','')}_{componente.lower()}.csv"
        gabarito_path = os.path.join(BASE_PATH, gabarito_nome)
        if os.path.exists(gabarito_path):
            gabarito_df = pd.read_csv(gabarito_path)
            gabarito_dict = {f'P. {int(row["Questão"])} Resposta': row["Gabarito"].strip().upper() for _, row in gabarito_df.iterrows()}
            gabaritos[(serie, componente)] = gabarito_dict

def get_quest_cols(serie, componente):
    gabarito_dict = gabaritos.get((serie, componente))
    if not gabarito_dict:
        return []
    return [col for col in df.columns if col in gabarito_dict]

def calcular_taxa_acerto_por_questao(df_turma, serie, componente):
    gabarito_dict = gabaritos.get((serie, componente))
    quest_cols = get_quest_cols(serie, componente)
    if not gabarito_dict or not quest_cols:
        return [], []
    total = len(df_turma)
    acertos = []
    for col in quest_cols:
        respostas = df_turma[col].fillna('').astype(str).str.upper().str.strip()
        acertos.append((respostas == gabarito_dict[col]).sum())
    taxas = [(a / total) * 100 if total else 0 for a in acertos]
    quest_labels = [col.replace("P. ", "Q").replace(" Resposta", "") for col in quest_cols]
    return taxas, quest_labels

app = Dash(__name__)
app.title = "Acertos por Questão - Ensino Fundamental"

# Layout
app.layout = html.Div(style={'fontFamily': 'Arial', 'padding': '30px'}, children=[
    html.H1("📊 Taxa de Acerto por Questão", style={'textAlign': 'center'}),
    html.Div([
        html.Label("Selecione a série:", style={'fontSize': '16px'}),
        dcc.Dropdown(
            id='serie-dropdown',
            options=[{'label': s, 'value': s} for s in sorted(df['Ano/Série'].dropna().unique())],
            value=sorted(df['Ano/Série'].dropna().unique())[0],
            clearable=False,
            style={'width': '100%'}
        ),
    ], style={'width': '40%', 'margin': '0 auto'}),
    html.Br(),
    html.Div([
        html.Label("Selecione o componente:", style={'fontSize': '16px'}),
        dcc.Dropdown(
            id='componente-dropdown',
            options=[{'label': c, 'value': c} for c in sorted(df['Componente'].dropna().unique())],
            value=sorted(df['Componente'].dropna().unique())[0],
            clearable=False,
            style={'width': '100%'}
        ),
    ], style={'width': '40%', 'margin': '0 auto'}),
    html.Br(),
    html.Div([
        html.Label("Selecione a turma:", style={'fontSize': '16px'}),
        dcc.Dropdown(
            id='turma-dropdown',
            options=[],
            value=None,
            clearable=False,
            style={'width': '100%'}
        ),
    ], style={'width': '40%', 'margin': '0 auto'}),
    html.Br(),
    dcc.Graph(id='grafico-questoes')
])

@app.callback(
    Output('turma-dropdown', 'options'),
    [Input('serie-dropdown', 'value'), Input('componente-dropdown', 'value')]
)
def atualizar_turmas(serie, componente):
    if serie and componente:
        turmas = df[(df['Ano/Série'] == serie) & (df['Componente'] == componente)]['Nome da turma'].dropna().unique()
        return [{'label': t, 'value': t} for t in sorted(turmas)]
    return []

@app.callback(
    Output('turma-dropdown', 'value'),
    [Input('turma-dropdown', 'options')]
)
def selecionar_primeira_turma(options):
    if options:
        return options[0]['value']
    return None

@app.callback(
    Output('grafico-questoes', 'figure'),
    [Input('serie-dropdown', 'value'), Input('componente-dropdown', 'value'), Input('turma-dropdown', 'value')]
)
def atualizar_grafico(serie, componente, turma):
    if not (serie and componente and turma):
        return px.bar(title="Selecione todos os filtros para visualizar o gráfico.")
    df_turma = df[(df['Ano/Série'] == serie) & (df['Componente'] == componente) & (df['Nome da turma'] == turma)]
    taxas, quest_labels = calcular_taxa_acerto_por_questao(df_turma, serie, componente)
    if not taxas:
        return px.bar(title="Gabarito não encontrado ou dados insuficientes.")
    fig = px.bar(
        x=quest_labels,
        y=taxas,
        labels={'x': 'Questão', 'y': 'Taxa de Acerto (%)'},
        title=f"Taxa de Acertos por Questão - {turma} ({serie} - {componente})",
        template='plotly_white',
    )
    fig.update_traces(marker_color='#118ab2', textposition='none')
    fig.update_layout(
        yaxis_range=[0, 100],
        title_font_size=22,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    for i, pct in enumerate(taxas):
        fig.add_annotation(
            x=quest_labels[i],
            y=pct + 2,
            text=f"{pct:.1f}%",
            showarrow=False,
            font=dict(color="white", size=13),
            align="center",
            bgcolor="black",
            bordercolor="black",
            borderpad=2,
            opacity=1.0,
            borderwidth=0,
            xanchor="center",
            yanchor="bottom"
        )
    return fig

if __name__ == '__main__':
    app.run(debug=True)
