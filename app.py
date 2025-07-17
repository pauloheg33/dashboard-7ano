import os
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

# Caminho base dos arquivos
BASE_PATH = os.path.dirname(__file__)

# Carregar dados com verificação
def carregar_dados(nome_arquivo, escola, serie, componente):
    caminho = os.path.join(BASE_PATH, nome_arquivo)
    if not os.path.exists(caminho):
        print(f"❌ Arquivo não encontrado: {nome_arquivo}")
        return None
    df = pd.read_csv(caminho)
    df["Escola"] = escola
    df["Ano/Série"] = serie
    df["Componente"] = componente
    return df

# Lista segura de arquivos
arquivos = [
    ("7_ANO_-_03_DE_DEZEMBRO_2025_2026_75993.csv", "E.E.F 03 DE DEZEMBRO", "7º ANO", "Matemática"),
    ("7º_ANO_-_ANTONIO_DE_SOUSA_BARROS_2025_2026_76019.csv", "E.E.F ANTONIO DE SOUSA BARROS", "7º ANO", "Matemática"),
    ("7º_ANO_A_-_21_DE_DEZEMBRO_2025_2026_71725.csv", "E.E.F 21 DE DEZEMBRO", "7º ANO", "Matemática"),
    ("7º_ANO_A_-_FIRMINO_JOSE_2025_2026_76239.csv", "E.E.F FIRMINO JOSÉ", "7º ANO", "Matemática"),
    ("7º_ANO_B_-_21_DE_DEZEMBRO_2025_2026_71726.csv", "E.E.F 21 DE DEZEMBRO", "7º ANO", "Matemática"),
    ("7º_ANO_C_-_21_DE_DEZEMBRO_2025_2026_71728.csv", "E.E.F 21 DE DEZEMBRO", "7º ANO", "Matemática")
]

dfs = [carregar_dados(*arq) for arq in arquivos]
dfs = [df for df in dfs if df is not None]
df = pd.concat(dfs, ignore_index=True)

# Gabarito
gabarito_path = os.path.join(BASE_PATH, "gabarito_7ano_letras.csv")
gabarito = pd.read_csv(gabarito_path)
gabarito_dict = {f'P. {int(row["Questão"])} Resposta': row["Gabarito"].strip().upper() for _, row in gabarito.iterrows()}
quest_cols = [col for col in df.columns if col in gabarito_dict]

def calcular_taxa_acerto_por_questao(df_turma):
    total = len(df_turma)
    acertos = []
    for col in quest_cols:
        respostas = df_turma[col].fillna('').astype(str).str.upper().str.strip()
        acertos.append((respostas == gabarito_dict[col]).sum())
    return [(a / total) * 100 if total else 0 for a in acertos]

app = Dash(__name__)
server = app.server

app.layout = html.Div(style={'fontFamily': 'Segoe UI', 'padding': '30px', 'backgroundColor': '#f8f9fa'}, children=[
    html.H2("📊 Desempenho por Questão", style={'textAlign': 'center', 'color': '#2c3e50'}),
    html.Div([
        html.Div([
            html.Label("Escola:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='escola-dropdown',
                options=[{'label': esc, 'value': esc} for esc in sorted(df['Escola'].dropna().unique())],
                placeholder="Selecione a escola...",
                style={'width': '100%'}
            )
        ], style={'width': '24%', 'display': 'inline-block', 'paddingRight': '10px'}),
        html.Div([
            html.Label("Ano/Série:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(id='serie-dropdown', placeholder="Selecione o ano/série...", style={'width': '100%'})
        ], style={'width': '24%', 'display': 'inline-block', 'paddingRight': '10px'}),
        html.Div([
            html.Label("Turma:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(id='turma-dropdown', placeholder="Selecione a turma...", style={'width': '100%'})
        ], style={'width': '24%', 'display': 'inline-block', 'paddingRight': '10px'}),
        html.Div([
            html.Label("Componente:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='componente-dropdown',
                options=[{'label': c, 'value': c} for c in sorted(df['Componente'].dropna().unique())],
                placeholder="Selecione o componente...",
                style={'width': '100%'}
            )
        ], style={'width': '24%', 'display': 'inline-block'})
    ], style={'width': '100%', 'margin': 'auto', 'padding': '25px 10px', 'border': '1px solid #ccc',
              'borderRadius': '10px', 'backgroundColor': '#ffffff', 'boxShadow': '0 4px 8px rgba(0,0,0,0.05)',
              'marginBottom': '30px'}),
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
        return [{'label': s, 'value': s} for s in sorted(series)]
    return []

@app.callback(
    Output('turma-dropdown', 'options'),
    [Input('escola-dropdown', 'value'), Input('serie-dropdown', 'value')]
)
def atualizar_turmas(escola, serie):
    if escola and serie:
        dff = df[(df['Escola'] == escola) & (df['Ano/Série'] == serie)]
        return [{'label': t, 'value': t} for t in sorted(dff['Nome da turma'].dropna().unique())]
    return []

@app.callback(
    Output('grafico-questoes', 'figure'),
    [Input('turma-dropdown', 'value'), Input('componente-dropdown', 'value')]
)
def atualizar_grafico(turma, componente):
    dff = df[(df['Nome da turma'] == turma) & (df['Componente'] == componente)]
    taxas = calcular_taxa_acerto_por_questao(dff)
    quest_labels = [col.replace("P. ", "Q").replace(" Resposta", "") for col in quest_cols]

    fig = px.bar(
        x=quest_labels,
        y=taxas,
        labels={'x': 'Questão', 'y': 'Taxa de Acerto (%)'},
        title=f"Taxa de Acertos - {turma} ({componente})",
        template='plotly_white'
    )
    fig.update_traces(marker_color='#118ab2')

    for i, pct in enumerate(taxas):
        fig.add_annotation(
            x=quest_labels[i],
            y=pct + 2,
            text=f"{pct:.1f}%",
            showarrow=False,
            font=dict(color="white", size=12),
            align="center",
            bgcolor="black",
            borderpad=4,
            borderwidth=0,
            opacity=1,
            xanchor="center",
            yanchor="bottom"
        )

    if taxas:
        media_geral = sum(taxas) / len(taxas)
        fig.add_shape(
            type='line',
            x0=-0.5,
            x1=len(taxas) - 0.5,
            y0=media_geral,
            y1=media_geral,
            line=dict(color='red', dash='dash', width=2)
        )
        fig.add_annotation(
            x=0,
            y=media_geral + 15,
            text=f"Média: {media_geral:.1f}%",
            showarrow=False,
            font=dict(color="red", size=14),
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="red",
            borderwidth=1,
            xanchor="left",
            yanchor="bottom"
        )

    fig.update_layout(yaxis_range=[0, 100])
    return fig

if __name__ == '__main__':
    app.run(debug=True, port=8051)
