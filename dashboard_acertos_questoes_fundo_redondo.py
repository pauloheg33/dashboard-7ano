import os
import glob
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

BASE_PATH = os.path.dirname(__file__)

arquivos = glob.glob(os.path.join(BASE_PATH, "*.csv")) + glob.glob(os.path.join(BASE_PATH, "results_*", "*.csv"))
dfs = []
for f in arquivos:
    try:
        dfs.append(pd.read_csv(f))
    except Exception:
        pass

if dfs:
    df = pd.concat(dfs, ignore_index=True)
    df["Escola"] = df["Escola"].str.strip().str.upper()
    df["Ano/Série"] = df["Ano/Série"].str.strip().str.upper()
    df["Componente"] = df["Componente"].str.strip().str.capitalize()
else:
    df = pd.DataFrame(columns=["Escola", "Ano/Série", "Componente", "Nome da turma"])

ESCOLAS = sorted(df['Escola'].dropna().unique())
SERIES = [f"{i}º ANO" for i in range(1, 10)]

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

app.layout = html.Div(style={'fontFamily': 'Arial', 'padding': '30px'}, children=[
    html.H1("📊 Taxa de Acerto por Questão", style={'textAlign': 'center'}),
    html.Div([
        html.Label("Selecione a escola:", style={'fontSize': '16px'}),
        dcc.Dropdown(
            id='escola-dropdown',
            options=[{'label': esc.title(), 'value': esc} for esc in ESCOLAS],
            value=ESCOLAS[0] if ESCOLAS else None,
            clearable=False,
            style={'width': '100%'}
        ),
    ], style={'width': '40%', 'margin': '0 auto'}),
    html.Br(),
    html.Div([
        html.Label("Selecione a série:", style={'fontSize': '16px'}),
        dcc.Dropdown(
            id='serie-dropdown',
            options=[{'label': s, 'value': s} for s in SERIES],
            value=SERIES[0],
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
            value=sorted(df['Componente'].dropna().unique())[0] if not df.empty else None,
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
    Output('serie-dropdown', 'options'),
    Input('escola-dropdown', 'value')
)
def atualizar_series(escola):
    if escola:
        series = df[df['Escola'] == escola]['Ano/Série'].unique()
        series = [s for s in series if s in SERIES]
        return [{'label': s, 'value': s} for s in sorted(series, key=lambda x: SERIES.index(x))]
    return [{'label': s, 'value': s} for s in SERIES]

@app.callback(
    Output('componente-dropdown', 'options'),
    [Input('escola-dropdown', 'value'), Input('serie-dropdown', 'value')]
)
def atualizar_componentes(escola, serie):
    if escola and serie:
        comps = df[(df['Escola'] == escola) & (df['Ano/Série'] == serie)]['Componente'].dropna().unique()
        return [{'label': c, 'value': c} for c in sorted(comps)]
    return []

@app.callback(
    Output('turma-dropdown', 'options'),
    [Input('escola-dropdown', 'value'), Input('serie-dropdown', 'value'), Input('componente-dropdown', 'value')]
)
def atualizar_turmas(escola, serie, componente):
    if escola and serie and componente:
        turmas = df[(df['Escola'] == escola) & (df['Ano/Série'] == serie) & (df['Componente'] == componente)]['Nome da turma'].dropna().unique()
        return [{'label': t, 'value': t} for t in sorted(turmas)]
    return []

@app.callback(
    Output('grafico-questoes', 'figure'),
    [Input('escola-dropdown', 'value'), Input('serie-dropdown', 'value'), Input('componente-dropdown', 'value'), Input('turma-dropdown', 'value')]
)
def atualizar_grafico(escola, serie, componente, turma):
    if not (escola and serie and componente and turma):
        return px.bar(title="Selecione todos os filtros para visualizar o gráfico.")
    df_turma = df[(df['Escola'] == escola) & (df['Ano/Série'] == serie) & (df['Componente'] == componente) & (df['Nome da turma'] == turma)]
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
