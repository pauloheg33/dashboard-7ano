import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

# Carregando dados das turmas com metadados
def carregar_dados(caminho, escola, serie):
    df = pd.read_csv(caminho)
    df["Escola"] = escola
    df["Ano/Série"] = serie
    return df

dfs = [
    carregar_dados("7_ANO_-_03_DE_DEZEMBRO_2025_2026_75993.csv", "E.E.F 03 DE DEZEMBRO", "7º ANO"),
    carregar_dados("7º_ANO_-_ANTONIO_DE_SOUSA_BARROS_2025_2026_76019.csv", "E.E.F ANTONIO DE SOUSA BAROS", "6º ANO"),
    carregar_dados("7º_ANO_A_-_21_DE_DEZEMBRO_2025_2026_71725.csv", "E.E.F 21 DE DEZEMBRO", "7º ANO"),
    carregar_dados("7º_ANO_A_-_FIRMINO_JOSE_2025_2026_76239.csv", "E.E.F FIRMINO JOSÉ", "7º ANO")
]

df = pd.concat(dfs, ignore_index=True)

# Gabarito
gabarito = pd.read_csv("gabarito_7ano_letras.csv")
gabarito_dict = {f'P. {int(row["Questão"])} Resposta': row["Gabarito"].strip().upper() for _, row in gabarito.iterrows()}
quest_cols = [col for col in df.columns if col in gabarito_dict]

# Cálculo de acertos por questão
def calcular_taxa_acerto_por_questao(df_turma):
    total = len(df_turma)
    acertos = []
    for col in quest_cols:
        respostas = df_turma[col].fillna('').astype(str).str.upper().str.strip()
        acertos.append((respostas == gabarito_dict[col]).sum())
    return [(a / total) * 100 if total else 0 for a in acertos]

# App Dash
app = Dash(__name__)
server = app.server

app.layout = html.Div(style={'fontFamily': 'Segoe UI', 'padding': '30px', 'backgroundColor': '#f8f9fa'}, children=[
    html.H2("📊 Desempenho por Questão", style={'textAlign': 'center', 'color': '#2c3e50'}),

    html.Div([
        html.Label("Escola:", style={'fontWeight': 'bold'}),
        dcc.Dropdown(
            id='escola-dropdown',
            options=[{'label': esc, 'value': esc} for esc in sorted(df['Escola'].unique())],
            placeholder="Selecione a escola...",
            style={'marginBottom': '10px'}
        ),

        html.Label("Ano/Série:", style={'fontWeight': 'bold'}),
        dcc.Dropdown(id='serie-dropdown', placeholder="Selecione o ano/série...", style={'marginBottom': '10px'}),

        html.Label("Turma:", style={'fontWeight': 'bold'}),
        dcc.Dropdown(id='turma-dropdown', placeholder="Selecione a turma...")
    ], style={
        'width': '80%',
        'maxWidth': '600px',
        'margin': 'auto',
        'padding': '25px',
        'border': '1px solid #ccc',
        'borderRadius': '10px',
        'backgroundColor': '#ffffff',
        'boxShadow': '0 4px 8px rgba(0,0,0,0.05)'
    }),

    html.Br(),
    dcc.Graph(id='grafico-questoes')
])

@app.callback(
    Output('serie-dropdown', 'options'),
    Input('escola-dropdown', 'value')
)
def atualizar_series(escola):
    if escola:
        return [{'label': s, 'value': s} for s in ['6º ANO', '7º ANO', '8º ANO', '9º ANO'] if s in df[df['Escola'] == escola]['Ano/Série'].unique()]
    return []

@app.callback(
    Output('turma-dropdown', 'options'),
    [Input('escola-dropdown', 'value'), Input('serie-dropdown', 'value')]
)
def atualizar_turmas(escola, serie):
    if escola and serie:
        dff = df[(df['Escola'] == escola) & (df['Ano/Série'] == serie)]
        return [{'label': t, 'value': t} for t in sorted(dff['Nome da turma'].unique())]
    return []

@app.callback(
    Output('grafico-questoes', 'figure'),
    Input('turma-dropdown', 'value')
)
def atualizar_grafico(turma):
    dff = df[df['Nome da turma'] == turma]
    taxas = calcular_taxa_acerto_por_questao(dff)
    quest_labels = [col.replace("P. ", "Q").replace(" Resposta", "") for col in quest_cols]

    fig = px.bar(
        x=quest_labels,
        y=taxas,
        labels={'x': 'Questão', 'y': 'Taxa de Acerto (%)'},
        title=f"Taxa de Acertos - {turma}",
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

    fig.update_layout(yaxis_range=[0, 100])
    return fig

if __name__ == '__main__':
    app.run(debug=True)
