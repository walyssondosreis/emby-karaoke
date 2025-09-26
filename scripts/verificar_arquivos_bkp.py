import os
import re
import pandas as pd
from datetime import datetime

PASTA_KARAOKE = "Karaoke"
PLANILHA = "karaoke.xlsx"

# Lista de extensões de vídeo
video_extensoes = {".mp4", ".mkv", ".avi", ".mov", ".flv", ".wmv", ".mpeg", ".webm"}

# Carrega planilha
df = pd.read_excel(PLANILHA)
df['full_title'] = df['full_title'].astype(str).str.strip()

# Função para normalizar nomes (remover vN)
def normalizar_nome(nome):
    return re.sub(r' v\d+$', '', nome, flags=re.IGNORECASE).strip().lower()

# Pega arquivos da pasta e cria mapeamento normalizado -> nome original
arquivos_pasta = {}
for arquivo in os.listdir(PASTA_KARAOKE):
    caminho = os.path.join(PASTA_KARAOKE, arquivo)
    if os.path.isfile(caminho):
        nome, ext = os.path.splitext(arquivo)
        if ext.lower() in video_extensoes:
            arquivos_pasta[normalizar_nome(nome)] = arquivo  # mantém nome completo com extensão

# Pega títulos da planilha e cria mapeamento normalizado -> título original
titulos_planilha = {}
for t in df['full_title'].tolist():
    t = t.strip()
    titulos_planilha[normalizar_nome(t)] = t

# Arquivos na pasta mas não na planilha
nao_na_planilha = [arquivos_pasta[n] for n in arquivos_pasta if n not in titulos_planilha]

# Arquivos na planilha mas não na pasta
nao_na_pasta = [titulos_planilha[n] for n in titulos_planilha if n not in arquivos_pasta]

# Nome do log com data e hora
agora = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_FILE = f"karaoke_verificar_{agora}.log"

# Gera log
with open(LOG_FILE, "w", encoding="utf-8") as log:
    log.write(f"Log gerado em: {datetime.now()}\n\n")
    
    log.write("Arquivos na pasta, mas não na planilha:\n")
    if nao_na_planilha:
        for a in nao_na_planilha:
            log.write(f"  {a}\n")
    else:
        log.write("  Nenhum\n")
    
    log.write("\nArquivos na planilha, mas não na pasta:\n")
    if nao_na_pasta:
        for t in nao_na_pasta:
            log.write(f"  {t}\n")
    else:
        log.write("  Nenhum\n")

print(f"Log gerado: {LOG_FILE}")
