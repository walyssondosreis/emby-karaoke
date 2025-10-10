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

def run(log_callback=None, pasta_videos="Karaoke", arquivo_xlsx="assets/Songs.xls"):
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

    # Carrega as abas necessárias da planilha
    try:
        df_biblioteca = pd.read_excel(arquivo_xlsx, sheet_name='Biblioteca')
        df_karaoke = pd.read_excel(arquivo_xlsx, sheet_name='Karaoke')
        log("Carregadas abas 'Biblioteca' e 'Karaoke' da planilha Songs.xls")
    except Exception as e:
        log(f"Erro ao carregar planilha: {e}")
        return

    # Prepara os dados
    df_biblioteca['full_title'] = df_biblioteca['full_title'].astype(str).str.strip()

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

            # Busca correspondência na aba Biblioteca
            linha_biblioteca = df_biblioteca[df_biblioteca['full_title'].str.lower() == nome_busca.lower()]
            if not linha_biblioteca.empty:
                artista = escape_xml(str(linha_biblioteca.iloc[0]['artist']))
                titulo = escape_xml(str(linha_biblioteca.iloc[0]['title']))
                genero = escape_xml(str(linha_biblioteca.iloc[0]['genre']))
                world = escape_xml(str(linha_biblioteca.iloc[0]['world']))

                # Busca tags na aba Karaoke usando music_id
                music_id = linha_biblioteca.iloc[0]['music_id']
                linha_karaoke = df_karaoke[df_karaoke['music_id'] == music_id]
                
                tags = []
                
                # Adiciona world da Biblioteca como tag
                if world and str(world) != 'nan' and str(world).strip():
                    tags.append(str(world).strip())
                
                # Adiciona tags da aba Karaoke (tag_1, tag_2, etc.)
                if not linha_karaoke.empty:
                    for col in linha_karaoke.columns:
                        if col.startswith('tag_'):
                            tag_value = str(linha_karaoke.iloc[0][col])
                            if tag_value and tag_value != 'nan' and tag_value.strip():
                                tags.append(tag_value.strip())
                
                # Remove duplicatas e escapa tags
                tags_unicas = []
                for tag in tags:
                    tag_escapada = escape_xml(tag)
                    if tag_escapada not in tags_unicas:
                        tags_unicas.append(tag_escapada)

                # Define tag adicional com o nome da subpasta ou "Outro"
                subpasta = os.path.relpath(root, pasta_videos)
                if subpasta == ".":
                    tag_adicional = "Outro"
                else:
                    tag_adicional = escape_xml(subpasta)
                tags_unicas.append(tag_adicional)

                # Cria conteúdo NFO
                tags_xml = "\n  ".join([f"<tag>{tag}</tag>" for tag in tags_unicas])
                
                nfo_content = f'''<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<musicvideo>
  <artist>{artista}</artist>
  <title>{titulo}</title>
  <genre>{genero}</genre>
  {tags_xml}
</musicvideo>
'''

                # Salva arquivo NFO
                with open(nfo_path, "w", encoding="utf-8") as f:
                    f.write(nfo_content)

                log(f"NFO gerado: {nfo_path}")