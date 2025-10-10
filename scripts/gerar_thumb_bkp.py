import os
import math
import pandas as pd
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
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

# Tipos de extensões de imagem que serão buscadas
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"}

def encontrar_imagem_artista(nome_artista):
    """Procura por uma imagem do artista na pasta 'assets/__artist'."""
    pasta_assets_artist = os.path.join(BASE_DIR, "..", "assets", "__artist")
    
    if not os.path.exists(pasta_assets_artist):
        return None
        
    nome_normalizado_artista = normalizar_nome(nome_artista)
    for arquivo in os.listdir(pasta_assets_artist):
        nome_arquivo, ext = os.path.splitext(arquivo)
        if ext.lower() in IMAGE_EXTENSIONS:
            # Verifica se o nome do arquivo começa com o nome do artista (normalizado)
            if normalizar_nome(nome_arquivo).startswith(nome_normalizado_artista):
                return os.path.join(pasta_assets_artist, arquivo)
    return None

def desenhar_ondas(draw_obj, largura, altura, cor_onda, num_ondas=5, intensidade=0.1):
    """Desenha um padrão de ondas translúcidas."""
    for i in range(num_ondas):
        amplitude = altura / (num_ondas * 2) * (i + 1) / num_ondas * 0.8
        frequencia = 0.005 + i * 0.001
        offset_y = altura / num_ondas * i + (altura / (num_ondas * 2))
        cor_onda_rgba = cor_onda + (int(255 * intensidade),) 
        pontos = []
        for x in range(largura + 1):
            y = int(offset_y + amplitude * math.sin(frequencia * x + i * 0.5))
            pontos.append((x, y))
        if pontos:
            pontos_preenchimento = [(0, altura)] + pontos + [(largura, altura)]
            draw_obj.polygon(pontos_preenchimento, fill=cor_onda_rgba)

def texto_quebrado_avancado(draw_obj, texto, fonte, max_largura, max_linhas=3):
    """Quebra texto de forma mais inteligente, considerando hífens e priorizando palavras completas."""
    palavras = texto.split()
    linhas = []
    linha_atual = ""
    
    for palavra in palavras:
        teste_linha = linha_atual + (" " if linha_atual else "") + palavra
        
        # Verifica se a palavra é muito longa para caber sozinha
        bbox_palavra = draw_obj.textbbox((0, 0), palavra, font=fonte)
        largura_palavra = bbox_palavra[2] - bbox_palavra[0]
        
        if largura_palavra > max_largura and len(palavra) > 10:
            # Quebra palavras muito longas com hífen
            partes = []
            parte_atual = ""
            for char in palavra:
                teste_parte = parte_atual + char
                bbox_teste = draw_obj.textbbox((0, 0), teste_parte, font=fonte)
                if bbox_teste[2] - bbox_teste[0] > max_largura * 0.8 and parte_atual:
                    partes.append(parte_atual + "-")
                    parte_atual = char
                else:
                    parte_atual = teste_parte
            if parte_atual:
                partes.append(parte_atual)
            
            for parte in partes:
                if linha_atual:
                    teste_com_linha = linha_atual + " " + parte
                else:
                    teste_com_linha = parte
                
                bbox_teste = draw_obj.textbbox((0, 0), teste_com_linha, font=fonte)
                if bbox_teste[2] - bbox_teste[0] <= max_largura:
                    linha_atual = teste_com_linha
                else:
                    if linha_atual:
                        linhas.append(linha_atual)
                    linha_atual = parte
        else:
            # Comportamento normal para palavras que cabem
            bbox_teste = draw_obj.textbbox((0, 0), teste_linha, font=fonte)
            if bbox_teste[2] - bbox_teste[0] <= max_largura:
                linha_atual = teste_linha
            else:
                if linha_atual:
                    linhas.append(linha_atual)
                linha_atual = palavra
    
    if linha_atual and len(linhas) < max_linhas:
        linhas.append(linha_atual)
    
    return linhas

