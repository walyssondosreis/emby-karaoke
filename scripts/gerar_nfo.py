import os
import re
import pandas as pd
from datetime import datetime

# --- Padrão de logs ---
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Função para escapar '&' no XML
def escape_xml(texto):
    return texto.replace("&", "&amp;")

def run(log_callback=None, pasta_videos="Karaoke", arquivo_xlsx="assets/karaoke.xlsx"):
    # Arquivo de log
    agora = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(LOG_DIR, f"karaoke_gerar_nfo_{agora}.log")

    def log(msg):
        if log_callback:
            log_callback(msg)
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(msg + "\n")

    # Verifica se pasta e arquivo existem
    if not os.path.exists(pasta_videos):
        log(f"Pasta não encontrada: {pasta_videos}")
        return
    if not os.path.exists(arquivo_xlsx):
        log(f"Arquivo XLSX não encontrado: {arquivo_xlsx}")
        return

    # Carrega planilha
    df = pd.read_excel(arquivo_xlsx)
    df['full_title'] = df['full_title'].astype(str).str.strip()

    # Percorre arquivos e subpastas
    for root, dirs, files in os.walk(pasta_videos):
        for arquivo in files:
            nome, ext = os.path.splitext(arquivo)
            if ext.lower() == ".jpg":
                continue  # ignora imagens

            caminho_arquivo = os.path.join(root, arquivo)
            nfo_path = os.path.join(root, nome + ".nfo")
            if os.path.exists(nfo_path):
                log(f"NFO já existe, ignorando: {arquivo}")
                continue

            # Remove vN para busca
            nome_busca = re.sub(r' v\d+$', '', nome, flags=re.IGNORECASE).strip()

            # Busca correspondência na planilha
            linha = df[df['full_title'].str.lower() == nome_busca.lower()]
            if not linha.empty:
                artista = escape_xml(str(linha.iloc[0]['artist']))
                titulo = escape_xml(str(linha.iloc[0]['title']))
                genero = escape_xml(str(linha.iloc[0]['genre']))
                tag_original = escape_xml(str(linha.iloc[0]['tag']))

                # Define tag adicional com o nome da subpasta ou "Outro"
                subpasta = os.path.relpath(root, pasta_videos)
                if subpasta == ".":
                    tag_adicional = "Outro"
                else:
                    tag_adicional = escape_xml(subpasta)

                # Cria conteúdo NFO
                nfo_content = f'''<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<musicvideo>
  <artist>{artista}</artist>
  <title>{titulo}</title>
  <genre>{genero}</genre>
  <tag>{tag_original}</tag>
  <tag>{tag_adicional}</tag>
</musicvideo>
'''

                # Salva arquivo NFO
                with open(nfo_path, "w", encoding="utf-8") as f:
                    f.write(nfo_content)

                log(f"NFO gerado: {nfo_path}")
