import os
import re
import pandas as pd

PASTA_KARAOKE = "Karaoke"
PLANILHA = "Karaoke.xlsx"

# Carrega planilha
df = pd.read_excel(PLANILHA)
df['full_title'] = df['full_title'].astype(str).str.strip()

# Função para substituir '&' por '&amp;'
def escape_xml(texto):
    return texto.replace("&", "&amp;")

# Varre arquivos da pasta
for arquivo in os.listdir(PASTA_KARAOKE):
    caminho = os.path.join(PASTA_KARAOKE, arquivo)
    if os.path.isfile(caminho):
        nome, ext = os.path.splitext(arquivo)
        if ext.lower() == ".jpg":
            continue  # ignora imagens

        # Verifica se NFO já existe
        nfo_path = os.path.join(PASTA_KARAOKE, nome + ".nfo")
        if os.path.exists(nfo_path):
            print(f"NFO já existe, ignorando: {arquivo}")
            continue

        # Verifica se termina com vN
        match_vn = re.search(r' v\d+$', nome, re.IGNORECASE)
        if match_vn:
            # Para busca no Excel, remove "vN"
            nome_busca = re.sub(r' v\d+$', '', nome, flags=re.IGNORECASE).strip()
        else:
            nome_busca = nome.strip()

        # Busca correspondência na planilha
        linha = df[df['full_title'].str.lower() == nome_busca.lower()]
        if not linha.empty:
            artista = escape_xml(str(linha.iloc[0]['artist']))
            titulo = escape_xml(str(linha.iloc[0]['title']))
            genero = escape_xml(str(linha.iloc[0]['genre']))
            tag = escape_xml(str(linha.iloc[0]['tag']))

            # Cria conteúdo NFO
            nfo_content = f'''<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<musicvideo>
  <artist>{artista}</artist>
  <title>{titulo}</title>
  <genre>{genero}</genre>
  <tag>{tag}</tag>
</musicvideo>
'''

            # Salva arquivo .nfo com o MESMO nome do arquivo
            with open(nfo_path, "w", encoding="utf-8") as f:
                f.write(nfo_content)

            print(f"NFO gerado: {nfo_path}")