def calcular_tamanho_fonte_ideal(draw_obj, texto, fonte_base, max_largura, max_altura, tamanho_minimo=60):
    """Calcula o tamanho de fonte ideal para o texto caber na área disponível."""
    tamanho_fonte = 160
    fonte = ImageFont.truetype(fonte_base, tamanho_fonte)
    
    while tamanho_fonte >= tamanho_minimo:
        linhas = texto_quebrado_avancado(draw_obj, texto, fonte, max_largura)
        
        # Calcula altura total do texto
        altura_total = 0
        for linha in linhas:
            bbox = draw_obj.textbbox((0, 0), linha, font=fonte)
            altura_linha = bbox[3] - bbox[1]
            altura_total += altura_linha
        
        # Adiciona espaçamento entre linhas (20% da altura da linha)
        espacamento = altura_total * 0.2 * (len(linhas) - 1) if len(linhas) > 1 else 0
        altura_total += espacamento
        
        if altura_total <= max_altura and len(linhas) <= 3:
            break
        
        tamanho_fonte -= 5
        fonte = ImageFont.truetype(fonte_base, tamanho_fonte)
    
    return max(tamanho_fonte, tamanho_minimo), linhas

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
    
    fundo_base = Image.new("RGB", (largura, altura), color=(0, 0, 0))
    draw_fundo_base = ImageDraw.Draw(fundo_base)

    imagem_artista_path = encontrar_imagem_artista(artista)
    
    if imagem_artista_path:
        try:
            img_fundo_artista = Image.open(imagem_artista_path).convert("RGB")
            img_fundo_artista = img_fundo_artista.resize((largura, altura), Image.LANCZOS)
            img_fundo_artista = img_fundo_artista.convert("L").convert("RGB") 
            fundo_base = img_fundo_artista
            
        except Exception as e:
            if log_callback:
                log_callback(f"Erro ao usar imagem de fundo para {artista}: {e}. Usando fundo gradiente.")
            cor_topo = (20, 20, 20)
            cor_base = (0, 0, 0)
            for y in range(altura):
                r = int(cor_topo[0] + (cor_base[0] - cor_topo[0]) * (y / altura))
                g = int(cor_topo[1] + (cor_base[1] - cor_topo[1]) * (y / altura))
                b = int(cor_topo[2] + (cor_base[2] - cor_topo[2]) * (y / altura))
                draw_fundo_base.line([(0, y), (largura, y)], fill=(r, g, b))
    else:
        cor_topo = (20, 20, 20)
        cor_base = (0, 0, 0)
        for y in range(altura):
            r = int(cor_topo[0] + (cor_base[0] - cor_topo[0]) * (y / altura))
            g = int(cor_topo[1] + (cor_base[1] - cor_topo[1]) * (y / altura))
            b = int(cor_topo[2] + (cor_base[2] - cor_topo[2]) * (y / altura))
            draw_fundo_base.line([(0, y), (largura, y)], fill=(r, g, b))

    ondas_layer = Image.new("RGBA", (largura, altura), (0, 0, 0, 0))
    draw_ondas = ImageDraw.Draw(ondas_layer)
    desenhar_ondas(draw_ondas, largura, altura, cor_onda=(50, 50, 50), num_ondas=4, intensidade=0.1)

    camada_legibilidade = Image.new("RGBA", (largura, altura), (0, 0, 0, 180))
    
    img = fundo_base.copy()
    img.paste(ondas_layer, (0, 0), ondas_layer)
    img.paste(camada_legibilidade, (0, 0), camada_legibilidade)

    draw = ImageDraw.Draw(img)

    try:
        fonte_karaoke = ImageFont.truetype(FONT_KARAOKE_BOLD, 60)
        fonte_artista = ImageFont.truetype(FONT_ARTISTA_REGULAR, 80)
        # A fonte da música será ajustada dinamicamente
        fonte_musica_base = FONT_MUSICA_BOLD
    except IOError as e:
        if log_callback:
            log_callback(f"Erro ao carregar fontes: {e}")
        fonte_karaoke = fonte_artista = ImageFont.load_default()
        fonte_musica_base = None

    margem = 80
    max_largura = largura - 2 * margem
    max_altura_disponivel = 400  # Altura máxima para o título + artista

    # --- AJUSTE DINÂMICO DO TÍTULO ---
    if fonte_musica_base:
        tamanho_fonte_titulo, linhas_titulo = calcular_tamanho_fonte_ideal(
            draw, titulo, fonte_musica_base, max_largura, max_altura_disponivel - 100, 60
        )
        fonte_musica = ImageFont.truetype(fonte_musica_base, tamanho_fonte_titulo)
    else:
        # Fallback se não carregar a fonte
        fonte_musica = ImageFont.load_default()
        linhas_titulo = [titulo]

    # Texto "KARAOKÊ" sempre no topo
    w_topo = draw.textbbox((0, 0), "KARAOKÊ", font=fonte_karaoke)[2]
    draw.text(((largura - w_topo) / 2, 40), "KARAOKÊ", font=fonte_karaoke, fill="white")

    # Quebra texto do artista
    linhas_artista = texto_quebrado_avancado(draw, artista, fonte_artista, max_largura, max_linhas=2)

    # --- CALCULAR POSIÇÃO VERTICAL CENTRALIZADA ---
    # Calcular altura total do conteúdo
    altura_total_conteudo = 0
    
    # Altura do título
    for linha in linhas_titulo:
        bbox = draw.textbbox((0, 0), linha, font=fonte_musica)
        altura_linha = bbox[3] - bbox[1]
        altura_total_conteudo += altura_linha
    
    # AUMENTEI O ESPAÇAMENTO ENTRE TÍTULO E ARTISTA (de 30 para 60)
    espacamento_titulo_artista = 60
    altura_total_conteudo += espacamento_titulo_artista
    
    # Altura do artista
    for linha in linhas_artista:
        bbox = draw.textbbox((0, 0), linha, font=fonte_artista)
        altura_linha = bbox[3] - bbox[1]
        altura_total_conteudo += altura_linha

    # Calcular Y inicial para centralizar verticalmente (considerando espaço do "KARAOKÊ")
    y_karaoke = 40 + draw.textbbox((0, 0), "KARAOKÊ", font=fonte_karaoke)[3] + 40
    espaco_disponivel = altura - y_karaoke - 40  # 40px de margem inferior
    y_inicio = y_karaoke + (espaco_disponivel - altura_total_conteudo) // 2

    # --- DESENHAR TÍTULO CENTRALIZADO ---
    y_atual = y_inicio
    for linha in linhas_titulo:
        bbox = draw.textbbox((0, 0), linha, font=fonte_musica)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        
        # Centralizar horizontalmente (permitindo que exceda visualmente se necessário)
        x = (largura - w) / 2
        draw.text((x, y_atual), linha, font=fonte_musica, fill="yellow")
        y_atual += h

    # --- DESENHAR ARTISTA CENTRALIZADO (COM MAIS ESPAÇO) ---
    y_atual += espacamento_titulo_artista  # Agora com 60px de espaçamento
    for linha in linhas_artista:
        bbox = draw.textbbox((0, 0), linha, font=fonte_artista)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        
        # Centralizar horizontalmente
        x = (largura - w) / 2
        draw.text((x, y_atual), linha, font=fonte_artista, fill="white")
        y_atual += h

    saida = os.path.join(pasta_base, base + ".jpg")
    img.save(saida, "JPEG", quality=95)
    if log_callback:
        log_callback(f"Capa gerada: {saida}")

def run(log_callback=None, pasta_videos="Karaoke", arquivo_xlsx="assets/karaoke.xlsx"):
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
    
    pasta_artists = os.path.join(BASE_DIR, "..", "assets", "__artist")
    log(f"Buscando imagens de artista na pasta: {pasta_artists}")

    if not os.path.exists(arquivo_xlsx):
        log(f"Arquivo XLSX não encontrado: {arquivo_xlsx}")
        return
    df = pd.read_excel(arquivo_xlsx)
    df['full_title'] = df['full_title'].astype(str).str.strip()
    titulos_map = {normalizar_nome(t): t for t in df['full_title'].tolist()}

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
                
                if not artista and " - " in nome:
                    artista = nome.split(" - ", 1)[0]
                elif not artista:
                    artista = "Desconhecido"

                capa_path = os.path.join(root, nome + ".jpg")
                if os.path.exists(capa_path):
                    log(f"Capa já existe, ignorando: {arquivo}")
                    continue
                gerar_capa(arquivo, root, titulo=titulo, artista=artista, log_callback=log)