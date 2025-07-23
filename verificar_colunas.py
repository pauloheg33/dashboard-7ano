import os
import glob
import pandas as pd

BASE_PATH = os.path.dirname(__file__)

# Lista dos arquivos CSV antigos (7º ano)
arquivos_7ano = [
    "7_ANO_-_03_DE_DEZEMBRO_2025_2026_75993.csv",
    "7º_ANO_-_ANTONIO_DE_SOUSA_BARROS_2025_2026_76019.csv",
    "7º_ANO_A_-_21_DE_DEZEMBRO_2025_2026_71725.csv",
    "7º_ANO_A_-_FIRMINO_JOSE_2025_2026_76239.csv",
    "7º_ANO_B_-_21_DE_DEZEMBRO_2025_2026_71726.csv",
    "7º_ANO_C_-_21_DE_DEZEMBRO_2025_2026_71728.csv"
]
arquivos = [os.path.join(BASE_PATH, f) for f in arquivos_7ano if os.path.exists(os.path.join(BASE_PATH, f))]

# Adiciona arquivos das novas pastas results_*
arquivos += glob.glob(os.path.join(BASE_PATH, "results_*", "*.csv"))

# Lê os arquivos e concatena
df = pd.concat([pd.read_csv(f) for f in arquivos], ignore_index=True)

# Exibe as colunas
print("🔍 Colunas disponíveis nos CSVs:")
for col in df.columns:
    print(f"- '{col}'")