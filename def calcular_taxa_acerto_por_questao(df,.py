def calcular_taxa_acerto_por_questao(df, gabarito):
    num_questoes = 22 if df['Série'].iloc[0] in ['1º', '2º', '3º', '4º', '5º'] else 24  # ajuste conforme necessário
    gabarito = gabarito.iloc[0:num_questoes]
    gabarito = gabarito.dropna()
    
    # Calcular a taxa de acerto por questão
    taxa_acerto_por_questao = []
    for i in range(num_questoes):
        coluna_resposta = 'Q' + str(i+1)  # Supondo que as colunas de resposta sejam Q1, Q2, ..., QN
        acertos = df[df[coluna_resposta] == gabarito[i]].shape[0]
        total_alunos = df.shape[0]
        taxa_acerto = acertos / total_alunos if total_alunos > 0 else 0
        taxa_acerto_por_questao.append(taxa_acerto)
    
    return taxa_acerto_por_questao