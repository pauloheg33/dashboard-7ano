import os
import glob
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

BASE_PATH = os.path.dirname(__file__)

def carregar_todos_dados():
    dfs = []
    escolas_encontradas = set()
    # Arquivos antigos (7º ano)
    arquivos_7ano = [
        ("7_ANO_-_03_DE_DEZEMBRO_2025_2026_75993.csv", "E.E.F 03 DE DEZEMBRO", "7º ANO", "Matemática"),
        ("7º_ANO_-_ANTONIO_DE_SOUSA_BARROS_2025_2026_76019.csv", "E.E.F ANTONIO DE SOUSA BARROS", "7º ANO", "Matemática"),
        ("7º_ANO_A_-_21_DE_DEZEMBRO_2025_2026_71725.csv", "E.E.F 21 DE DEZEMBRO", "7º ANO", "Matemática"),
        ("7º_ANO_A_-_FIRMINO_JOSE_2025_2026_76239.csv", "E.E.F FIRMINO JOSÉ", "7º ANO", "Matemática"),
        ("7º_ANO_B_-_21_DE_DEZEMBRO_2025_2026_71726.csv", "E.E.F 21 DE DEZEMBRO", "7º ANO", "Matemática"),
        ("7º_ANO_C_-_21_DE_DEZEMBRO_2025_2026_71728.csv", "E.E.F 21 DE DEZEMBRO", "7º ANO", "Matemática")
    ]
    for nome_arquivo, escola, serie, componente in arquivos_7ano:
        caminho = os.path.join(BASE_PATH, nome_arquivo)
        if os.path.exists(caminho):
            df = pd.read_csv(caminho)
            df["Escola"] = escola
            df["Ano/Série"] = serie
            df["Componente"] = componente
            escolas_encontradas.add(escola)
            dfs.append(df)
    # Novos arquivos das pastas results_*
    for arquivo in glob.glob(os.path.join(BASE_PATH, "results_*", "*.csv")):
        df = pd.read_csv(arquivo)
        # Tenta identificar o nome correto da escola
        if "Escola" in df.columns:
            escola = df["Escola"].iloc[0].strip().upper()
        else:
            # Tenta extrair do nome do arquivo
            nome = os.path.basename(arquivo)
            partes = nome.replace(".csv", "").split("_")
            escola = " ".join(partes[3:]).replace("-", " ").upper() if len(partes) > 3 else "DESCONHECIDO"
        df["Escola"] = escola
        escolas_encontradas.add(escola)
        # Série
        if "Ano/Série" in df.columns:
            serie = df["Ano/Série"].iloc[0]
        else:
            partes = nome.replace(".csv", "").split("_")
            serie = partes[1].replace("ano", "º ANO") if len(partes) > 1 else "Desconhecido"
        df["Ano/Série"] = serie
        # Componente
        if "Componente" in df.columns:
            componente = df["Componente"].iloc[0]
        else:
            componente = "Português" if "portugues" in nome.lower() else "Matemática"
        df["Componente"] = componente
        dfs.append(df)
    if dfs:
        df_final = pd.concat(dfs, ignore_index=True)
        escolas_registradas = sorted({e.strip().upper() for e in df_final['Escola'].dropna().unique()})
        return df_final, escolas_registradas
    return pd.DataFrame(), []

df, ESCOLAS = carregar_todos_dados()
SERIES = [f"{i}º ANO" for i in range(1, 10)]

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
server = app.server

app.layout = html.Div(style={'fontFamily': 'Segoe UI', 'padding': '30px', 'backgroundColor': '#f8f9fa'}, children=[
    html.H2("📊 Desempenho por Questão", style={'textAlign': 'center', 'color': '#2c3e50'}),
    html.Div([
        html.Div([
            html.Label("Escola:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='escola-dropdown',
                options=[{'label': esc.title(), 'value': esc} for esc in ESCOLAS],
                placeholder="Selecione a escola...",
                style={'width': '100%'}
            )
        ], style={'width': '24%', 'display': 'inline-block', 'paddingRight': '10px'}),
        html.Div([
            html.Label("Ano/Série:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='serie-dropdown',
                options=[{'label': s, 'value': s} for s in SERIES],
                placeholder="Selecione o ano/série...",
                style={'width': '100%'}
            )
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
        # Garante que só aparecem séries do 1º ao 9º ano
        series = [s for s in series if s in SERIES]
        return [{'label': s, 'value': s} for s in sorted(series, key=lambda x: SERIES.index(x))]
    return [{'label': s, 'value': s} for s in SERIES]

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
    [Input('escola-dropdown', 'value'), Input('serie-dropdown', 'value'), Input('turma-dropdown', 'value'), Input('componente-dropdown', 'value')]
)
def atualizar_grafico(escola, serie, turma, componente):
    if not (escola and serie and turma and componente):
        return px.bar(title="Selecione todos os filtros para visualizar o gráfico.")
    dff = df[(df['Escola'] == escola) & (df['Ano/Série'] == serie) & (df['Nome da turma'] == turma) & (df['Componente'] == componente)]
    taxas, quest_labels = calcular_taxa_acerto_por_questao(dff, serie, componente)
    if not taxas:
        return px.bar(title="Gabarito não encontrado ou dados insuficientes.")
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
