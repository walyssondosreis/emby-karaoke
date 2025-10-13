import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from dotenv import load_dotenv
import subprocess
import threading
import shutil
from datetime import datetime

# Carrega o .env
load_dotenv()

# Diretório raiz do projeto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(BASE_DIR)

# Lê variáveis do .env
pasta_env = os.getenv("PATH_PASTA_KARAOKE", "assets")
arquivo_env = os.getenv("PATH_ARQUIVO_KARAOKE", "assets/karaoke.xlsx")
pasta_stems_env = os.getenv("PATH_PASTA_STEMS", "stems")

# Caminhos absolutos
DEFAULT_PASTA_KARAOKE = os.path.join(BASE_DIR, pasta_env)
DEFAULT_ARQUIVO_KARAOKE = os.path.join(BASE_DIR, arquivo_env)
DEFAULT_PASTA_STEMS = os.path.join(BASE_DIR, pasta_stems_env)

# Importação dos scripts
try:
    from scripts import verificar_arquivos, gerar_thumb, normalizar_nomes, gerar_nfo, renomear_arquivos
except ImportError as e:
    print(f"⚠️  Erro ao importar scripts: {e}")
    # Mock dos scripts para desenvolvimento
    class MockScript:
        @staticmethod
        def run(*args, **kwargs):
            log_callback = kwargs.get('log_callback', print)
            log_callback("⚡ Simulação: Script executado com sucesso")
    
    verificar_arquivos = MockScript()
    gerar_thumb = MockScript()
    normalizar_nomes = MockScript()
    gerar_nfo = MockScript()
    renomear_arquivos = MockScript()

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Emby Karaoke Checker - Professional")
        self.root.configure(bg='#2C3E50')
        self.root.geometry('900x800')  # Aumentei a altura para acomodar os novos botões
        
        self.pasta_var = tk.StringVar(value=DEFAULT_PASTA_KARAOKE)
        self.arquivo_var = tk.StringVar(value=DEFAULT_ARQUIVO_KARAOKE)
        self.pasta_stems_var = tk.StringVar(value=DEFAULT_PASTA_STEMS)
        self.trilha_audio_var = tk.StringVar(value="instrumental")
        
        self.setup_styles()
        main_frame = tk.Frame(root, bg='#2C3E50', padx=20, pady=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.create_header(main_frame)
        self.create_settings_section(main_frame)
        self.create_actions_section(main_frame)
        self.create_utilities_section(main_frame)  # Nova seção de utilitários
        self.create_log_section(main_frame)

    def setup_styles(self):
        self.colors = {
            'primary': '#3498DB',
            'dark': '#2C3E50',
            'light': '#ECF0F1',
            'text': '#2C3E50'
        }
        self.fonts = {
            'title': ('Segoe UI', 16, 'bold'),
            'subtitle': ('Segoe UI', 10),
            'label': ('Segoe UI', 9, 'bold'),
            'button': ('Segoe UI', 9, 'bold'),
            'log': ('Consolas', 9)
        }

    def create_header(self, parent):
        header_frame = tk.Frame(parent, bg=self.colors['dark'])
        header_frame.pack(fill=tk.X, pady=(0, 20))
        tk.Label(header_frame, text="🎤 Emby Karaoke Checker", font=self.fonts['title'], fg='white', bg=self.colors['dark'], pady=10).pack()
        tk.Label(header_frame, text="Ferramenta completa para gerenciamento de biblioteca de karaokê", font=self.fonts['subtitle'], fg='#BDC3C7', bg=self.colors['dark'], pady=5).pack()

    def create_settings_section(self, parent):
        settings_frame = tk.LabelFrame(parent, text=" ⚙️ CONFIGURAÇÕES ", font=self.fonts['label'], fg=self.colors['text'], bg=self.colors['light'], padx=15, pady=10)
        settings_frame.pack(fill=tk.X, pady=(0, 15))

        # Pasta Karaoke
        tk.Label(settings_frame, text="Pasta Karaoke:", font=self.fonts['label'], bg=self.colors['light']).grid(row=0, column=0, sticky="w", pady=5)
        frame_pasta = tk.Frame(settings_frame, bg=self.colors['light'])
        frame_pasta.grid(row=0, column=1, sticky="ew", pady=5)
        entry_pasta = tk.Entry(frame_pasta, textvariable=self.pasta_var, width=60, font=('Segoe UI', 9), relief='solid', borderwidth=1)
        entry_pasta.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        tk.Button(frame_pasta, text="📁 Selecionar", command=self.selecionar_pasta, **self.get_button_style('primary')).pack(side=tk.RIGHT)

        # Arquivo XLSX
        tk.Label(settings_frame, text="Arquivo Karaoke (.xlsx):", font=self.fonts['label'], bg=self.colors['light']).grid(row=1, column=0, sticky="w", pady=5)
        frame_arquivo = tk.Frame(settings_frame, bg=self.colors['light'])
        frame_arquivo.grid(row=1, column=1, sticky="ew", pady=5)
        entry_arquivo = tk.Entry(frame_arquivo, textvariable=self.arquivo_var, width=60, font=('Segoe UI', 9), relief='solid', borderwidth=1)
        entry_arquivo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        tk.Button(frame_arquivo, text="📄 Selecionar", command=self.selecionar_arquivo, **self.get_button_style('primary')).pack(side=tk.RIGHT)

        # Pasta Stems
        tk.Label(settings_frame, text="Pasta Stems:", font=self.fonts['label'], bg=self.colors['light']).grid(row=2, column=0, sticky="w", pady=5)
        frame_stems = tk.Frame(settings_frame, bg=self.colors['light'])
        frame_stems.grid(row=2, column=1, sticky="ew", pady=5)
        entry_stems = tk.Entry(frame_stems, textvariable=self.pasta_stems_var, width=60, font=('Segoe UI', 9), relief='solid', borderwidth=1)
        entry_stems.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        tk.Button(frame_stems, text="📁 Selecionar", command=self.selecionar_pasta_stems, **self.get_button_style('primary')).pack(side=tk.RIGHT)

        # Trilha de Áudio
        tk.Label(settings_frame, text="Trilha de Áudio:", font=self.fonts['label'], bg=self.colors['light']).grid(row=3, column=0, sticky="w", pady=5)
        frame_trilha = tk.Frame(settings_frame, bg=self.colors['light'])
        frame_trilha.grid(row=3, column=1, sticky="w", pady=5)
        
        trilha_options = ["instrumental", "vocals", "mix"]
        trilha_dropdown = tk.OptionMenu(frame_trilha, self.trilha_audio_var, *trilha_options)
        trilha_dropdown.config(font=('Segoe UI', 9), bg=self.colors['primary'], fg='white', relief='flat', width=12)
        trilha_dropdown.pack(side=tk.LEFT)
        
        settings_frame.columnconfigure(1, weight=1)

    def create_actions_section(self, parent):
        actions_frame = tk.LabelFrame(parent, text=" 🚀 AÇÕES ", font=self.fonts['label'], fg=self.colors['text'], bg=self.colors['light'], padx=15, pady=10)
        actions_frame.pack(fill=tk.X, pady=(0, 15))

        button_frame1 = tk.Frame(actions_frame, bg=self.colors['light'])
        button_frame1.pack(fill=tk.X, pady=5)
        button_frame2 = tk.Frame(actions_frame, bg=self.colors['light'])
        button_frame2.pack(fill=tk.X, pady=5)
        button_frame3 = tk.Frame(actions_frame, bg=self.colors['light'])
        button_frame3.pack(fill=tk.X, pady=5)
        button_frame4 = tk.Frame(actions_frame, bg=self.colors['light'])
        button_frame4.pack(fill=tk.X, pady=5)

        tk.Button(button_frame1, text="🔍 Verificar Arquivos", command=self.verificar, **self.get_button_style('primary')).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        tk.Button(button_frame1, text="🖼️ Gerar Thumbnails", command=self.gerar_thumbs, **self.get_button_style('primary')).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        tk.Button(button_frame2, text="📝 Normalizar Nomes", command=self.normalizar_nomes, **self.get_button_style('primary')).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        tk.Button(button_frame2, text="📋 Gerar NFO", command=self.gerar_nfo, **self.get_button_style('primary')).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        tk.Button(button_frame2, text="✏️ Renomear Arquivos", command=self.renomear_arquivos, **self.get_button_style('primary')).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        tk.Button(button_frame3, text="🗑️ Excluir Thumbs JPG", command=self.excluir_thumbs, **self.get_button_style('primary')).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        tk.Button(button_frame3, text="🗑️ Excluir NFOs", command=self.excluir_nfos, **self.get_button_style('primary')).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        tk.Button(button_frame3, text="📂 Abrir Pasta de Logs", command=self.abrir_logs, **self.get_button_style('primary')).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # Botão Gerar Video
        tk.Button(button_frame4, text="🎬 Gerar Video", command=self.gerar_video, **self.get_button_style('primary')).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

    def create_utilities_section(self, parent):
        """Nova seção para utilitários"""
        utilities_frame = tk.LabelFrame(parent, text=" 🛠️ UTILITÁRIOS ", font=self.fonts['label'], fg=self.colors['text'], bg=self.colors['light'], padx=15, pady=10)
        utilities_frame.pack(fill=tk.X, pady=(0, 15))

        button_frame = tk.Frame(utilities_frame, bg=self.colors['light'])
        button_frame.pack(fill=tk.X, pady=5)

        # Botões de utilitários
        tk.Button(button_frame, text="📁 Abrir pasta de saída", command=self.abrir_pasta_output, **self.get_button_style('primary')).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        tk.Button(button_frame, text="🖼️ Abrir imagens", command=self.abrir_pasta_imagens, **self.get_button_style('primary')).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        tk.Button(button_frame, text="📤 Enviar Songs.xlsx", command=self.enviar_songs_xlsx, **self.get_button_style('primary')).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

    def create_log_section(self, parent):
        log_frame = tk.LabelFrame(parent, text=" 📊 LOG DE EXECUÇÃO ", font=self.fonts['label'], fg=self.colors['text'], bg=self.colors['light'], padx=15, pady=10)
        log_frame.pack(fill=tk.BOTH, expand=True)
        self.txt_log = scrolledtext.ScrolledText(log_frame, height=15, width=80, state="disabled", font=self.fonts['log'], bg='#1A252F', fg='#00FF00', insertbackground='white', selectbackground=self.colors['primary'], relief='solid', borderwidth=1, padx=10, pady=10)
        self.txt_log.pack(fill=tk.BOTH, expand=True)

    def get_button_style(self, color_type):
        return {
            'bg': self.colors['primary'], 
            'fg': 'white', 
            'font': self.fonts['button'], 
            'relief': 'flat',
            'borderwidth': 0, 
            'padx': 15, 
            'pady': 8, 
            'cursor': 'hand2'
        }

    def log(self, mensagem):
        self.txt_log.config(state="normal")
        self.txt_log.insert(tk.END, mensagem + "\n")
        self.txt_log.see(tk.END)
        self.txt_log.config(state="disabled")

    # ========== NOVAS FUNÇÕES DE UTILITÁRIOS ==========

    def abrir_pasta_output(self):
        """Abre a pasta Output onde os vídeos são gerados"""
        output_path = os.path.join(BASE_DIR, "Output")
        
        if not os.path.exists(output_path):
            os.makedirs(output_path)
            self.log(f"📁 Pasta Output criada: {output_path}")

        try:
            if os.name == 'nt':  # Windows
                subprocess.Popen(f'explorer "{output_path}"')
            else:  # Linux/Mac
                subprocess.Popen(['xdg-open', output_path])
            self.log(f"📂 Abrindo pasta de saída: {output_path}")
        except Exception as e:
            self.log(f"❌ Erro ao abrir pasta de saída: {e}")

    def abrir_pasta_imagens(self):
        """Abre a pasta __artist com as imagens dos artistas"""
        imagens_path = os.path.join(BASE_DIR, "assets", "__artist")
        
        if not os.path.exists(imagens_path):
            os.makedirs(imagens_path)
            self.log(f"📁 Pasta de imagens criada: {imagens_path}")

        try:
            if os.name == 'nt':  # Windows
                subprocess.Popen(f'explorer "{imagens_path}"')
            else:  # Linux/Mac
                subprocess.Popen(['xdg-open', imagens_path])
            self.log(f"🖼️ Abrindo pasta de imagens: {imagens_path}")
        except Exception as e:
            self.log(f"❌ Erro ao abrir pasta de imagens: {e}")

    def enviar_songs_xlsx(self):
        """Permite ao usuário enviar uma nova planilha Songs.xlsx"""
        # Solicitar arquivo ao usuário
        arquivo_novo = filedialog.askopenfilename(
            title="Selecionar nova planilha Songs.xlsx",
            filetypes=[("Planilhas Excel", "*.xlsx"), ("Todos os arquivos", "*.*")]
        )
        
        if not arquivo_novo:
            return  # Usuário cancelou
        
        # Caminhos dos arquivos
        songs_atual = os.path.join(BASE_DIR, "assets", "Songs.xlsx")
        songs_backup_dir = os.path.join(BASE_DIR, "assets", "backups")
        
        try:
            # Criar pasta de backups se não existir
            if not os.path.exists(songs_backup_dir):
                os.makedirs(songs_backup_dir)
            
            # Verificar se o arquivo atual existe para fazer backup
            if os.path.exists(songs_atual):
                # Gerar nome do backup com timestamp
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                nome_backup = f"Songs_old_{timestamp}.xlsx"
                caminho_backup = os.path.join(songs_backup_dir, nome_backup)
                
                # Fazer backup do arquivo atual
                shutil.copy2(songs_atual, caminho_backup)
                self.log(f"📦 Backup criado: {nome_backup}")
            
            # Copiar o novo arquivo para Songs.xlsx
            shutil.copy2(arquivo_novo, songs_atual)
            self.log(f"✅ Nova planilha enviada: {os.path.basename(arquivo_novo)}")
            self.log(f"📊 Songs.xlsx atualizado com sucesso!")
            
            # Atualizar o campo do arquivo na interface
            self.arquivo_var.set(songs_atual)
            
        except Exception as e:
            self.log(f"❌ Erro ao enviar planilha: {str(e)}")
            messagebox.showerror("Erro", f"Erro ao enviar planilha: {str(e)}")

    # ========== FUNÇÕES EXISTENTES ==========

    def selecionar_pasta(self):
        pasta = filedialog.askdirectory()
        if pasta:
            self.pasta_var.set(pasta)
            self.log(f"📁 Pasta selecionada: {pasta}")

    def selecionar_arquivo(self):
        arquivo = filedialog.askopenfilename(filetypes=[("Planilhas Excel", "*.xlsx")])
        if arquivo:
            self.arquivo_var.set(arquivo)
            self.log(f"📄 Arquivo selecionado: {arquivo}")

    def selecionar_pasta_stems(self):
        pasta = filedialog.askdirectory()
        if pasta:
            self.pasta_stems_var.set(pasta)
            self.log(f"📁 Pasta Stems selecionada: {pasta}")

    def verificar_se_video_ja_existe(self, nome_arquivo, pasta_karaoke):
        """Verifica se o vídeo já existe na pasta karaoke (em qualquer subpasta)"""
        for root_dir, _, files in os.walk(pasta_karaoke):
            for arquivo in files:
                # Remove a extensão para comparar apenas o nome
                nome_sem_extensao = os.path.splitext(arquivo)[0]
                if nome_sem_extensao == nome_arquivo:
                    return os.path.join(root_dir, arquivo)
        return None

    def encontrar_imagem_artista(self, nome_artista):
        """Encontra imagem do artista na pasta assets/__artist"""
        pasta_artistas = os.path.join(BASE_DIR, "assets", "__artist")
        
        if not os.path.exists(pasta_artistas):
            return None
        
        # Extrair apenas o nome do artista (parte antes do " - ")
        artista = nome_artista.split(" - ")[0].strip()
        
        # Extensões de imagem suportadas
        extensoes = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp']
        
        for ext in extensoes:
            caminho_imagem = os.path.join(pasta_artistas, f"{artista}{ext}")
            if os.path.exists(caminho_imagem):
                return caminho_imagem
        
        # Se não encontrou com o nome exato, procurar por arquivos que começam com o nome do artista
        try:
            for arquivo in os.listdir(pasta_artistas):
                if arquivo.lower().startswith(artista.lower()):
                    caminho_imagem = os.path.join(pasta_artistas, arquivo)
                    if any(arquivo.lower().endswith(ext) for ext in extensoes):
                        return caminho_imagem
        except:
            pass
        
        return None

    def encontrar_ultrastar_txt_em_stems(self, pasta_stems):
        """Encontra todos os arquivos ultrastar.txt nas subpastas 'artist - title'"""
        projetos_validos = []
        
        if not os.path.exists(pasta_stems):
            self.log(f"❌ Pasta Stems não encontrada: {pasta_stems}")
            return projetos_validos
        
        self.log(f"🔍 Procurando projetos em: {pasta_stems}")
        
        for item in os.listdir(pasta_stems):
            caminho_completo = os.path.join(pasta_stems, item)
            
            # Verifica se é uma pasta no formato "artist - title"
            if os.path.isdir(caminho_completo) and " - " in item:
                artista_titulo = item
                caminho_ultrastar = os.path.join(caminho_completo, "ultrastar.txt")
                
                if os.path.exists(caminho_ultrastar):
                    # Verifica se o arquivo de áudio existe
                    trilha_audio = self.trilha_audio_var.get() + ".mp3"
                    caminho_audio = os.path.join(caminho_completo, trilha_audio)
                    
                    if os.path.exists(caminho_audio):
                        # Buscar imagem do artista
                        imagem_artista = self.encontrar_imagem_artista(artista_titulo)
                        
                        projetos_validos.append({
                            'pasta': caminho_completo,
                            'artista_titulo': artista_titulo,
                            'ultrastar_txt': caminho_ultrastar,
                            'arquivo_audio': caminho_audio,
                            'imagem_artista': imagem_artista
                        })
                        self.log(f"   ✅ Projeto válido: {artista_titulo}")
                        if imagem_artista:
                            self.log(f"      🖼️  Imagem encontrada: {os.path.basename(imagem_artista)}")
                    else:
                        self.log(f"   ⚠️  Áudio não encontrado: {trilha_audio} em {artista_titulo}")
                else:
                    self.log(f"   ❌ Ultrastar.txt não encontrado em: {artista_titulo}")
        
        return projetos_validos

    def executar_gerar_video_com_progresso(self, comando, projeto, log_filepath):
        """Executa o comando e captura o progresso em tempo real"""
        try:
            # Criar ambiente com encoding UTF-8 forçado
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            env['PYTHONUTF8'] = '1'
            
            # Executar o script como subprocesso com PIPE para capturar saída em tempo real
            processo = subprocess.Popen(
                comando,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # Juntar stdout e stderr
                text=True,
                encoding='utf-8',
                errors='ignore',
                cwd=BASE_DIR,
                env=env,
                bufsize=1,  # Line buffered
                universal_newlines=True
            )
            
            # Ler a saída em tempo real
            while True:
                linha = processo.stdout.readline()
                if not linha and processo.poll() is not None:
                    break
                
                if linha:
                    linha = linha.strip()
                    if linha:
                        # Filtrar apenas linhas de progresso importantes
                        if any(palavra in linha for palavra in ['Rolagem:', 'Finalizando...', '✅ Vídeo com Rolagem', '📤 Finalizando']):
                            self.log(f"   📊 {linha}")
                        elif any(palavra in linha for palavra in ['🚀 Gerador de Karaokê', '📺 Resolução:', '🎵 Música:', '🎤 Artista:', '⏱️  Duração:']):
                            # Log inicial importante
                            self.log(f"   ℹ️  {linha}")
                        elif '❌' in linha or 'Erro:' in linha or 'Traceback' in linha:
                            # Log de erros
                            self.log(f"   {linha}")
            
            # Aguardar processo terminar
            returncode = processo.wait()
            return returncode, ""
            
        except Exception as e:
            return 1, f"Erro ao executar processo: {str(e)}"

    def executar_gerar_video_thread(self, projetos_para_gerar, log_filepath):
        """Executa a geração de vídeos em thread separada"""
        try:
            videos_gerados = []
            sucessos = 0
            erros = 0
            
            # Obter o caminho do Python atual
            python_executable = sys.executable
            
            for i, projeto in enumerate(projetos_para_gerar, 1):
                self.log(f"🎬 Processando ({i}/{len(projetos_para_gerar)}): {projeto['artista_titulo']}")
                
                # Verificar se os arquivos existem
                if not os.path.exists(projeto['ultrastar_txt']):
                    self.log(f"   ❌ Arquivo ultrastar.txt não encontrado: {projeto['ultrastar_txt']}")
                    erros += 1
                    continue
                    
                if not os.path.exists(projeto['arquivo_audio']):
                    self.log(f"   ❌ Arquivo de áudio não encontrado: {projeto['arquivo_audio']}")
                    erros += 1
                    continue
                
                # Montar comando para chamar o script gerar_video.py
                comando = [
                    python_executable, 
                    'scripts/gerar_video.py',
                    projeto['ultrastar_txt'],
                    '--audio', projeto['arquivo_audio']
                ]
                
                # Adicionar parâmetro de background se houver imagem do artista
                if projeto['imagem_artista']:
                    comando.extend(['--background', projeto['imagem_artista']])
                    self.log(f"   🖼️  Usando imagem do artista: {os.path.basename(projeto['imagem_artista'])}")
                
                self.log(f"   🔧 Iniciando geração de vídeo...")
                
                try:
                    # Executar com captura de progresso em tempo real
                    returncode, erro_msg = self.executar_gerar_video_com_progresso(comando, projeto, log_filepath)
                    
                    if returncode == 0:
                        sucessos += 1
                        # Verificar se o arquivo foi realmente criado na pasta Output
                        output_file = os.path.join(BASE_DIR, "Output", f"{projeto['artista_titulo']}.mp4")
                        if os.path.exists(output_file):
                            videos_gerados.append(f"{projeto['artista_titulo']}.mp4")
                            self.log(f"   ✅ Vídeo criado com sucesso: {projeto['artista_titulo']}.mp4")
                            
                            # Log no arquivo também
                            with open(log_filepath, 'a', encoding='utf-8') as f:
                                f.write(f"✅ Vídeo criado: {projeto['artista_titulo']}.mp4\n")
                        else:
                            self.log(f"   ⚠️  Script executou mas vídeo não foi encontrado em: Output/{projeto['artista_titulo']}.mp4")
                    else:
                        erros += 1
                        erro_msg = f"   ❌ Erro ao gerar {projeto['artista_titulo']} (código: {returncode})"
                        self.log(erro_msg)
                        
                        with open(log_filepath, 'a', encoding='utf-8') as f:
                            f.write(f"{erro_msg}\n")
                            
                except subprocess.TimeoutExpired:
                    erros += 1
                    erro_msg = f"   ⏰ Timeout ao gerar {projeto['artista_titulo']}"
                    self.log(erro_msg)
                    with open(log_filepath, 'a', encoding='utf-8') as f:
                        f.write(f"{erro_msg}\n")
                
                except Exception as e:
                    erros += 1
                    erro_msg = f"   ❌ Erro ao gerar {projeto['artista_titulo']}: {str(e)}"
                    self.log(erro_msg)
                    with open(log_filepath, 'a', encoding='utf-8') as f:
                        f.write(f"{erro_msg}\n")
            
            # Resumo final
            self.log(f"\n📊 RESUMO DA GERAÇÃO:")
            self.log(f"   ✅ Sucessos: {sucessos}")
            self.log(f"   ❌ Erros: {erros}")
            
            if videos_gerados:
                self.log(f"\n🎬 VÍDEOS CRIADOS:")
                for video in videos_gerados:
                    self.log(f"   📹 {video}")
            
            # Log resumo no arquivo
            with open(log_filepath, 'a', encoding='utf-8') as f:
                f.write(f"\n📊 RESUMO DA GERAÇÃO:\n")
                f.write(f"   ✅ Sucessos: {sucessos}\n")
                f.write(f"   ❌ Erros: {erros}\n")
                f.write(f"⏰ Finalizado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                
                if videos_gerados:
                    f.write(f"\n🎬 VÍDEOS CRIADOS:\n")
                    for video in videos_gerados:
                        f.write(f"   📹 {video}\n")
            
            # Apenas log no console, sem popups
            self.log(f"🎯 Geração de vídeos finalizada")
                
        except Exception as e:
            self.log(f"❌ Erro inesperado: {str(e)}")
            with open(log_filepath, 'a', encoding='utf-8') as f:
                f.write(f"❌ Erro inesperado: {str(e)}\n")

    def gerar_video(self):
        pasta_stems = self.pasta_stems_var.get()
        pasta_karaoke = self.pasta_var.get()
        trilha_audio = self.trilha_audio_var.get()
        
        if not pasta_stems:
            messagebox.showerror("Erro", "Selecione a pasta de stems.")
            return
        
        if not os.path.exists(pasta_stems):
            messagebox.showerror("Erro", f"Pasta Stems não encontrada: {pasta_stems}")
            return
        
        if not pasta_karaoke:
            messagebox.showerror("Erro", "Selecione a pasta de karaokê.")
            return
        
        # Configurar sistema de log em arquivo
        raiz_projeto = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logs_path = os.path.join(raiz_projeto, 'logs')
        
        if not os.path.exists(logs_path):
            os.makedirs(logs_path)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"gerar_video_{timestamp}.log"
        log_filepath = os.path.join(logs_path, log_filename)
        
        # Iniciar log
        with open(log_filepath, 'w', encoding='utf-8') as f:
            f.write(f"🚀 Iniciando geração de vídeos - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"   📁 Pasta Stems: {pasta_stems}\n")
            f.write(f"   📁 Pasta Karaoke: {pasta_karaoke}\n")
            f.write(f"   🎵 Trilha de Áudio: {trilha_audio}\n\n")
        
        self.log(f"🚀 Iniciando geração de vídeos - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.log(f"   📁 Pasta Stems: {pasta_stems}")
        self.log(f"   📁 Pasta Karaoke: {pasta_karaoke}")
        self.log(f"   🎵 Trilha de Áudio: {trilha_audio}")
        self.log(f"   📄 Log: {log_filename}")
        
        # Encontrar projetos válidos
        projetos = self.encontrar_ultrastar_txt_em_stems(pasta_stems)
        
        if not projetos:
            self.log("❌ Nenhum projeto válido encontrado para geração.")
            with open(log_filepath, 'a', encoding='utf-8') as f:
                f.write("❌ Nenhum projeto válido encontrado para geração.\n")
            return
        
        self.log(f"📋 Total de projetos encontrados: {len(projetos)}")
        with open(log_filepath, 'a', encoding='utf-8') as f:
            f.write(f"📋 Total de projetos encontrados: {len(projetos)}\n")
        
        # Filtrar projetos que ainda não têm vídeo gerado
        projetos_para_gerar = []
        
        for projeto in projetos:
            nome_arquivo = projeto['artista_titulo']
            video_existente = self.verificar_se_video_ja_existe(nome_arquivo, pasta_karaoke)
            
            if video_existente:
                self.log(f"   ⏭️  Já existe: {nome_arquivo}")
                with open(log_filepath, 'a', encoding='utf-8') as f:
                    f.write(f"   ⏭️  Já existe: {nome_arquivo}\n")
            else:
                projetos_para_gerar.append(projeto)
                self.log(f"   ✅ Gerar: {nome_arquivo}")
                with open(log_filepath, 'a', encoding='utf-8') as f:
                    f.write(f"   ✅ Gerar: {nome_arquivo}\n")
        
        self.log(f"🎬 Projetos para gerar: {len(projetos_para_gerar)}")
        with open(log_filepath, 'a', encoding='utf-8') as f:
            f.write(f"\n🎬 Projetos para gerar: {len(projetos_para_gerar)}\n")
        
        if not projetos_para_gerar:
            self.log("✅ Todos os vídeos já estão gerados!")
            with open(log_filepath, 'a', encoding='utf-8') as f:
                f.write("✅ Todos os vídeos já estão gerados!\n")
            return
        
        # Executar geração em thread separada para não travar a interface
        thread = threading.Thread(
            target=self.executar_gerar_video_thread,
            args=(projetos_para_gerar, log_filepath)
        )
        thread.daemon = True
        thread.start()

    # ========== FUNÇÕES DOS SCRIPTS ORIGINAIS ==========

    def verificar(self):
        pasta = self.pasta_var.get()
        arquivo = self.arquivo_var.get()
        if not pasta or not arquivo: 
            messagebox.showerror("Erro", "Selecione pasta e arquivo .xlsx.")
            return
        self.log("🚀 Iniciando verificação de arquivos...")
        try: 
            verificar_arquivos.run(log_callback=self.log, pasta_videos=pasta, caminho_planilha=arquivo)
        except Exception as e: 
            self.log(f"❌ Erro: {str(e)}")
            messagebox.showerror("Erro", str(e))

    def gerar_thumbs(self):
        pasta = self.pasta_var.get()
        arquivo = self.arquivo_var.get()
        if not pasta: 
            messagebox.showerror("Erro", "Selecione a pasta de vídeos.")
            return
        self.log("🚀 Iniciando geração de thumbnails...")
        try: 
            gerar_thumb.run(log_callback=self.log, pasta_videos=pasta, arquivo_xlsx=arquivo)
        except Exception as e: 
            self.log(f"❌ Erro: {str(e)}")
            messagebox.showerror("Erro", str(e))

    def normalizar_nomes(self):
        pasta = self.pasta_var.get()
        arquivo = self.arquivo_var.get()
        if not pasta or not arquivo: 
            messagebox.showerror("Erro", "Selecione pasta e arquivo .xlsx.")
            return
        self.log("🚀 Iniciando normalização de nomes...")
        try: 
            normalizar_nomes.run(log_callback=self.log, pasta_videos=pasta, arquivo_xlsx=arquivo)
        except Exception as e: 
            self.log(f"❌ Erro: {str(e)}")
            messagebox.showerror("Erro", str(e))

    def gerar_nfo(self):
        pasta = self.pasta_var.get()
        arquivo = self.arquivo_var.get()
        if not pasta or not arquivo: 
            messagebox.showerror("Erro", "Selecione pasta e arquivo .xlsx.")
            return
        self.log("🚀 Iniciando geração de NFOs...")
        try: 
            gerar_nfo.run(log_callback=self.log, pasta_videos=pasta, arquivo_xlsx=arquivo)
        except Exception as e: 
            self.log(f"❌ Erro: {str(e)}")
            messagebox.showerror("Erro", str(e))

    def renomear_arquivos(self):
        pasta = self.pasta_var.get()
        arquivo = self.arquivo_var.get()
        if not pasta or not arquivo: 
            messagebox.showerror("Erro", "Selecione pasta e arquivo .xlsx.")
            return
        self.log("🚀 Iniciando renomeação de arquivos...")
        try: 
            renomear_arquivos.run(log_callback=self.log, pasta_videos=pasta, arquivo_xlsx=arquivo)
        except Exception as e: 
            self.log(f"❌ Erro: {str(e)}")
            messagebox.showerror("Erro", str(e))

    def excluir_thumbs(self):
        pasta = self.pasta_var.get()
        thumbs = []
        for root_dir, _, files in os.walk(pasta):
            for f in files:
                if f.lower().endswith('.jpg'):
                    thumbs.append(os.path.join(root_dir, f))
        if not thumbs:
            messagebox.showinfo("Info", "Nenhuma thumbnail .jpg encontrada.")
            return
        if messagebox.askyesno("Confirmação", f"Deseja excluir {len(thumbs)} thumbnails .jpg em todas as subpastas?"):
            for f in thumbs:
                try:
                    os.remove(f)
                except Exception as e:
                    self.log(f"   ⚠️  Erro ao excluir {f}: {e}")
            self.log(f"🗑️ {len(thumbs)} thumbnails excluídas em subpastas.")

    def excluir_nfos(self):
        pasta = self.pasta_var.get()
        nfos = []
        for root_dir, _, files in os.walk(pasta):
            for f in files:
                if f.lower().endswith('.nfo'):
                    nfos.append(os.path.join(root_dir, f))
        if not nfos:
            messagebox.showinfo("Info", "Nenhum arquivo .nfo encontrado.")
            return
        if messagebox.askyesno("Confirmação", f"Deseja excluir {len(nfos)} arquivos .nfo em todas as subpastas?"):
            for f in nfos:
                try:
                    os.remove(f)
                except Exception as e:
                    self.log(f"   ⚠️  Erro ao excluir {f}: {e}")
            self.log(f"🗑️ {len(nfos)} arquivos .nfo excluídos em subpastas.")

    def abrir_logs(self):
        raiz_projeto = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logs_path = os.path.join(raiz_projeto, 'logs')

        if not os.path.exists(logs_path):
            os.makedirs(logs_path)

        try:
            if os.name == 'nt':  # Windows
                subprocess.Popen(f'explorer "{logs_path}"')
            else:  # Linux/Mac
                subprocess.Popen(['xdg-open', logs_path])
            self.log(f"📂 Abrindo pasta de logs: {logs_path}")
        except Exception as e:
            self.log(f"❌ Erro ao abrir pasta de logs: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()