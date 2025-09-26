import os
import math
import pandas as pd
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from scripts.verificar_arquivos import normalizar_nome  # reutiliza função de normalização

# Pastas de fontes
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONTS_DIR = os.path.join(BASE_DIR, "..", "assets", "fonts")
FONT_MUSICA_BOLD = os.path.join(FONTS_DIR, "Montserrat-Bold.ttf")
FONT_ARTISTA_REGULAR = os.path.join(FONTS_DIR, "OpenSans-Regular.ttf")
FONT_KARAOKE_BOLD = os.path.join(FONTS_DIR, "OpenSans-Bold.ttf")

# Pasta de logs
LOG_DIR = os.path.join(BASE_DIR, "..", "logs")
os.makedirs(LOG_DIR, exist_ok=True)

def gerar_capa(nome_arquivo, pasta_base, titulo=None, artista=None, log_callback=None):
    base, _ = os.path.splitext(nome_arquivo)
    
    if not titulo or not artista:
        if " - " in base:
            artista, titulo = base.split(" - ", 1)
        else:
            artista = "Desconhecido"
            titulo = base
            if log_callback:
                log_callback(f"Formato inválido (esperado 'Artista - Música'): {nome_arquivo}")
    
    titulo = titulo.split(" v")[0].strip()
    
    largura, altura = 1280, 720
    img = Image.new("RGB", (largura, altura), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Fundo gradiente
    cor_topo = (20, 20, 20)
    cor_base = (0, 0, 0)
    for y in range(altura):
        r = int(cor_topo[0] + (cor_base[0] - cor_topo[0]) * (y / altura))
        g = int(cor_topo[1] + (cor_base[1] - cor_topo[1]) * (y / altura))
        b = int(cor_topo[2] + (cor_base[2] - cor_topo[2]) * (y / altura))
        draw.line([(0, y), (largura, y)], fill=(r, g, b))

    # Carregar fontes
    try:
        fonte_karaoke = ImageFont.truetype(FONT_KARAOKE_BOLD, 60)
        fonte_musica = ImageFont.truetype(FONT_MUSICA_BOLD, 160)
        fonte_artista = ImageFont.truetype(FONT_ARTISTA_REGULAR, 80)
    except IOError as e:
        if log_callback:
            log_callback(f"Erro ao carregar fontes: {e}")
        fonte_karaoke = fonte_musica = fonte_artista = ImageFont.load_default()

    # Função para quebrar texto
    def texto_quebrado(draw_obj, texto, fonte, max_largura):
        linhas = []
        palavras = texto.split()
        linha_atual = ""
        for palavra in palavras:
            teste = linha_atual + (" " if linha_atual else "") + palavra
            largura_texto = draw_obj.textbbox((0,0), teste, font=fonte)[2]
            if largura_texto <= max_largura:
                linha_atual = teste
            else:
                if linha_atual:
                    linhas.append(linha_atual)
                linha_atual = palavra
        if linha_atual:
            linhas.append(linha_atual)
        return linhas

    margem = 80
    max_largura = largura - 2 * margem

    # Texto "KARAOKÊ"
    w_topo = draw.textbbox((0,0), "KARAOKÊ", font=fonte_karaoke)[2]
    draw.text(((largura - w_topo)/2, 40), "KARAOKÊ", font=fonte_karaoke, fill="white")

    linhas_titulo = texto_quebrado(draw, titulo, fonte_musica, max_largura)
    linhas_artista = texto_quebrado(draw, artista, fonte_artista, max_largura)

    y_inicio = 200
    for linha in linhas_titulo:
        w = draw.textbbox((0,0), linha, font=fonte_musica)[2]
        draw.text(((largura - w)/2, y_inicio), linha, font=fonte_musica, fill="yellow")
        y_inicio += draw.textbbox((0,0), linha, font=fonte_musica)[3] - draw.textbbox((0,0), linha, font=fonte_musica)[1]

    y_inicio += 30
    for linha in linhas_artista:
        w = draw.textbbox((0,0), linha, font=fonte_artista)[2]
        draw.text(((largura - w)/2, y_inicio), linha, font=fonte_artista, fill="white")
        y_inicio += draw.textbbox((0,0), linha, font=fonte_artista)[3] - draw.textbbox((0,0), linha, font=fonte_artista)[1]

    saida = os.path.join(pasta_base, base + ".jpg")
    img.save(saida, "JPEG", quality=95)
    if log_callback:
        log_callback(f"Capa gerada: {saida}")

def run(log_callback=None, pasta_videos="Karaoke", arquivo_xlsx="assets/karaoke.xlsx"):
    # Log file
    agora = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(LOG_DIR, f"karaoke_gerar_thumb_{agora}.log")

    def log(msg):
        if log_callback:
            log_callback(msg)
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(msg + "\n")

    if not os.path.exists(pasta_videos):
        os.makedirs(pasta_videos)
        log(f"Pasta '{pasta_videos}' criada.")

    # Lê planilha
    if not os.path.exists(arquivo_xlsx):
        log(f"Arquivo XLSX não encontrado: {arquivo_xlsx}")
        return
    df = pd.read_excel(arquivo_xlsx)
    df['full_title'] = df['full_title'].astype(str).str.strip()
    titulos_map = {normalizar_nome(t): t for t in df['full_title'].tolist()}

    # Percorre vídeos e subpastas
    video_extensoes = {".mp4", ".mkv", ".avi", ".mov", ".flv", ".wmv", ".mpeg", ".webm"}
    for root, dirs, files in os.walk(pasta_videos):
        for arquivo in files:
            nome, ext = os.path.splitext(arquivo)
            if ext.lower() in video_extensoes:
                chave = normalizar_nome(nome)
                titulo = artista = None
                if chave in titulos_map:
                    if " - " in titulos_map[chave]:
                        artista, titulo = titulos_map[chave].split(" - ", 1)
                    else:
                        titulo = titulos_map[chave]
                capa_path = os.path.join(root, nome + ".jpg")
                if os.path.exists(capa_path):
                    log(f"Capa já existe, ignorando: {arquivo}")
                    continue
                gerar_capa(arquivo, root, titulo=titulo, artista=artista, log_callback=log)
