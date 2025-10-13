import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from dotenv import load_dotenv

# Carrega o .env
load_dotenv()

# Diretório raiz do projeto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(BASE_DIR)

# Lê variáveis do .env
pasta_env = os.getenv("PATH_PASTA_KARAOKE", "assets")
arquivo_env = os.getenv("PATH_ARQUIVO_KARAOKE", "assets/karaoke.xlsx")

# Caminhos absolutos
DEFAULT_PASTA_KARAOKE = os.path.join(BASE_DIR, pasta_env)
DEFAULT_ARQUIVO_KARAOKE = os.path.join(BASE_DIR, arquivo_env)

# Importação dos scripts
try:
    from scripts import verificar_arquivos, gerar_thumb, normalizar_nomes, gerar_nfo, renomear_arquivos
except ImportError:
    # Fallback para demonstração
    class MockScript:
        @staticmethod
        def run(*args, **kwargs):
            log_callback = kwargs.get('log_callback', print)
            log_callback("⚡ Simulação: Script executado com sucesso")
    
    verificar_arquivos = MockScript()
    gerar_thumb = MockScript()
    normalizar_nomes = MockScript()
    gerar_nfo = MockScript()

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎤 Emby Karaoke Checker - Professional")
        self.root.configure(bg='#2C3E50')
        self.root.geometry('900x700')
        
        # Variáveis
        self.pasta_var = tk.StringVar(value=DEFAULT_PASTA_KARAOKE)
        self.arquivo_var = tk.StringVar(value=DEFAULT_ARQUIVO_KARAOKE)
        
        self.setup_styles()
        
        # Frame principal com padding
        main_frame = tk.Frame(root, bg='#2C3E50', padx=20, pady=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Cabeçalho
        self.create_header(main_frame)
        
        # Seção de configurações
        self.create_settings_section(main_frame)
        
        # Seção de botões de ação
        self.create_actions_section(main_frame)
        
        # Seção de log
        self.create_log_section(main_frame)

    def setup_styles(self):
        self.colors = {
            'primary': '#3498DB',
            'secondary': '#2980B9',
            'success': '#27AE60',
            'warning': '#F39C12',
            'danger': '#E74C3C',
            'dark': '#2C3E50',
            'darker': '#1A252F',
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
        
        tk.Label(
            header_frame, 
            text="🎤 Emby Karaoke Checker", 
            font=self.fonts['title'],
            fg='white',
            bg=self.colors['dark'],
            pady=10
        ).pack()
        
        tk.Label(
            header_frame,
            text="Ferramenta completa para gerenciamento de biblioteca de karaokê",
            font=self.fonts['subtitle'],
            fg='#BDC3C7',
            bg=self.colors['dark'],
            pady=5
        ).pack()

    def create_settings_section(self, parent):
        settings_frame = tk.LabelFrame(
            parent, 
            text=" ⚙️ CONFIGURAÇÕES ", 
            font=self.fonts['label'],
            fg=self.colors['text'],
            bg=self.colors['light'],
            padx=15,
            pady=10
        )
        settings_frame.pack(fill=tk.X, pady=(0, 15))

        # Pasta Karaoke
        tk.Label(
            settings_frame, 
            text="Pasta Karaoke:", 
            font=self.fonts['label'],
            bg=self.colors['light']
        ).grid(row=0, column=0, sticky="w", pady=5)
        
        frame_pasta = tk.Frame(settings_frame, bg=self.colors['light'])
        frame_pasta.grid(row=0, column=1, sticky="ew", pady=5)
        
        entry_pasta = tk.Entry(
            frame_pasta, 
            textvariable=self.pasta_var, 
            width=60,
            font=('Segoe UI', 9),
            relief='solid',
            borderwidth=1
        )
        entry_pasta.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        tk.Button(
            frame_pasta, 
            text="📁 Selecionar", 
            command=self.selecionar_pasta,
            **self.get_button_style('secondary')
        ).pack(side=tk.RIGHT)

        # Arquivo XLSX
        tk.Label(
            settings_frame, 
            text="Arquivo Karaoke (.xlsx):", 
            font=self.fonts['label'],
            bg=self.colors['light']
        ).grid(row=1, column=0, sticky="w", pady=5)
        
        frame_arquivo = tk.Frame(settings_frame, bg=self.colors['light'])
        frame_arquivo.grid(row=1, column=1, sticky="ew", pady=5)
        
        entry_arquivo = tk.Entry(
            frame_arquivo, 
            textvariable=self.arquivo_var, 
            width=60,
            font=('Segoe UI', 9),
            relief='solid',
            borderwidth=1
        )
        entry_arquivo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        tk.Button(
            frame_arquivo, 
            text="📄 Selecionar", 
            command=self.selecionar_arquivo,
            **self.get_button_style('secondary')
        ).pack(side=tk.RIGHT)

        settings_frame.columnconfigure(1, weight=1)

    def create_actions_section(self, parent):
        actions_frame = tk.LabelFrame(
            parent, 
            text=" 🚀 AÇÕES ", 
            font=self.fonts['label'],
            fg=self.colors['text'],
            bg=self.colors['light'],
            padx=15,
            pady=10
        )
        actions_frame.pack(fill=tk.X, pady=(0, 15))

        # Botões em duas linhas para melhor organização
        button_frame1 = tk.Frame(actions_frame, bg=self.colors['light'])
        button_frame1.pack(fill=tk.X, pady=5)
        
        button_frame2 = tk.Frame(actions_frame, bg=self.colors['light'])
        button_frame2.pack(fill=tk.X, pady=5)

        tk.Button(
            button_frame1, 
            text="🔍 Verificar Arquivos", 
            command=self.verificar,
            **self.get_button_style('primary')
        ).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        tk.Button(
            button_frame1, 
            text="🖼️ Gerar Thumbnails", 
            command=self.gerar_thumbs,
            **self.get_button_style('success')
        ).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        tk.Button(
            button_frame2, 
            text="📝 Normalizar Nomes", 
            command=self.normalizar_nomes,
            **self.get_button_style('warning')
        ).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        tk.Button(
            button_frame2, 
            text="📋 Gerar NFO", 
            command=self.gerar_nfo,
            **self.get_button_style('danger')
        ).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        tk.Button(
        button_frame2, 
        text="✏️ Renomear Arquivos", 
        command=self.renomear_arquivos,
        **self.get_button_style('primary')
        ).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)


    def create_log_section(self, parent):
        log_frame = tk.LabelFrame(
            parent, 
            text=" 📊 LOG DE EXECUÇÃO ", 
            font=self.fonts['label'],
            fg=self.colors['text'],
            bg=self.colors['light'],
            padx=15,
            pady=10
        )
        log_frame.pack(fill=tk.BOTH, expand=True)

        self.txt_log = scrolledtext.ScrolledText(
            log_frame, 
            height=15, 
            width=80, 
            state="disabled",
            font=self.fonts['log'],
            bg='#1A252F',
            fg='#00FF00',
            insertbackground='white',
            selectbackground=self.colors['primary'],
            relief='solid',
            borderwidth=1,
            padx=10,
            pady=10
        )
        self.txt_log.pack(fill=tk.BOTH, expand=True)

    def get_button_style(self, color_type):
        return {
            'bg': self.colors[color_type],
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

    def verificar(self):
        pasta = self.pasta_var.get()
        arquivo = self.arquivo_var.get()

        if not pasta or not arquivo:
            messagebox.showerror("Erro", "Por favor, selecione a pasta e o arquivo .xlsx.")
            return

        self.log("🚀 Iniciando verificação de arquivos...")
        try:
            # CORREÇÃO AQUI: usar 'run' em vez de 'executar_verificacao'
            verificar_arquivos.run(log_callback=self.log, pasta_videos=pasta, caminho_planilha=arquivo)
            messagebox.showinfo("Concluído", "✅ Verificação finalizada! Confira o log acima.")
        except Exception as e:
            self.log(f"❌ Erro durante a verificação: {str(e)}")
            messagebox.showerror("Erro", f"Ocorreu um erro: {str(e)}")

    def gerar_thumbs(self):
        pasta = self.pasta_var.get()
        arquivo = self.arquivo_var.get()

        if not pasta:
            messagebox.showerror("Erro", "Selecione a pasta de vídeos.")
            return

        self.log("🚀 Iniciando geração de thumbnails...")
        try:
            gerar_thumb.run(log_callback=self.log, pasta_videos=pasta, arquivo_xlsx=arquivo)
            messagebox.showinfo("Concluído", "✅ Geração de thumbnails finalizada!")
        except Exception as e:
            self.log(f"❌ Erro durante geração de thumbnails: {str(e)}")
            messagebox.showerror("Erro", f"Ocorreu um erro: {str(e)}")

    def normalizar_nomes(self):
        pasta = self.pasta_var.get()
        arquivo = self.arquivo_var.get()

        if not pasta or not arquivo:
            messagebox.showerror("Erro", "Selecione a pasta e o arquivo .xlsx.")
            return

        self.log("🚀 Iniciando normalização de nomes...")
        try:
            normalizar_nomes.run(log_callback=self.log, pasta_videos=pasta, arquivo_xlsx=arquivo)
            messagebox.showinfo("Concluído", "✅ Normalização de nomes finalizada!")
        except Exception as e:
            self.log(f"❌ Erro durante normalização: {str(e)}")
            messagebox.showerror("Erro", f"Ocorreu um erro: {str(e)}")
    
    def gerar_nfo(self):
        pasta = self.pasta_var.get()
        arquivo = self.arquivo_var.get()

        if not pasta or not arquivo:
            messagebox.showerror("Erro", "Selecione a pasta e o arquivo .xlsx.")
            return

        self.log("🚀 Iniciando geração de NFOs...")
        try:
            gerar_nfo.run(log_callback=self.log, pasta_videos=pasta, arquivo_xlsx=arquivo)
            messagebox.showinfo("Concluído", "✅ Geração de NFOs finalizada!")
        except Exception as e:
            self.log(f"❌ Erro durante geração de NFO: {str(e)}")
            messagebox.showerror("Erro", f"Ocorreu um erro: {str(e)}")
    def renomear_arquivos(self):
        pasta = self.pasta_var.get()
        arquivo = self.arquivo_var.get()

        if not pasta or not arquivo:
            messagebox.showerror("Erro", "Selecione a pasta e o arquivo .xlsx.")
            return

        self.log("🚀 Iniciando renomeação de arquivos...")
        try:
            renomear_arquivos.run(log_callback=self.log, pasta_videos=pasta, arquivo_xlsx=arquivo)
            messagebox.showinfo("Concluído", "✅ Renomeação de arquivos finalizada!")
        except Exception as e:
            self.log(f"❌ Erro durante renomeação: {str(e)}")
            messagebox.showerror("Erro", f"Ocorreu um erro: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()