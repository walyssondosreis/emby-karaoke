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
    :param caminho_planilha: caminho do arquivo Excel (ou assets/karaoke.xlsx)
    """
    try:
        log_callback("🔍 Iniciando verificação de arquivos...")
        logger.info("Iniciando verificação de arquivos...")

        # Carrega planilha
        if not os.path.exists(caminho_planilha):
            raise FileNotFoundError(f"Planilha não encontrada: {caminho_planilha}")
        
        df = pd.read_excel(caminho_planilha, engine="openpyxl")
        df['full_title'] = df['full_title'].astype(str).str.strip()

        # Pega arquivos da pasta (com subpastas)
        arquivos_pasta = {}
        for root, _, files in os.walk(pasta_videos):
            for arquivo in files:
                nome, ext = os.path.splitext(arquivo)
                if ext.lower() in VIDEO_EXTENSOES:
                    arquivos_pasta[normalizar_nome(nome)] = arquivo

        # Pega títulos da planilha
        titulos_planilha = {}
        for t in df['full_title'].tolist():
            t = str(t).strip()
            titulos_planilha[normalizar_nome(t)] = t

        # Arquivos na pasta mas não na planilha
        nao_na_planilha = [arquivos_pasta[n] for n in arquivos_pasta if n not in titulos_planilha]

        # Arquivos na planilha mas não na pasta
        nao_na_pasta = [titulos_planilha[n] for n in titulos_planilha if n not in arquivos_pasta]

        # Nome do log com data/hora
        agora = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join("logs", f"karaoke_verificar_{agora}.log")

        # Escreve log no arquivo
        with open(log_file, "w", encoding="utf-8") as log:
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

        log_callback(f"✅ Verificação concluída! Log salvo em {log_file}")
        logger.info(f"Verificação concluída! Log salvo em {log_file}")

    except Exception as e:
        msg = f"❌ Erro na verificação: {e}"
        log_callback(msg)
        logger.exception(msg)
