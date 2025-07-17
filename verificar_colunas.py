import pandas as pd

# Lista dos arquivos CSV
arquivos = [
    "7_ANO_-_03_DE_DEZEMBRO_2025_2026_75993.csv",
    "7º_ANO_-_ANTONIO_DE_SOUSA_BARROS_2025_2026_76019.csv",
    "7º_ANO_A_-_21_DE_DEZEMBRO_2025_2026_71725.csv",
    "7º_ANO_A_-_FIRMINO_JOSE_2025_2026_76239.csv",
    "7º_ANO_B_-_21_DE_DEZEMBRO_2025_2026_71726.csv",
    "7º_ANO_C_-_21_DE_DEZEMBRO_2025_2026_71728.csv"
]

# Lê os arquivos e concatena
df = pd.concat([pd.read_csv(f) for f in arquivos], ignore_index=True)

# Exibe as colunas
print("🔍 Colunas disponíveis nos CSVs:")
for col in df.columns:
    print(f"- '{col}'")