
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

# Arquivos das turmas e gabarito
arquivos = [
    "7_ANO_-_03_DE_DEZEMBRO_2025_2026_75993.csv",
    "7º_ANO_-_ANTONIO_DE_SOUSA_BARROS_2025_2026_76019.csv",
    "7º_ANO_A_-_21_DE_DEZEMBRO_2025_2026_71725.csv",
    "7º_ANO_A_-_FIRMINO_JOSE_2025_2026_76239.csv",
    "7º_ANO_B_-_21_DE_DEZEMBRO_2025_2026_71726.csv",
    "7º_ANO_C_-_21_DE_DEZEMBRO_2025_2026_71728.csv"
]
df = pd.concat([pd.read_csv(f) for f in arquivos], ignore_index=True)

# Gabarito
gabarito = pd.read_csv("gabarito_7ano_letras.csv")
gabarito_dict = {f'P. {row["Questão"]} Resposta': row["Gabarito"].strip().upper() for _, row in gabarito.iterrows()}

# Colunas das questões
quest_cols = [col for col in df.columns if col in gabarito_dict]

# Função para calcular acertos exatos
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

# App
app = Dash(__name__)
app.title = "Acertos por Questão - 7º Ano"

# Layout
app.layout = html.Div(style={'fontFamily': 'Arial', 'padding': '30px'}, children=[
    html.H1("📊 Taxa de Acerto por Questão - 7º Ano", style={'textAlign': 'center'}),

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

    dcc.Graph(id='grafico-questoes')
])

@app.callback(
    Output('grafico-questoes', 'figure'),
    Input('turma-dropdown', 'value')
)
def atualizar_grafico(turma):
    df_turma = df[df['Nome da turma'] == turma]
    taxas = calcular_taxa_acerto_por_questao(df_turma)
    quest_labels = [col.replace("P. ", "Q").replace(" Resposta", "") for col in quest_cols]

    fig = px.bar(
        x=quest_labels,
        y=taxas,
        labels={'x': 'Questão', 'y': 'Taxa de Acerto (%)'},
        title=f"Taxa de Acertos por Questão - {turma}",
        template='plotly',
    )
    fig.update_traces(marker_color='#118ab2', textposition='none')

    fig.update_layout(
        yaxis_range=[0, 100],
        title_font_size=22,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )

    # Inserir as anotações com fundo proporcional ao texto
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
            # Simulando canto arredondado com borda leve e preenchimento pequeno
            xanchor="center",
            yanchor="bottom"
        )

    return fig

# Rodar o app
if __name__ == '__main__':
    app.run(debug=True)
    