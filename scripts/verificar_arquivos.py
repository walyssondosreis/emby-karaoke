import os
import re
import pandas as pd
from datetime import datetime
from app.utils import get_logger

# Lista de extensões de vídeo aceitas
VIDEO_EXTENSOES = {".mp4", ".mkv", ".avi", ".mov", ".flv", ".wmv", ".mpeg", ".webm"}

logger = get_logger("verificar_arquivos")

def normalizar_nome(nome: str) -> str:
    """Remove o sufixo vN e normaliza o nome para comparação."""
    return re.sub(r' v\d+$', '', nome, flags=re.IGNORECASE).strip().lower()

def run(log_callback, pasta_videos: str, caminho_planilha: str):
    """
    Executa a verificação dos arquivos de vídeo em relação à planilha.
    
    :param log_callback: função de log (ex.: self.log da UI)
    :param pasta_videos: pasta escolhida pelo usuário
    :param caminho_planilha: caminho do arquivo Excel (ou assets/Songs.xls)
    """
    try:
        log_callback("🔍 Iniciando verificação de arquivos...")
        logger.info("Iniciando verificação de arquivos...")

        # Carrega planilha
        if not os.path.exists(caminho_planilha):
            raise FileNotFoundError(f"Planilha não encontrada: {caminho_planilha}")
        
        # Carrega as abas Karaoke e Biblioteca
        df_karaoke = pd.read_excel(caminho_planilha, sheet_name='Karaoke', engine="openpyxl")
        df_biblioteca = pd.read_excel(caminho_planilha, sheet_name='Biblioteca', engine="openpyxl")
        
        # Verifica se as colunas necessárias existem
        if 'music_id' not in df_karaoke.columns:
            raise ValueError("Coluna 'music_id' não encontrada na aba Karaoke")
        if 'music_id' not in df_biblioteca.columns or 'full_title' not in df_biblioteca.columns:
            raise ValueError("Colunas 'music_id' ou 'full_title' não encontradas na aba Biblioteca")
        
        # Filtra apenas os music_ids presentes na aba Karaoke
        music_ids_karaoke = set(df_karaoke['music_id'].dropna().unique())
        
        # Pega os full_titles da Biblioteca apenas para os music_ids que estão no Karaoke
        df_biblioteca_filtrado = df_biblioteca[df_biblioteca['music_id'].isin(music_ids_karaoke)]
        df_biblioteca_filtrado['full_title'] = df_biblioteca_filtrado['full_title'].astype(str).str.strip()

        # Pega arquivos da pasta (com subpastas)
        arquivos_pasta = {}
        for root, _, files in os.walk(pasta_videos):
            for arquivo in files:
                nome, ext = os.path.splitext(arquivo)
                if ext.lower() in VIDEO_EXTENSOES:
                    arquivos_pasta[normalizar_nome(nome)] = arquivo

        # Pega títulos da planilha (apenas os que estão no Karaoke)
        titulos_planilha = {}
        for t in df_biblioteca_filtrado['full_title'].tolist():
            t = str(t).strip()
            titulos_planilha[normalizar_nome(t)] = t

        # Arquivos na pasta mas não na planilha
        nao_na_planilha = [arquivos_pasta[n] for n in arquivos_pasta if n not in titulos_planilha]

        # Arquivos na planilha mas não na pasta
        nao_na_pasta = [titulos_planilha[n] for n in titulos_planilha if n not in arquivos_pasta]

        # Nome do log com data/hora
        agora = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f"karaoke_verificar_{agora}.log")

        # Escreve log no arquivo
        with open(log_file, "w", encoding="utf-8") as log:
            log.write(f"Log gerado em: {datetime.now()}\n")
            log.write(f"Planilha: {caminho_planilha}\n")
            log.write(f"Pasta de vídeos: {pasta_videos}\n")
            log.write(f"Músicas na aba Karaoke: {len(music_ids_karaoke)}\n")
            log.write(f"Músicas com full_title na Biblioteca: {len(titulos_planilha)}\n\n")

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

        log_callback(f"✅ Verificação concluída! Log salvo em {log_file}")
        log_callback(f"📊 Estatísticas: {len(music_ids_karaoke)} músicas no Karaoke, {len(titulos_planilha)} com dados na Biblioteca")
        logger.info(f"Verificação concluída! Log salvo em {log_file}")

    except Exception as e:
        msg = f"❌ Erro na verificação: {e}"
        log_callback(msg)
        logger.exception(msg)