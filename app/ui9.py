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
        self.root.title("Emby Karaoke")
        self.root.configure(bg='#2C3E50')
        self.root.geometry('1000x850')
        
        self.pasta_var = tk.StringVar(value=DEFAULT_PASTA_KARAOKE)
        self.arquivo_var = tk.StringVar(value=DEFAULT_ARQUIVO_KARAOKE)
        self.pasta_stems_var = tk.StringVar(value=DEFAULT_PASTA_STEMS)
        self.trilha_audio_var = tk.StringVar(value="instrumental")
        
        self.setup_styles()
        main_frame = tk.Frame(root, bg='#2C3E50', padx=20, pady=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.create_header(main_frame)
        self.create_parameters_section(main_frame)
        
        # Container para Comandos/Utilitários e Log
        content_frame = tk.Frame(main_frame, bg='#2C3E50')
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Frame esquerdo para Comandos e Utilitários (mesma altura do Log)
        left_frame = tk.Frame(content_frame, bg='#2C3E50')
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 10))
        
        self.create_commands_section(left_frame)
        self.create_utilities_section(left_frame)
        
        # Frame direito para Log (mais espaço)
        right_frame = tk.Frame(content_frame, bg='#2C3E50')
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.create_log_section(right_frame)

    def setup_styles(self):
        self.colors = {
            'primary': '#3498DB',
            'secondary': '#2980B9',
            'dark': '#2C3E50',
            'darker': '#1A252F',
            'light': '#ECF0F1',
            'lighter': '#F8F9F9',
            'text': '#2C3E50',
            'text_light': '#7F8C8D',
            'success': '#27AE60',
            'warning': '#E67E22',
            'danger': '#E74C3C'
        }
        
        # Configuração de fontes
        self.fonts = {
            'title': self.load_font('PlayfairDisplay-Bold.ttf', 18, 'bold'),
            'subtitle': self.load_font('Lato-Light.ttf', 10),
            'section': self.load_font('Montserrat-Bold.ttf', 11, 'bold'),
            'label': self.load_font('OpenSans-Bold.ttf', 9, 'bold'),
            'button': self.load_font('Poppins-Bold.ttf', 9, 'bold'),
            'input': self.load_font('OpenSans-Regular.ttf', 9),
            'log': self.load_font('Consolas', 9),
            'dropdown': self.load_font('OpenSans-Regular.ttf', 9)
        }

    def load_font(self, font_name, size, weight='normal'):
        """Carrega fonte personalizada ou usa fallback"""
        font_path = os.path.join(BASE_DIR, 'assets', 'fonts', font_name)
        if os.path.exists(font_path):
            try:
                return (font_name.replace('.ttf', ''), size, weight)
            except:
                pass
        # Fallback para fontes padrão
        fallbacks = {
            'PlayfairDisplay-Bold.ttf': ('Arial', size, 'bold'),
            'Lato-Light.ttf': ('Arial', size),
            'Montserrat-Bold.ttf': ('Arial', size, 'bold'),
            'OpenSans-Bold.ttf': ('Arial', size, 'bold'),
            'OpenSans-Regular.ttf': ('Arial', size),
            'Poppins-Bold.ttf': ('Arial', size, 'bold'),
            'Poppins-Regular.ttf': ('Arial', size)
        }
        return fallbacks.get(font_name, ('Arial', size, weight))

    def create_header(self, parent):
        header_frame = tk.Frame(parent, bg=self.colors['dark'])
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = tk.Label(
            header_frame, 
            text="🎤 Emby Karaoke", 
            font=self.fonts['title'], 
            fg='white', 
            bg=self.colors['dark'], 
            pady=15
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            header_frame, 
            text="Ferramenta completa para gerenciamento de biblioteca de karaokê", 
            font=self.fonts['subtitle'], 
            fg='#BDC3C7', 
            bg=self.colors['dark'], 
            pady=5
        )
        subtitle_label.pack()

    def create_parameters_section(self, parent):
        parameters_frame = tk.LabelFrame(
            parent, 
            text=" ⚙️ PARÂMETROS ", 
            font=self.fonts['section'], 
            fg=self.colors['text'], 
            bg=self.colors['lighter'], 
            padx=15, 
            pady=12,
            relief='flat',
            bd=1,
            highlightbackground='#BDC3C7',
            highlightcolor='#BDC3C7'
        )
        parameters_frame.pack(fill=tk.X, pady=(0, 15))

        # Pasta Karaoke
        self.create_parameter_row(
            parameters_frame, 
            "Pasta Karaoke:", 
            self.pasta_var, 
            self.selecionar_pasta, 
            0
        )

        # Arquivo XLSX
        self.create_parameter_row(
            parameters_frame, 
            "Arquivo Karaoke (.xlsx):", 
            self.arquivo_var, 
            self.selecionar_arquivo, 
            1
        )

        # Pasta Stems
        self.create_parameter_row(
            parameters_frame, 
            "Pasta Stems:", 
            self.pasta_stems_var, 
            self.selecionar_pasta_stems, 
            2
        )

        # Trilha de Áudio
        tk.Label(
            parameters_frame, 
            text="Trilha de Áudio:", 
            font=self.fonts['label'], 
            bg=self.colors['lighter']
        ).grid(row=3, column=0, sticky="w", pady=8)
        
        frame_trilha = tk.Frame(parameters_frame, bg=self.colors['lighter'])
        frame_trilha.grid(row=3, column=1, sticky="w", pady=8)
        
        trilha_options = ["instrumental", "vocals", "mix"]
        
        # Estilo padrão para dropdown (não de botão)
        trilha_dropdown = tk.OptionMenu(
            frame_trilha, 
            self.trilha_audio_var, 
            *trilha_options
        )
        trilha_dropdown.config(
            font=self.fonts['dropdown'],
            bg='white',
            fg=self.colors['text'],
            relief='solid',
            borderwidth=1,
            width=12,
            highlightthickness=1,
            highlightbackground='#BDC3C7',
            anchor='w'
        )
        trilha_dropdown['menu'].config(
            bg='white',
            fg=self.colors['text'],
            font=self.fonts['dropdown']
        )
        trilha_dropdown.pack(side=tk.LEFT)
        
        parameters_frame.columnconfigure(1, weight=1)

    def create_parameter_row(self, parent, label_text, variable, command, row):
        """Cria uma linha de parâmetro com label, entry e botões"""
        tk.Label(
            parent, 
            text=label_text, 
            font=self.fonts['label'], 
            bg=self.colors['lighter']
        ).grid(row=row, column=0, sticky="w", pady=8)
        
        frame = tk.Frame(parent, bg=self.colors['lighter'])
        frame.grid(row=row, column=1, sticky="ew", pady=8)
        
        entry = tk.Entry(
            frame, 
            textvariable=variable, 
            width=60, 
            font=self.fonts['input'],
            bg='white',
            fg=self.colors['text'],
            relief='solid', 
            borderwidth=1,
            highlightthickness=1,
            highlightbackground='#BDC3C7',
            highlightcolor=self.colors['primary']
        )
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Botões com tamanho fixo
        btn_style = self.get_button_style('primary')
        btn_style['width'] = 10  # Tamanho fixo
        
        tk.Button(
            frame, 
            text="📁 Selecionar", 
            command=command, 
            **btn_style
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        tk.Button(
            frame, 
            text="📂 Abrir", 
            command=lambda: self.abrir_pasta_explorer(variable.get()), 
            **btn_style
        ).pack(side=tk.LEFT)

    def create_commands_section(self, parent):
        commands_frame = tk.LabelFrame(
            parent, 
            text=" 🚀 COMANDOS ", 
            font=self.fonts['section'], 
            fg=self.colors['text'], 
            bg=self.colors['lighter'], 
            padx=15, 
            pady=12,
            relief='flat',
            bd=1,
            highlightbackground='#BDC3C7',
            highlightcolor='#BDC3C7'
        )
        commands_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Frame para organizar os botões em grid
        grid_frame = tk.Frame(commands_frame, bg=self.colors['lighter'])
        grid_frame.pack(fill=tk.BOTH, expand=True)

        # Linhas de botões (3 por linha)
        button_frame1 = tk.Frame(grid_frame, bg=self.colors['lighter'])
        button_frame1.pack(fill=tk.X, pady=3)
        
        button_frame2 = tk.Frame(grid_frame, bg=self.colors['lighter'])
        button_frame2.pack(fill=tk.X, pady=3)
        
        button_frame3 = tk.Frame(grid_frame, bg=self.colors['lighter'])
        button_frame3.pack(fill=tk.X, pady=3)

        # Botões com tamanho fixo e bordas arredondadas
        btn_style = self.get_button_style('primary')
        btn_style['width'] = 16  # Tamanho fixo para todos os botões

        # Linha 1: Gerar Videos, Gerar NFOs, Gerar Thumbs
        tk.Button(button_frame1, text="🎬 Gerar Videos", command=self.gerar_video, **btn_style).pack(side=tk.LEFT, padx=2)
        tk.Button(button_frame1, text="📋 Gerar NFOs", command=self.gerar_nfo, **btn_style).pack(side=tk.LEFT, padx=2)
        tk.Button(button_frame1, text="🖼️ Gerar Thumbs", command=self.gerar_thumbs, **btn_style).pack(side=tk.LEFT, padx=2)

        # Linha 2: Normalizar Nomes, Verificar Arquivos, Renomear Arquivos
        tk.Button(button_frame2, text="📝 Normalizar Nomes", command=self.normalizar_nomes, **btn_style).pack(side=tk.LEFT, padx=2)
        tk.Button(button_frame2, text="🔍 Verificar Arquivos", command=self.verificar, **btn_style).pack(side=tk.LEFT, padx=2)
        tk.Button(button_frame2, text="✏️ Renomear Arquivos", command=self.renomear_arquivos, **btn_style).pack(side=tk.LEFT, padx=2)

        # Linha 3: Excluir Thumbs, Excluir NFOs
        tk.Button(button_frame3, text="🗑️ Excluir Thumbs", command=self.excluir_thumbs, **btn_style).pack(side=tk.LEFT, padx=2)
        tk.Button(button_frame3, text="🗑️ Excluir NFOs", command=self.excluir_nfos, **btn_style).pack(side=tk.LEFT, padx=2)

    def create_utilities_section(self, parent):
        utilities_frame = tk.LabelFrame(
            parent, 
            text=" 🛠️ UTILITÁRIOS ", 
            font=self.fonts['section'], 
            fg=self.colors['text'], 
            bg=self.colors['lighter'], 
            padx=15, 
            pady=12,
            relief='flat',
            bd=1,
            highlightbackground='#BDC3C7',
            highlightcolor='#BDC3C7'
        )
        utilities_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 0))

        # Frame para organizar os botões em grid (3 por linha)
        grid_frame = tk.Frame(utilities_frame, bg=self.colors['lighter'])
        grid_frame.pack(fill=tk.BOTH, expand=True)

        # Linhas de botões (3 por linha)
        button_frame1 = tk.Frame(grid_frame, bg=self.colors['lighter'])
        button_frame1.pack(fill=tk.X, pady=3)
        
        button_frame2 = tk.Frame(grid_frame, bg=self.colors['lighter'])
        button_frame2.pack(fill=tk.X, pady=3)

        # Botões de utilitários com tamanho fixo e bordas arredondadas
        btn_style = self.get_button_style('secondary')
        btn_style['width'] = 16  # Tamanho fixo

        # Linha 1: Enviar Songs.xlsx, Abrir Output, Abrir Logs
        tk.Button(button_frame1, text="📤 Enviar Songs.xlsx", command=self.enviar_songs_xlsx, **btn_style).pack(side=tk.LEFT, padx=2)
        tk.Button(button_frame1, text="📁 Abrir Output", command=self.abrir_pasta_output, **btn_style).pack(side=tk.LEFT, padx=2)
        tk.Button(button_frame1, text="📂 Abrir Logs", command=self.abrir_logs, **btn_style).pack(side=tk.LEFT, padx=2)

        # Linha 2: Abrir Imagens, Enviar Karaoke
        tk.Button(button_frame2, text="🖼️ Abrir Imagens", command=self.abrir_pasta_imagens, **btn_style).pack(side=tk.LEFT, padx=2)
        tk.Button(button_frame2, text="🚀 Enviar Karaoke", command=self.enviar_karaoke, **btn_style).pack(side=tk.LEFT, padx=2)

    def create_log_section(self, parent):
        log_frame = tk.LabelFrame(
            parent, 
            text=" 📊 LOG DE EXECUÇÃO ", 
            font=self.fonts['section'], 
            fg=self.colors['text'], 
            bg=self.colors['lighter'], 
            padx=15, 
            pady=12,
            relief='flat',
            bd=1,
            highlightbackground='#BDC3C7',
            highlightcolor='#BDC3C7'
        )
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.txt_log = scrolledtext.ScrolledText(
            log_frame, 
            height=20, 
            width=80, 
            state="disabled", 
            font=self.fonts['log'], 
            bg='#1A252F', 
            fg='#00FF00', 
            insertbackground='white', 
            selectbackground=self.colors['primary'], 
            relief='solid', 
            borderwidth=1, 
            padx=12, 
            pady=12,
            wrap=tk.WORD
        )
        self.txt_log.pack(fill=tk.BOTH, expand=True)

    def get_button_style(self, color_type):
        colors = {
            'primary': {'bg': self.colors['primary'], 'fg': 'white'},
            'secondary': {'bg': self.colors['secondary'], 'fg': 'white'},
            'success': {'bg': self.colors['success'], 'fg': 'white'},
            'warning': {'bg': self.colors['warning'], 'fg': 'white'},
            'danger': {'bg': self.colors['danger'], 'fg': 'white'}
        }
        
        color_set = colors.get(color_type, colors['primary'])
        
        return {
            'bg': color_set['bg'], 
            'fg': color_set['fg'], 
            'font': self.fonts['button'], 
            'relief': 'flat',
            'borderwidth': 0, 
            'padx': 12, 
            'pady': 8, 
            'cursor': 'hand2',
            'width': 16,
            'highlightbackground': color_set['bg'],
            'highlightthickness': 1,
            'bd': 0
        }

    # ========== FUNÇÃO CORRIGIDA: VERIFICAR SE VÍDEO JÁ EXISTE ==========

    def normalizar_nome_arquivo(self, nome):
        """Normaliza o nome do arquivo para comparação robusta"""
        if not nome:
            return ""
        
        # Converter para minúsculas
        nome = nome.lower()
        
        # Substituir caracteres problemáticos
        nome = nome.replace('&', 'e')
        nome = nome.replace('  ', ' ')
        nome = nome.replace('_', ' ')
        nome = nome.replace('-', ' ')
        
        # Remover espaços extras e caracteres especiais
        nome = ''.join(c for c in nome if c.isalnum() or c in (' ', '-', '_'))
        nome = ' '.join(nome.split())  # Remove espaços múltiplos
        nome = nome.strip()
        
        return nome

    def verificar_se_video_ja_existe(self, nome_arquivo, pasta_karaoke):
        """Verifica se o vídeo já existe na pasta karaoke (em qualquer subpasta)"""
        try:
            # Normalizar o nome do arquivo
            nome_normalizado = self.normalizar_nome_arquivo(nome_arquivo)
            
            for root_dir, _, files in os.walk(pasta_karaoke):
                for arquivo in files:
                    # Verificar apenas arquivos de vídeo
                    if not arquivo.lower().endswith(('.mp4', '.avi', '.mkv', '.mov')):
                        continue
                    
                    nome_sem_extensao = os.path.splitext(arquivo)[0]
                    nome_arquivo_normalizado = self.normalizar_nome_arquivo(nome_sem_extensao)
                    
                    # Múltiplas estratégias de comparação
                    if (nome_normalizado == nome_arquivo_normalizado or
                        nome_normalizado in nome_arquivo_normalizado or
                        nome_arquivo_normalizado in nome_normalizado):
                        
                        return os.path.join(root_dir, arquivo)
            
            return None
            
        except Exception as e:
            self.log(f"❌ Erro ao verificar vídeo: {e}")
            return None

    # ========== FUNÇÃO AJUSTADA: EXECUTAR GERAR VIDEO SEM JANELAS ==========

    def executar_gerar_video_com_progresso(self, comando, projeto, log_filepath):
        """Executa o comando e captura o progresso em tempo real"""
        try:
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            env['PYTHONUTF8'] = '1'
            
            # Configuração para evitar janelas do terminal no Windows (APENAS PARA FFMPEG)
            startupinfo = None
            if os.name == 'nt':  # Windows
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = 0  # SW_HIDE - esconde a janela
            
            processo = subprocess.Popen(
                comando,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='ignore',
                cwd=BASE_DIR,
                env=env,
                bufsize=1,
                universal_newlines=True,
                startupinfo=startupinfo  # MANTIDO APENAS AQUI PARA FFMPEG
            )
            
            while True:
                linha = processo.stdout.readline()
                if not linha and processo.poll() is not None:
                    break
                
                if linha:
                    linha = linha.strip()
                    if linha:
                        if any(palavra in linha for palavra in ['Rolagem:', 'Finalizando...', '✅ Vídeo com Rolagem', '📤 Finalizando']):
                            self.log(f"   📊 {linha}")
                        elif any(palavra in linha for palavra in ['🚀 Gerador de Karaokê', '📺 Resolução:', '🎵 Música:', '🎤 Artista:', '⏱️  Duração:']):
                            self.log(f"   ℹ️  {linha}")
                        elif '❌' in linha or 'Erro:' in linha or 'Traceback' in linha:
                            self.log(f"   {linha}")
            
            returncode = processo.wait()
            return returncode, ""
            
        except Exception as e:
            return 1, f"Erro ao executar processo: {str(e)}"

    # ========== FUNÇÕES CORRIGIDAS: EXPLORER FUNCIONANDO ==========

    def abrir_pasta_explorer(self, caminho):
        """Abre uma pasta no explorador de arquivos"""
        if not caminho:
            messagebox.showwarning("Aviso", "Nenhum caminho selecionado.")
            return
        
        # Se for um arquivo, pegar o diretório pai
        if os.path.isfile(caminho):
            caminho = os.path.dirname(caminho)
        
        # Criar pasta se não existir
        if not os.path.exists(caminho):
            try:
                os.makedirs(caminho)
                self.log(f"📁 Pasta criada: {caminho}")
            except Exception as e:
                self.log(f"❌ Erro ao criar pasta: {e}")
                messagebox.showerror("Erro", f"Não foi possível criar a pasta: {e}")
                return
        
        try:
            # SEM startupinfo para o Explorer funcionar normalmente
            if os.name == 'nt':  # Windows
                subprocess.Popen(f'explorer "{caminho}"')
            else:  # Linux/Mac
                subprocess.Popen(['xdg-open', caminho])
            self.log(f"📂 Abrindo pasta: {caminho}")
        except Exception as e:
            self.log(f"❌ Erro ao abrir pasta: {e}")
            messagebox.showerror("Erro", f"Não foi possível abrir a pasta: {e}")

    def abrir_pasta_output(self):
        """Abre a pasta Output onde os vídeos são gerados"""
        output_path = os.path.join(BASE_DIR, "Output")
        
        if not os.path.exists(output_path):
            os.makedirs(output_path)
            self.log(f"📁 Pasta Output criada: {output_path}")

        try:
            # SEM startupinfo para o Explorer funcionar normalmente
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
            # SEM startupinfo para o Explorer funcionar normalmente
            if os.name == 'nt':  # Windows
                subprocess.Popen(f'explorer "{imagens_path}"')
            else:  # Linux/Mac
                subprocess.Popen(['xdg-open', imagens_path])
            self.log(f"🖼️ Abrindo pasta de imagens: {imagens_path}")
        except Exception as e:
            self.log(f"❌ Erro ao abrir pasta de imagens: {e}")

    def abrir_logs(self):
        raiz_projeto = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logs_path = os.path.join(raiz_projeto, 'logs')

        if not os.path.exists(logs_path):
            os.makedirs(logs_path)

        try:
            # SEM startupinfo para o Explorer funcionar normalmente
            if os.name == 'nt':  # Windows
                subprocess.Popen(f'explorer "{logs_path}"')
            else:  # Linux/Mac
                subprocess.Popen(['xdg-open', logs_path])
            self.log(f"📂 Abrindo pasta de logs: {logs_path}")
        except Exception as e:
            self.log(f"❌ Erro ao abrir pasta de logs: {e}")

    # ========== NOVA FUNÇÃO: ENVIAR KARAOKE ==========

    def enviar_karaoke(self):
        """Envia os vídeos da pasta Output para a pasta Karaoke"""
        pasta_output = os.path.join(BASE_DIR, "Output")
        pasta_karaoke = self.pasta_var.get()
        
        if not pasta_karaoke:
            messagebox.showerror("Erro", "Selecione a pasta de karaokê.")
            return
        
        if not os.path.exists(pasta_output):
            self.log("❌ Pasta Output não encontrada.")
            messagebox.showerror("Erro", "Pasta Output não encontrada.")
            return
        
        # Configurar sistema de log em arquivo
        raiz_projeto = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logs_path = os.path.join(raiz_projeto, 'logs')
        
        if not os.path.exists(logs_path):
            os.makedirs(logs_path)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"enviar_karaoke_{timestamp}.log"
        log_filepath = os.path.join(logs_path, log_filename)
        
        # Iniciar log
        with open(log_filepath, 'w', encoding='utf-8') as f:
            f.write(f"🚀 Iniciando envio de karaokê - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"   📁 Pasta Output: {pasta_output}\n")
            f.write(f"   📁 Pasta Karaoke: {pasta_karaoke}\n\n")
        
        self.log(f"🚀 Iniciando envio de karaokê - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.log(f"   📁 Pasta Output: {pasta_output}")
        self.log(f"   📁 Pasta Karaoke: {pasta_karaoke}")
        self.log(f"   📄 Log: {log_filename}")
        
        # Executar em thread separada
        thread = threading.Thread(
            target=self.executar_enviar_karaoke_thread,
            args=(pasta_output, pasta_karaoke, log_filepath)
        )
        thread.daemon = True
        thread.start()

    def executar_enviar_karaoke_thread(self, pasta_output, pasta_karaoke, log_filepath):
        """Executa o envio de karaokê em thread separada"""
        try:
            videos_enviados = []
            erros = 0
            
            # Verificar se a pasta Output existe
            if not os.path.exists(pasta_output):
                self.log("❌ Pasta Output não encontrada.")
                with open(log_filepath, 'a', encoding='utf-8') as f:
                    f.write("❌ Pasta Output não encontrada.\n")
                return
            
            # Listar arquivos de vídeo na pasta Output
            arquivos_video = []
            for arquivo in os.listdir(pasta_output):
                if arquivo.lower().endswith(('.mp4', '.avi', '.mkv', '.mov')):
                    arquivos_video.append(arquivo)
            
            if not arquivos_video:
                self.log("📭 Nenhum vídeo encontrado na pasta Output.")
                with open(log_filepath, 'a', encoding='utf-8') as f:
                    f.write("📭 Nenhum vídeo encontrado na pasta Output.\n")
                return
            
            self.log(f"📋 Total de vídeos encontrados: {len(arquivos_video)}")
            with open(log_filepath, 'a', encoding='utf-8') as f:
                f.write(f"📋 Total de vídeos encontrados: {len(arquivos_video)}\n")
            
            # Criar pasta karaoke se não existir
            if not os.path.exists(pasta_karaoke):
                try:
                    os.makedirs(pasta_karaoke)
                    self.log(f"📁 Pasta karaoke criada: {pasta_karaoke}")
                    with open(log_filepath, 'a', encoding='utf-8') as f:
                        f.write(f"📁 Pasta karaoke criada: {pasta_karaoke}\n")
                except Exception as e:
                    self.log(f"❌ Erro ao criar pasta karaoke: {e}")
                    with open(log_filepath, 'a', encoding='utf-8') as f:
                        f.write(f"❌ Erro ao criar pasta karaoke: {e}\n")
                    return
            
            # Processar cada vídeo
            for i, arquivo in enumerate(arquivos_video, 1):
                caminho_origem = os.path.join(pasta_output, arquivo)
                caminho_destino = os.path.join(pasta_karaoke, arquivo)
                
                self.log(f"📦 Processando ({i}/{len(arquivos_video)}): {arquivo}")
                with open(log_filepath, 'a', encoding='utf-8') as f:
                    f.write(f"📦 Processando ({i}/{len(arquivos_video)}): {arquivo}\n")
                
                try:
                    # Verificar se o arquivo já existe no destino
                    if os.path.exists(caminho_destino):
                        self.log(f"   ⚠️  Arquivo já existe: {arquivo}")
                        with open(log_filepath, 'a', encoding='utf-8') as f:
                            f.write(f"   ⚠️  Arquivo já existe: {arquivo}\n")
                        continue
                    
                    # Copiar arquivo
                    shutil.copy2(caminho_origem, caminho_destino)
                    
                    # Verificar se a cópia foi bem sucedida
                    if os.path.exists(caminho_destino):
                        videos_enviados.append(arquivo)
                        self.log(f"   ✅ Enviado: {arquivo}")
                        with open(log_filepath, 'a', encoding='utf-8') as f:
                            f.write(f"   ✅ Enviado: {arquivo}\n")
                    else:
                        erros += 1
                        self.log(f"   ❌ Falha ao enviar: {arquivo}")
                        with open(log_filepath, 'a', encoding='utf-8') as f:
                            f.write(f"   ❌ Falha ao enviar: {arquivo}\n")
                            
                except Exception as e:
                    erros += 1
                    self.log(f"   ❌ Erro ao processar {arquivo}: {str(e)}")
                    with open(log_filepath, 'a', encoding='utf-8') as f:
                        f.write(f"   ❌ Erro ao processar {arquivo}: {str(e)}\n")
            
            # Resumo final
            self.log(f"\n📊 RESUMO DO ENVIO:")
            self.log(f"   ✅ Vídeos enviados: {len(videos_enviados)}")
            self.log(f"   ❌ Erros: {erros}")
            
            if videos_enviados:
                self.log(f"\n🎬 VÍDEOS ENVIADOS:")
                for video in videos_enviados:
                    self.log(f"   📹 {video}")
            
            # Log resumo no arquivo
            with open(log_filepath, 'a', encoding='utf-8') as f:
                f.write(f"\n📊 RESUMO DO ENVIO:\n")
                f.write(f"   ✅ Vídeos enviados: {len(videos_enviados)}\n")
                f.write(f"   ❌ Erros: {erros}\n")
                f.write(f"⏰ Finalizado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                
                if videos_enviados:
                    f.write(f"\n🎬 VÍDEOS ENVIADOS:\n")
                    for video in videos_enviados:
                        f.write(f"   📹 {video}\n")
            
            self.log(f"🎯 Envio de karaokê finalizado")
                
        except Exception as e:
            self.log(f"❌ Erro inesperado: {str(e)}")
            with open(log_filepath, 'a', encoding='utf-8') as f:
                f.write(f"❌ Erro inesperado: {str(e)}\n")

    # ========== FUNÇÕES EXISTENTES ==========

    def log(self, mensagem):
        self.txt_log.config(state="normal")
        self.txt_log.insert(tk.END, mensagem + "\n")
        self.txt_log.see(tk.END)
        self.txt_log.config(state="disabled")

    def enviar_songs_xlsx(self):
        """Permite ao usuário enviar uma nova planilha Songs.xlsx"""
        arquivo_novo = filedialog.askopenfilename(
            title="Selecionar nova planilha Songs.xlsx",
            filetypes=[("Planilhas Excel", "*.xlsx"), ("Todos os arquivos", "*.*")]
        )
        
        if not arquivo_novo:
            return
        
        songs_atual = os.path.join(BASE_DIR, "assets", "Songs.xlsx")
        songs_backup_dir = os.path.join(BASE_DIR, "assets", "backups")
        
        try:
            if not os.path.exists(songs_backup_dir):
                os.makedirs(songs_backup_dir)
            
            if os.path.exists(songs_atual):
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                nome_backup = f"Songs_old_{timestamp}.xlsx"
                caminho_backup = os.path.join(songs_backup_dir, nome_backup)
                
                shutil.copy2(songs_atual, caminho_backup)
                self.log(f"📦 Backup criado: {nome_backup}")
            
            shutil.copy2(arquivo_novo, songs_atual)
            self.log(f"✅ Nova planilha enviada: {os.path.basename(arquivo_novo)}")
            self.log(f"📊 Songs.xlsx atualizado com sucesso!")
            
            self.arquivo_var.set(songs_atual)
            
        except Exception as e:
            self.log(f"❌ Erro ao enviar planilha: {str(e)}")
            messagebox.showerror("Erro", f"Erro ao enviar planilha: {str(e)}")

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

    def encontrar_imagem_artista(self, nome_artista):
        """Encontra imagem do artista na pasta assets/__artist"""
        pasta_artistas = os.path.join(BASE_DIR, "assets", "__artist")
        
        if not os.path.exists(pasta_artistas):
            return None
        
        artista = nome_artista.split(" - ")[0].strip()
        
        extensoes = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp','avif']
        
        for ext in extensoes:
            caminho_imagem = os.path.join(pasta_artistas, f"{artista}{ext}")
            if os.path.exists(caminho_imagem):
                return caminho_imagem
        
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
            
            if os.path.isdir(caminho_completo) and " - " in item:
                artista_titulo = item
                caminho_ultrastar = os.path.join(caminho_completo, "ultrastar.txt")
                
                if os.path.exists(caminho_ultrastar):
                    trilha_audio = self.trilha_audio_var.get() + ".mp3"
                    caminho_audio = os.path.join(caminho_completo, trilha_audio)
                    
                    if os.path.exists(caminho_audio):
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

    def executar_gerar_video_thread(self, projetos_para_gerar, log_filepath):
        """Executa a geração de vídeos em thread separada"""
        try:
            videos_gerados = []
            sucessos = 0
            erros = 0
            
            python_executable = sys.executable
            
            for i, projeto in enumerate(projetos_para_gerar, 1):
                self.log(f"🎬 Processando ({i}/{len(projetos_para_gerar)}): {projeto['artista_titulo']}")
                
                if not os.path.exists(projeto['ultrastar_txt']):
                    self.log(f"   ❌ Arquivo ultrastar.txt não encontrado: {projeto['ultrastar_txt']}")
                    erros += 1
                    continue
                    
                if not os.path.exists(projeto['arquivo_audio']):
                    self.log(f"   ❌ Arquivo de áudio não encontrado: {projeto['arquivo_audio']}")
                    erros += 1
                    continue
                
                comando = [
                    python_executable, 
                    'scripts/gerar_video.py',
                    projeto['ultrastar_txt'],
                    '--audio', projeto['arquivo_audio']
                ]
                
                if projeto['imagem_artista']:
                    comando.extend(['--background', projeto['imagem_artista']])
                    self.log(f"   🖼️  Usando imagem do artista: {os.path.basename(projeto['imagem_artista'])}")
                
                self.log(f"   🔧 Iniciando geração de vídeo...")
                
                try:
                    returncode, erro_msg = self.executar_gerar_video_com_progresso(comando, projeto, log_filepath)
                    
                    if returncode == 0:
                        sucessos += 1
                        output_file = os.path.join(BASE_DIR, "Output", f"{projeto['artista_titulo']}.mp4")
                        if os.path.exists(output_file):
                            videos_gerados.append(f"{projeto['artista_titulo']}.mp4")
                            self.log(f"   ✅ Vídeo criado com sucesso: {projeto['artista_titulo']}.mp4")
                            
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
            
            self.log(f"\n📊 RESUMO DA GERAÇÃO:")
            self.log(f"   ✅ Sucessos: {sucessos}")
            self.log(f"   ❌ Erros: {erros}")
            
            if videos_gerados:
                self.log(f"\n🎬 VÍDEOS CRIADOS:")
                for video in videos_gerados:
                    self.log(f"   📹 {video}")
            
            with open(log_filepath, 'a', encoding='utf-8') as f:
                f.write(f"\n📊 RESUMO DA GERAÇÃO:\n")
                f.write(f"   ✅ Sucessos: {sucessos}\n")
                f.write(f"   ❌ Erros: {erros}\n")
                f.write(f"⏰ Finalizado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                
                if videos_gerados:
                    f.write(f"\n🎬 VÍDEOS CRIADOS:\n")
                    for video in videos_gerados:
                        f.write(f"   📹 {video}\n")
            
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
        
        raiz_projeto = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logs_path = os.path.join(raiz_projeto, 'logs')
        
        if not os.path.exists(logs_path):
            os.makedirs(logs_path)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"gerar_video_{timestamp}.log"
        log_filepath = os.path.join(logs_path, log_filename)
        
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
        
        projetos = self.encontrar_ultrastar_txt_em_stems(pasta_stems)
        
        if not projetos:
            self.log("❌ Nenhum projeto válido encontrado para geração.")
            with open(log_filepath, 'a', encoding='utf-8') as f:
                f.write("❌ Nenhum projeto válido encontrado para geração.\n")
            return
        
        self.log(f"📋 Total de projetos encontrados: {len(projetos)}")
        with open(log_filepath, 'a', encoding='utf-8') as f:
            f.write(f"📋 Total de projetos encontrados: {len(projetos)}\n")
        
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

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()