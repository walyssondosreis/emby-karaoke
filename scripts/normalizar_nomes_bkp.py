import os
import re
import pandas as pd
from datetime import datetime
from scripts.verificar_arquivos import normalizar_nome

# Base e logs
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "..", "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Extensões suportadas
VIDEO_EXTS = {".mp4", ".mkv", ".avi", ".mov", ".flv", ".wmv", ".mpeg", ".webm"}
RELATED_EXTS = {".jpg", ".nfo"}

def renomear_arquivo_antigo(orig_path, novo_path, log_callback=None):
    """Renomeia arquivo e arquivos relacionados (.jpg, .nfo)"""
    os.rename(orig_path, novo_path)
    if log_callback:
        log_callback(f"Renomeado: {orig_path} -> {novo_path}")

    base_orig, _ = os.path.splitext(orig_path)
    base_novo, _ = os.path.splitext(novo_path)
    for ext in RELATED_EXTS:
        rel_orig = base_orig + ext
        rel_novo = base_novo + ext
        if os.path.exists(rel_orig):
            os.rename(rel_orig, rel_novo)
            if log_callback:
                log_callback(f"Renomeado relacionado: {rel_orig} -> {rel_novo}")

def run(log_callback=None, pasta_videos="Karaoke", arquivo_xlsx="assets/karaoke.xlsx"):
    agora = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(LOG_DIR, f"karaoke_normalizar_nomes_{agora}.log")

    def log(msg):
        if log_callback:
            log_callback(msg)
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(msg + "\n")

    if not os.path.exists(pasta_videos):
        log(f"Pasta de vídeos não encontrada: {pasta_videos}")
        return

    if not os.path.exists(arquivo_xlsx):
        log(f"Arquivo XLSX não encontrado: {arquivo_xlsx}")
        return

    # Mapear todos os arquivos de todas as subpastas
    arquivos_dict = {}
    for root, dirs, files in os.walk(pasta_videos):
        for arquivo in files:
            nome, ext = os.path.splitext(arquivo)
            if ext.lower() not in VIDEO_EXTS:
                continue
            chave = normalizar_nome(nome)
            m = re.search(r' v(\d+)$', nome, re.IGNORECASE)
            versao = int(m.group(1)) if m else 1
            if chave not in arquivos_dict:
                arquivos_dict[chave] = []
            arquivos_dict[chave].append({
                "caminho": os.path.join(root, arquivo),
                "nome": nome,
                "ext": ext,
                "versao": versao
            })

    # Processar normalização global por nome base
    for chave, lista in arquivos_dict.items():
        # Ordena pela versão existente
        lista.sort(key=lambda x: x['versao'])

        # Se não existe versão 1, renomeia o primeiro arquivo para versão 1 (sem vN)
        if lista[0]['versao'] != 1:
            orig = lista[0]
            novo_nome = re.sub(r' v\d+$', '', orig['nome'], flags=re.IGNORECASE)
            novo_path = os.path.join(os.path.dirname(orig['caminho']), novo_nome + orig['ext'])
            renomear_arquivo_antigo(orig['caminho'], novo_path, log_callback)
            lista[0]['caminho'] = novo_path
            lista[0]['nome'] = novo_nome
            lista[0]['versao'] = 1

        # Renomeia demais arquivos mantendo sequência correta (v2, v3, ...)
        for i, item in enumerate(lista[1:], start=2):
            orig = item
            nome_base = re.sub(r' v\d+$', '', orig['nome'], flags=re.IGNORECASE)
            novo_nome = f"{nome_base} v{i}{orig['ext']}"
            novo_path = os.path.join(os.path.dirname(orig['caminho']), novo_nome)
            if os.path.exists(orig['caminho']):
                renomear_arquivo_antigo(orig['caminho'], novo_path, log_callback)
                item['caminho'] = novo_path
                item['nome'] = f"{nome_base} v{i}"
                item['versao'] = i

    log("Normalização de nomes concluída com sucesso!")
