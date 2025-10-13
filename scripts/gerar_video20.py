#!/usr/bin/env python3
"""
Gerador de Vídeo Karaokê ULTRA RÁPIDO - Com Efeito de Rolagem
Versão com sincronização corrigida (sem atraso)
"""

import re
import os
import sys
import math
import time
import platform
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import subprocess
import shutil
import threading

# ==================== CONFIGURAÇÕES OTIMIZADAS ====================

def find_ffmpeg_tools():
    """Encontra FFmpeg e FFprobe no sistema"""
    base_paths = [
        r"C:\ffmpeg\bin",
        r"C:\ffmpeg",
        r"C:\Program Files\ffmpeg\bin",
        r"C:\Program Files (x86)\ffmpeg\bin"
    ]
    
    ffmpeg_path = None
    ffprobe_path = None
    
    for base_path in base_paths:
        ffmpeg_candidate = os.path.join(base_path, "ffmpeg.exe")
        ffprobe_candidate = os.path.join(base_path, "ffprobe.exe")
        
        if os.path.exists(ffmpeg_candidate):
            ffmpeg_path = ffmpeg_candidate
        if os.path.exists(ffprobe_candidate):
            ffprobe_path = ffprobe_candidate
        
        if ffmpeg_path and ffprobe_path:
            break
    
    if not ffmpeg_path:
        ffmpeg_path = shutil.which("ffmpeg")
    if not ffprobe_path:
        ffprobe_path = shutil.which("ffprobe")
    
    return ffmpeg_path, ffprobe_path

def get_custom_fonts(project_root):
    """Carrega fontes personalizadas da pasta fonts com verificação detalhada"""
    fonts_dir = os.path.join(project_root, "assets", "fonts")
    fonts_dir = os.path.abspath(fonts_dir)
    
    print(f"🔍 Procurando fontes em: {fonts_dir}")
    
    font_files = {
        'playfair_bold': os.path.join(fonts_dir, "PlayfairDisplay-Bold.ttf"),
        'lato_light': os.path.join(fonts_dir, "Lato-Light.ttf"),
        'poppins_bold': os.path.join(fonts_dir, "Poppins-Bold.ttf"),
        'poppins_regular': os.path.join(fonts_dir, "Poppins-Regular.ttf")
    }
    
    available_fonts = {}
    for key, path in font_files.items():
        if os.path.exists(path):
            available_fonts[key] = path
            print(f"   ✅ Encontrada: {os.path.basename(path)}")
        else:
            print(f"   ❌ Não encontrada: {path}")
    
    if not os.path.exists(fonts_dir):
        print(f"   ⚠️  Pasta fonts não existe: {fonts_dir}")
        print(f"   💡 Crie a pasta 'fonts' em assets/fonts do projeto")
    
    if os.path.exists(fonts_dir):
        print(f"   📁 Arquivos na pasta fonts:")
        for arquivo in os.listdir(fonts_dir):
            print(f"      - {arquivo}")
    
    if not available_fonts:
        print("⚠️  Usando fontes do sistema como fallback")
        system = platform.system().lower()
        if system == 'windows':
            available_fonts = {
                'playfair_bold': r"C:\Windows\Fonts\georgia.ttf",
                'lato_light': r"C:\Windows\Fonts\segoeui.ttf",
                'poppins_bold': r"C:\Windows\Fonts\arialbd.ttf",
                'poppins_regular': r"C:\Windows\Fonts\arial.ttf"
            }
    
    return available_fonts

def test_amd_encoder(ffmpeg_path):
    """Testa se o encoder AMD funciona"""
    try:
        print("   🧪 Testando encoder AMD...")
        test_cmd = [
            ffmpeg_path, '-f', 'lavfi', '-i', 'testsrc=duration=1:size=320x240:rate=1', 
            '-c:v', 'h264_amf', '-b:v', '1M', '-f', 'null', '-', '-y'
        ]
        result = subprocess.run(test_cmd, capture_output=True, timeout=8)
        success = result.returncode == 0
        print(f"   {'✅' if success else '❌'} Teste AMD: {'OK' if success else 'FALHOU'}")
        return success
    except Exception as e:
        print(f"   ❌ Teste AMD falhou: {str(e)[:30]}...")
        return False

def detect_gpu_optimized(ffmpeg_path):
    """Detecção otimizada de GPU"""
    if not ffmpeg_path:
        return 'libx264', 'CPU', []
    
    try:
        print("🔍 Detectando encoders disponíveis...")
        result = subprocess.run([ffmpeg_path, '-hide_banner', '-encoders'], 
                              capture_output=True, text=True, timeout=5)
        
        if result.returncode != 0:
            return 'libx264', 'CPU', []
        
        encoders = result.stdout.lower()
        
        if 'h264_amf' in encoders:
            if test_amd_encoder(ffmpeg_path):
                amd_params = [
                    '-c:v', 'h264_amf', 
                    '-b:v', '4M',
                    '-maxrate', '6M',
                    '-bufsize', '8M',
                    '-threads', '0'
                ]
                return 'h264_amf', 'AMD Radeon', amd_params
        
        if 'h264_nvenc' in encoders:
            try:
                print("   🧪 Testando encoder NVIDIA...")
                test = subprocess.run([ffmpeg_path, '-f', 'lavfi', '-i', 'testsrc=duration=1:size=320x240:rate=1', 
                                     '-c:v', 'h264_nvenc', '-f', 'null', '-', '-y'], 
                                    capture_output=True, timeout=8)
                if test.returncode == 0:
                    print("   ✅ Teste NVIDIA: OK")
                    nvidia_params = ['-c:v', 'h264_nvenc', '-preset', 'fast', '-b:v', '4M']
                    return 'h264_nvenc', 'NVIDIA', nvidia_params
            except:
                print("   ❌ Teste NVIDIA: ERRO")
                
    except Exception as e:
        print(f"   ❌ Erro na detecção: {str(e)[:30]}...")
    
    print("   💻 Usando CPU como fallback")
    cpu_params = ['-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '28', '-threads', '0']
    return 'libx264', 'CPU', cpu_params

# ==================== EFEITOS VISUAIS OTIMIZADOS ====================

def desenhar_ondas(draw_obj, largura, altura, cor_onda, num_ondas=4, intensidade=0.08):
    """Desenha ondas com menos detalhes para velocidade"""
    for i in range(num_ondas):
        amplitude = altura / (num_ondas * 2) * (i + 1) / num_ondas * 0.8
        frequencia = 0.005 + i * 0.001
        offset_y = altura / num_ondas * i + (altura / (num_ondas * 2))
        cor_onda_rgba = cor_onda + (int(255 * intensidade),) 
        pontos = []
        for x in range(0, largura + 1, 4):
            y = int(offset_y + amplitude * math.sin(frequencia * x + i * 0.5))
            pontos.append((x, y))
        if pontos:
            pontos_preenchimento = [(0, altura)] + pontos + [(largura, altura)]
            draw_obj.polygon(pontos_preenchimento, fill=cor_onda_rgba)

# ==================== PARSER ULTRASTAR ====================

class UltraStarParser:
    def __init__(self, filepath):
        self.filepath = filepath
        self.header = {}
        self.notes = []
        self.parse_file()
    
    def parse_file(self):
        with open(self.filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('#'):
                    self.parse_header(line)
                elif line.startswith(':'):
                    self.parse_note(line)
                elif line.startswith('-'):
                    self.notes.append({'type': 'break', 'beat': int(line.split()[1]) if len(line.split()) > 1 else 0})
                elif line.startswith('E'):
                    break
    
    def parse_header(self, line):
        match = re.match(r'#(\w+):(.+)', line)
        if match:
            key, value = match.groups()
            self.header[key] = value.strip()
    
    def parse_note(self, line):
        parts = line.split()
        if len(parts) >= 4:
            note = {
                'type': 'note',
                'beat': int(parts[1]),
                'duration': int(parts[2]),
                'pitch': int(parts[3]),
                'text': ' '.join(parts[4:]) if len(parts) > 4 else ''
            }
            self.notes.append(note)
    
    def beat_to_seconds(self, beat):
        bpm = float(self.header.get('BPM', 120))
        gap = float(self.header.get('GAP', 0)) / 1000
        seconds = (beat * 60) / (bpm * 4) + gap
        return seconds
    
    def get_lines(self):
        lines = []
        current_line = []
        
        for note in self.notes:
            if note['type'] == 'break':
                if current_line:
                    lines.append(current_line)
                    current_line = []
            elif note['type'] == 'note' and note['text']:
                current_line.append(note)
        
        if current_line:
            lines.append(current_line)
        
        return lines

# ==================== RENDERIZADOR COM ROLAGEM ====================

class ScrollingTextRenderer:
    def __init__(self, width=1920, height=1080, project_root="."):
        self.width = width
        self.height = height
        self.project_root = project_root
        self.fonts = self.load_custom_fonts()
        self.frame_cache = {}
        
    def load_custom_fonts(self):
        """Carrega fontes personalizadas"""
        font_files = get_custom_fonts(self.project_root)
        fonts = {}
        
        print("🔤 Carregando fontes personalizadas...")
        
        sizes = {
            'title': 120,
            'artist': 70,
            'main': 85,      # Linha atual (destaque)
            'previous': 68,  # Linha anterior (cinza acima)
            'preview': 68    # Próxima linha (cinza abaixo)
        }
        
        font_mapping = {
            'title': 'playfair_bold',
            'artist': 'lato_light',
            'main': 'poppins_bold',
            'previous': 'poppins_regular',
            'preview': 'poppins_regular'
        }
        
        for size_name, size in sizes.items():
            fonts[size_name] = None
            preferred_font = font_mapping[size_name]
            
            try:
                if preferred_font in font_files:
                    fonts[size_name] = ImageFont.truetype(font_files[preferred_font], size)
                    font_display_name = os.path.basename(font_files[preferred_font]).replace('.ttf', '')
                    print(f"   ✅ {size_name}: {font_display_name} ({size}px)")
                else:
                    print(f"   ⚠️  {size_name}: {preferred_font} não encontrada, usando fallback")
                    
                    system_fonts = []
                    if platform.system().lower() == 'windows':
                        if size_name == 'title':
                            system_fonts = [r"C:\Windows\Fonts\georgia.ttf", r"C:\Windows\Fonts\times.ttf"]
                        elif size_name == 'artist':
                            system_fonts = [r"C:\Windows\Fonts\segoeui.ttf", r"C:\Windows\Fonts\calibri.ttf"]
                        elif size_name == 'main':
                            system_fonts = [r"C:\Windows\Fonts\arialbd.ttf", r"C:\Windows\Fonts\verdanab.ttf"]
                        else:
                            system_fonts = [r"C:\Windows\Fonts\arial.ttf", r"C:\Windows\Fonts\calibri.ttf"]
                    
                    font_loaded = False
                    for sys_font in system_fonts:
                        if os.path.exists(sys_font):
                            try:
                                fonts[size_name] = ImageFont.truetype(sys_font, size)
                                print(f"   ✅ {size_name}: {os.path.basename(sys_font)} ({size}px)")
                                font_loaded = True
                                break
                            except:
                                continue
                    
                    if not font_loaded:
                        fonts[size_name] = ImageFont.load_default()
                        print(f"   ⚠️  {size_name}: Fonte padrão (fallback)")
                        
            except Exception as e:
                print(f"   ❌ Erro ao carregar {size_name}: {str(e)[:50]}...")
                fonts[size_name] = ImageFont.load_default()
        
        return fonts
    
    def wrap_text(self, text, font, max_width):
        """Quebra texto inteligente"""
        words = text.split()
        lines = []
        current_line = []
        
        temp_img = Image.new('RGBA', (1, 1))
        temp_draw = ImageDraw.Draw(temp_img)
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            try:
                bbox = temp_draw.textbbox((0, 0), test_line, font=font)
                text_width = bbox[2] - bbox[0]
            except:
                text_width, _ = temp_draw.textsize(test_line, font=font)
            
            if text_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
                    current_line = []
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def create_text_enhanced(self, text, font_type='main', color=(255, 255, 255), 
                           stroke_width=4, stroke_color=(0, 0, 0), max_width=None):
        """Renderização com cache"""
        cache_key = f"{text}_{font_type}_{color}_{stroke_width}_{stroke_color}_{max_width}"
        
        if cache_key in self.frame_cache:
            return self.frame_cache[cache_key]
        
        font = self.fonts.get(font_type)
        if not font:
            return None
        
        if max_width is None:
            if font_type == 'title':
                max_width = self.width - 100
            elif font_type == 'artist':
                max_width = self.width - 200
            else:
                max_width = self.width - 100
        
        text_lines = self.wrap_text(text, font, max_width)
        
        if not text_lines:
            return None
        
        temp_img = Image.new('RGBA', (1, 1))
        temp_draw = ImageDraw.Draw(temp_img)
        
        line_heights = []
        line_widths = []
        
        for line in text_lines:
            try:
                bbox = temp_draw.textbbox((0, 0), line, font=font)
                line_width = bbox[2] - bbox[0]
                line_height = bbox[3] - bbox[1]
            except:
                line_width, line_height = temp_draw.textsize(line, font=font)
            
            line_widths.append(line_width)
            line_heights.append(line_height)
        
        margin_extra = 60
        total_width = max(line_widths) + (stroke_width * 2) + margin_extra
        total_height = sum(line_heights) + (len(text_lines) - 1) * 20 + (stroke_width * 2) + margin_extra
        
        img = Image.new('RGBA', (total_width, total_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        y_offset = stroke_width + (margin_extra // 2)
        
        for i, line in enumerate(text_lines):
            line_width = line_widths[i]
            line_height = line_heights[i]
            
            x = (total_width - line_width) // 2
            
            if stroke_width > 0:
                for dx in range(-stroke_width, stroke_width + 1, 2):
                    for dy in range(-stroke_width, stroke_width + 1, 2):
                        if dx*dx + dy*dy <= stroke_width*stroke_width:
                            draw.text((x + dx, y_offset + dy), line, font=font, fill=stroke_color)
            
            draw.text((x, y_offset), line, font=font, fill=color)
            y_offset += line_height + 20
        
        self.frame_cache[cache_key] = img
        
        return img
    
    def create_background_with_effects(self, background_image=None):
        """Cria fundo com efeitos"""
        print("📸 Processando fundo com efeitos visuais...")
        
        project_root = Path(self.project_root) if isinstance(self.project_root, str) else self.project_root
        
        final_background_path = None
        
        if background_image:
            background_path = Path(background_image)
            
            if not background_path.is_absolute() and len(background_path.parts) == 1:
                possible_paths = [
                    project_root / background_path,
                    project_root / "assets" / "background" / background_path,
                    project_root / "assets" / "background" / "__artist" / background_path
                ]
                for path in possible_paths:
                    if path.exists():
                        final_background_path = str(path)
                        print(f"   🔍 Background encontrado em: {path}")
                        break
                
                if not final_background_path:
                    print(f"   ❌ Background não encontrado: {background_path}")
            else:
                if background_path.exists():
                    final_background_path = str(background_path)
                else:
                    print(f"   ❌ Background não encontrado: {background_path}")
        else:
            default_path = project_root / "assets" / "background" / "bg.jpg"
            if default_path.exists():
                final_background_path = str(default_path)
                print(f"   🎯 Usando background padrão: {default_path}")
            else:
                print(f"   ⚠️  Background padrão: bg.jpg não encontrado em {default_path}")
        
        fundo_base = Image.new("RGB", (self.width, self.height), color=(0, 0, 0))
        draw_fundo_base = ImageDraw.Draw(fundo_base)

        if final_background_path and os.path.exists(final_background_path):
            try:
                img_fundo_artista = Image.open(final_background_path).convert("RGB")
                img_fundo_artista = img_fundo_artista.resize((self.width, self.height), Image.Resampling.LANCZOS)
                fundo_base = img_fundo_artista
                print(f"   ✅ Imagem de fundo carregada: {os.path.basename(final_background_path)}")
            except Exception as e:
                print(f"   ⚠️  Erro ao carregar imagem: {e}. Usando fundo gradiente.")
                cor_topo = (20, 20, 20)
                cor_base = (0, 0, 0)
                for y in range(self.height):
                    r = int(cor_topo[0] + (cor_base[0] - cor_topo[0]) * (y / self.height))
                    g = int(cor_topo[1] + (cor_base[1] - cor_topo[1]) * (y / self.height))
                    b = int(cor_topo[2] + (cor_base[2] - cor_topo[2]) * (y / self.height))
                    draw_fundo_base.line([(0, y), (self.width, y)], fill=(r, g, b))
        else:
            cor_topo = (20, 20, 20)
            cor_base = (0, 0, 0)
            for y in range(self.height):
                r = int(cor_topo[0] + (cor_base[0] - cor_topo[0]) * (y / self.height))
                g = int(cor_topo[1] + (cor_base[1] - cor_topo[1]) * (y / self.height))
                b = int(cor_topo[2] + (cor_base[2] - cor_topo[2]) * (y / self.height))
                draw_fundo_base.line([(0, y), (self.width, y)], fill=(r, g, b))
            print("   ✅ Fundo gradiente padrão criado")

        ondas_layer = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        draw_ondas = ImageDraw.Draw(ondas_layer)
        desenhar_ondas(draw_ondas, self.width, self.height, cor_onda=(50, 50, 50), num_ondas=4, intensidade=0.1)

        camada_preta = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 200))
        
        img = fundo_base.copy()
        img.paste(ondas_layer, (0, 0), ondas_layer)
        img.paste(camada_preta, (0, 0), camada_preta)

        print("   ✅ Efeitos visuais aplicados com rolagem de texto")
        
        return img

# ==================== GERADOR COM ROLAGEM ====================

class ScrollingKaraokeGenerator:
    def __init__(self, ultrastar_file, background_image=None, audio_file=None, use_gpu=True):
        script_dir = Path(__file__).parent
        project_root = script_dir.parent
        
        self.parser = UltraStarParser(ultrastar_file)
        self.background_image = background_image
        
        artist = self.parser.header.get('ARTIST', 'Artista_Desconhecido')
        title = self.parser.header.get('TITLE', 'Musica_Desconhecida')
        
        def sanitize_filename(name):
            invalid_chars = '<>:"/\\|?*'
            for char in invalid_chars:
                name = name.replace(char, '')
            name = ' '.join(name.split())
            return name.strip()
        
        artist_clean = sanitize_filename(artist)
        title_clean = sanitize_filename(title)
        
        output_dir = project_root / "Output"
        output_dir.mkdir(exist_ok=True)
        
        self.output_file = str(output_dir / f"{artist_clean} - {title_clean}.mp4")
        self.project_root = str(project_root)
        
        print(f"📁 Diretório do projeto: {self.project_root}")
        print(f"📁 Pasta de saída: {output_dir}")
        print(f"📝 Arquivo de saída: {self.output_file}")
        
        self.width = 1920
        self.height = 1080
        self.fps = 25
        
        self.ffmpeg_path, self.ffprobe_path = find_ffmpeg_tools()
        if not self.ffmpeg_path:
            raise FileNotFoundError("FFmpeg não encontrado")
        
        print(f"🔧 FFmpeg: {self.ffmpeg_path}")
        if self.ffprobe_path:
            print(f"🔧 FFprobe: {self.ffprobe_path}")
        
        if use_gpu:
            self.encoder, self.gpu_name, self.encoder_params = detect_gpu_optimized(self.ffmpeg_path)
        else:
            self.encoder, self.gpu_name = 'libx264', 'CPU'
            self.encoder_params = ['-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '28']
        
        self.text_renderer = ScrollingTextRenderer(self.width, self.height, self.project_root)
        
        if audio_file:
            self.audio_path = Path(audio_file)
            if not self.audio_path.is_absolute():
                self.audio_path = Path.cwd() / audio_file
            print(f"🎵 Usando áudio especificado: {self.audio_path}")
        else:
            audio_filename = self.parser.header.get('MP3', 'audio.mp3')
            txt_path = Path(ultrastar_file)
            self.audio_path = txt_path.parent / audio_filename
            print(f"🎵 Usando áudio do TXT: {self.audio_path}")
            
            if not self.audio_path.exists():
                project_root_path = Path(project_root)
                self.audio_path = project_root_path / audio_filename
                print(f"🎵 Áudio não encontrado na pasta do TXT, tentando: {self.audio_path}")
        
        if not self.audio_path.exists():
            raise FileNotFoundError(f"Arquivo de áudio não encontrado: {self.audio_path}")
        
        self.duration = self.get_audio_duration()
        
        # Posições para o efeito de rolagem (3 linhas visíveis)
        self.pos_previous = self.height // 2 - 220  # Linha anterior (acima)
        self.pos_main = self.height // 2 - 50       # Linha atual (centro - destaque)
        self.pos_preview = self.height // 2 + 150   # Próxima linha (abaixo)
        
        self.process = None
        self.encoding_finished = False
    
    def get_audio_duration(self):
        """Duração do áudio"""
        if not self.ffprobe_path:
            print("   ⚠️  FFprobe não disponível - usando duração padrão")
            return 180.0
        
        try:
            print("🎵 Analisando áudio...")
            result = subprocess.run([
                self.ffprobe_path, '-v', 'quiet', '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1', str(self.audio_path)
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and result.stdout.strip():
                duration = float(result.stdout.strip())
                print(f"   ✅ Duração detectada: {duration:.1f}s")
                return duration
            else:
                print("   ⚠️  Usando duração padrão")
                return 180.0
                
        except Exception as e:
            print(f"   ⚠️  Erro: {str(e)[:30]}... Usando duração padrão")
            return 180.0
    
    def calculate_scroll_moments(self, lines):
        """Calcula momentos com suporte para 3 linhas (anterior, atual, próxima)"""
        scroll_moments = []
        
        # Frame inicial (título + artista)
        scroll_moments.append({
            'start_time': 0,
            'end_time': 4,
            'type': 'title',
            'title': self.parser.header.get('TITLE', 'Música'),
            'artist': self.parser.header.get('ARTIST', 'Artista'),
            'transition_progress': 1.0
        })
        
        # Processar cada linha com contexto (anterior, atual, próxima)
        for i, line_notes in enumerate(lines):
            if not line_notes:
                continue
            
            line_start = self.parser.beat_to_seconds(line_notes[0]['beat'])
            line_end = self.parser.beat_to_seconds(line_notes[-1]['beat'] + line_notes[-1]['duration'])
            
            # Linha anterior
            previous_line = None
            if i > 0:
                prev_notes = lines[i - 1]
                if prev_notes:
                    previous_line = ' '.join([note['text'] for note in prev_notes]).strip()
            
            # Linha atual
            current_line = ' '.join([note['text'] for note in line_notes]).strip()
            
            # Próxima linha
            next_line = None
            next_line_start = None
            if i + 1 < len(lines):
                next_notes = lines[i + 1]
                if next_notes:
                    next_line = ' '.join([note['text'] for note in next_notes]).strip()
                    next_line_start = self.parser.beat_to_seconds(next_notes[0]['beat'])
            
            # Calcular fim do momento
            if next_line_start is not None:
                moment_end = next_line_start
            else:
                moment_end = line_end + 0.5
            
            # CORREÇÃO: Iniciar transição ANTES para terminar no tempo certo
            # A transição de rolagem precisa terminar quando o áudio começa
            transition_duration = 0.5  # 500ms para rolagem suave
            transition_start = max(4, line_start - transition_duration)  # Começar ANTES
            
            scroll_moments.append({
                'start_time': transition_start,
                'end_time': moment_end,
                'type': 'lyrics',
                'previous_line': previous_line,
                'current_line': current_line,
                'next_line': next_line,
                'transition_duration': transition_duration,
                'line_actual_start': line_start  # Momento real da linha
            })
        
        # Frame final (sem texto)
        if scroll_moments:
            last_end = scroll_moments[-1]['end_time']
            if last_end < self.duration:
                scroll_moments.append({
                    'start_time': last_end,
                    'end_time': self.duration,
                    'type': 'empty',
                    'transition_progress': 1.0
                })
        
        return scroll_moments
    
    def apply_fade_transition(self, img, alpha_value):
        """Aplica fade-in/fade-out em uma imagem"""
        if img is None:
            return None
        
        # Criar cópia com alpha ajustado
        img_copy = img.copy()
        
        # Ajustar transparência
        alpha = img_copy.split()[3] if img_copy.mode == 'RGBA' else None
        if alpha:
            alpha = alpha.point(lambda p: int(p * alpha_value))
            img_copy.putalpha(alpha)
        
        return img_copy
    
    def create_scrolling_frame(self, moment, background_frame, timestamp):
        """Cria frame com efeito de rolagem INVERTIDO (de baixo para cima)"""
        frame = background_frame.copy()
        
        if moment['type'] == 'title':
            # Título e artista (sem mudanças)
            title_img = self.text_renderer.create_text_enhanced(
                moment['title'], 'title', color=(255, 255, 255), stroke_width=5
            )
            if title_img:
                x = (self.width - title_img.width) // 2
                y = max(50, min(self.height // 2 - 120, self.height - title_img.height - 100))
                frame.paste(title_img, (x, y), title_img)
            
            artist_img = self.text_renderer.create_text_enhanced(
                moment['artist'], 'artist', color=(200, 200, 200), stroke_width=4
            )
            if artist_img:
                x = (self.width - artist_img.width) // 2
                y = max(150, min(self.height // 2 - 120 + (title_img.height if title_img else 0) + 30, 
                               self.height - artist_img.height - 50))
                frame.paste(artist_img, (x, y), artist_img)
        
        elif moment['type'] == 'lyrics':
            # CORREÇÃO: Calcular progresso baseado no início REAL da transição
            transition_duration = moment.get('transition_duration', 0.5)
            line_actual_start = moment.get('line_actual_start', moment['start_time'])
            
            # Progresso: 0 = início da transição (tudo embaixo), 1 = linha no topo (pronta para cantar)
            time_in_transition = timestamp - moment['start_time']
            transition_progress = min(1.0, time_in_transition / transition_duration)
            
            # IMPORTANTE: Quando transition_progress = 1.0, a linha está em posição final
            # e pronta para ser cantada no tempo exato do áudio
            
            # EFEITO DE ROLAGEM SUAVE: As linhas sobem gradualmente
            # No início (progress=0): scroll_offset = 200 (tudo mais embaixo)
            # No fim (progress=1): scroll_offset = 0 (posições finais)
            # Usando função de easing suave (ease-out) para movimento mais natural
            ease_progress = 1 - math.pow(1 - transition_progress, 3)  # Cubic ease-out
            scroll_offset = int((1 - ease_progress) * 200)  # Sobe suavemente 200px
            
            # PRÉ-RENDERIZAR todas as imagens para calcular alturas
            previous_img = None
            main_img = None
            preview_img = None
            
            if moment['previous_line']:
                previous_img = self.text_renderer.create_text_enhanced(
                    moment['previous_line'], 'previous', 
                    color=(140, 140, 140), stroke_width=3
                )
            
            if moment['current_line']:
                main_img = self.text_renderer.create_text_enhanced(
                    moment['current_line'], 'main', 
                    color=(255, 255, 255), stroke_width=5
                )
            
            if moment['next_line']:
                preview_img = self.text_renderer.create_text_enhanced(
                    moment['next_line'], 'preview', 
                    color=(120, 120, 120), stroke_width=3
                )
            
            # CALCULAR POSIÇÕES COM ESPAÇAMENTO DINÂMICO
            # Altura da linha principal (pode ocupar múltiplas linhas)
            main_height = main_img.height if main_img else 0
            
            # LINHA ANTERIOR (acima, cinza claro, fade-out progressivo)
            if previous_img:
                # Fade-out suave e progressivo quando nova linha entra
                alpha_previous = max(0.3, 1.0 - (transition_progress * 0.7))
                previous_img = self.apply_fade_transition(previous_img, alpha_previous)
                
                x = (self.width - previous_img.width) // 2
                y = self.pos_previous + scroll_offset  # Sobe suavemente
                y = max(50, min(y, self.height - previous_img.height - 50))
                frame.paste(previous_img, (x, y), previous_img)
            
            # LINHA ATUAL (centro, branca, destaque MÁXIMO com fade-in suave)
            if main_img:
                # Fade-in suave e gradual
                alpha_main = min(1.0, transition_progress * 1.5)
                main_img = self.apply_fade_transition(main_img, alpha_main)
                
                x = (self.width - main_img.width) // 2
                y = self.pos_main + scroll_offset  # Sobe suavemente
                y = max(150, min(y, self.height - main_img.height - 150))
                frame.paste(main_img, (x, y), main_img)
            
            # PRÓXIMA LINHA (abaixo, cinza escuro, preview com fade-in)
            if preview_img:
                # Fade-in muito suave e progressivo
                alpha_preview = min(0.8, transition_progress * 0.8)
                preview_img = self.apply_fade_transition(preview_img, alpha_preview)
                
                x = (self.width - preview_img.width) // 2
                
                # POSIÇÃO DINÂMICA: Abaixo da linha principal + margem extra
                y_base = self.pos_main + main_height + 60  # 60px de margem extra
                y = y_base + scroll_offset  # Sobe suavemente
                
                # Garantir que não saia da tela
                y = max(y_base, min(y, self.height - preview_img.height - 50))
                frame.paste(preview_img, (x, y), preview_img)
        
        return frame
    
    def monitor_ffmpeg_optimized(self, process):
        """Monitor otimizado"""
        def monitor():
            try:
                process.wait(timeout=600)
                self.encoding_finished = True
            except subprocess.TimeoutExpired:
                print(f"\n⏰ Timeout do FFmpeg - finalizando...")
                try:
                    process.terminate()
                    process.wait(timeout=15)
                except:
                    process.kill()
                self.encoding_finished = True
        
        monitor_thread = threading.Thread(target=monitor)
        monitor_thread.daemon = True
        monitor_thread.start()
        return monitor_thread
    
    def generate_video_with_scroll(self):
        """Geração com efeito de rolagem"""
        print(f"🚀 Gerador de Karaokê com Efeito de Rolagem - SINCRONIZADO")
        print(f"   📺 Resolução: {self.width}x{self.height} @ {self.fps}fps")
        print(f"   🎵 Música: {self.parser.header.get('TITLE', 'Desconhecida')}")
        print(f"   🎤 Artista: {self.parser.header.get('ARTIST', 'Desconhecido')}")
        print(f"   ⏱️  Duração: {self.duration:.1f}s")
        print(f"   🎮 Encoder: {self.gpu_name} ({self.encoder})")
        print(f"   🎬 Efeitos: Rolagem Suave + Easing (500ms)")
        print(f"   🌊 Animação: Cubic ease-out para movimento natural")
        
        lines = self.parser.get_lines()
        print(f"   📝 Linhas: {len(lines)}")
        
        # Calcular momentos com rolagem
        scroll_moments = self.calculate_scroll_moments(lines)
        print(f"   🎯 Momentos de rolagem: {len(scroll_moments)}")
        print(f"   ⚡ Sincronização: Transição inicia 500ms ANTES do áudio")
        print(f"   📈 Movimento: 200px de rolagem com aceleração suave")
        
        # Fundo com efeitos
        background_frame = self.text_renderer.create_background_with_effects(self.background_image)
        
        total_frames = int(self.duration * self.fps)
        print(f"   🎬 Total de frames: {total_frames}")
        
        # Comando FFmpeg
        print(f"\n🎬 Preparando encoding com transições antecipadas...")
        
        base_cmd = [
            self.ffmpeg_path, '-y', 
            '-f', 'rawvideo', '-vcodec', 'rawvideo',
            '-s', f'{self.width}x{self.height}', '-pix_fmt', 'rgb24', '-r', str(self.fps),
            '-i', '-', 
            '-i', str(self.audio_path)
        ]
        
        video_cmd = base_cmd + self.encoder_params + [
            '-c:a', 'copy',
            '-pix_fmt', 'yuv420p', 
            '-movflags', '+faststart',
            '-avoid_negative_ts', 'make_zero',
            self.output_file
        ]
        
        try:
            print(f"🚀 Iniciando encoding com {self.gpu_name}...")
            self.process = subprocess.Popen(video_cmd, stdin=subprocess.PIPE, 
                                          stderr=subprocess.PIPE, stdout=subprocess.PIPE,
                                          bufsize=2*1024*1024)
            
            monitor_thread = self.monitor_ffmpeg_optimized(self.process)
            
            print(f"📡 Gerando frames com rolagem sincronizada...")
            self.start_time = time.time()
            
            # Gerar e enviar frames em tempo real
            for frame_num in range(total_frames):
                timestamp = frame_num / self.fps
                
                # Encontrar momento atual
                current_moment = None
                for moment in scroll_moments:
                    if moment['start_time'] <= timestamp < moment['end_time']:
                        current_moment = moment
                        break
                
                # Se não encontrou, usar o último
                if current_moment is None and scroll_moments:
                    current_moment = scroll_moments[-1]
                
                # Gerar frame com rolagem
                if current_moment:
                    frame = self.create_scrolling_frame(current_moment, background_frame, timestamp)
                    frame_data = np.array(frame)
                    
                    try:
                        self.process.stdin.write(frame_data.tobytes())
                        if frame_num % 100 == 0:
                            self.process.stdin.flush()
                    except (BrokenPipeError, OSError):
                        print(f"\n💥 Conexão perdida no frame {frame_num}")
                        break
                
                # Progresso
                if frame_num % 50 == 0 or frame_num == total_frames - 1:
                    percentage = (frame_num / total_frames) * 100
                    elapsed = time.time() - self.start_time
                    fps_current = frame_num / elapsed if elapsed > 0 else 0
                    eta_seconds = (total_frames - frame_num) / fps_current if fps_current > 0 else 0
                    print(f"\rRolagem: {percentage:.1f}% | {fps_current:.1f}fps | ETA: {int(eta_seconds//60):02d}:{int(eta_seconds%60):02d}", end='', flush=True)
            
            print(f"\n📤 Finalizando...")
            
            try:
                self.process.stdin.close()
            except:
                pass
            
            # Aguardar finalização
            timeout_count = 0
            while not self.encoding_finished and timeout_count < 30:
                time.sleep(1)
                timeout_count += 1
                if timeout_count % 10 == 0:
                    print(f"   ⏳ Finalizando... ({timeout_count}s)")
            
            elapsed = time.time() - self.start_time
            
            if os.path.exists(self.output_file):
                file_size = os.path.getsize(self.output_file) / (1024*1024)
                print(f"\n✅ Vídeo com Rolagem Suave e Sincronizada gerado com sucesso!")
                print(f"   📁 Arquivo: {self.output_file}")
                print(f"   📏 Tamanho: {file_size:.1f} MB")
                print(f"   ⏱️  Tempo total: {elapsed:.1f}s")
                print(f"   🚀 Velocidade média: {total_frames/elapsed:.1f} fps")
                print(f"   🎨 Efeitos aplicados:")
                print(f"      - Rolagem suave com cubic ease-out")
                print(f"      - Transição antecipada (500ms ANTES)")
                print(f"      - Sincronização perfeita com áudio")
                print(f"      - 200px de deslocamento vertical")
                print(f"      - Fade progressivo em 3 linhas")
                print(f"      - Linha anterior (cinza, fade-out)")
                print(f"      - Linha atual (branco, fade-in)")
                print(f"      - Próxima linha (cinza escuro, preview)")
            else:
                print(f"\n❌ Arquivo não foi criado!")
                
        except Exception as e:
            print(f"\n❌ Erro: {e}")
            if self.process:
                try:
                    self.process.terminate()
                except:
                    pass
            raise

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Gerador de Karaokê com Efeito de Rolagem Sincronizado')
    parser.add_argument('input', help='Arquivo UltraStar TXT')
    parser.add_argument('--background', '-bg', help='Imagem de fundo')
    parser.add_argument('--audio', '-a', help='Arquivo de áudio')
    parser.add_argument('--no-gpu', action='store_true', help='Usar CPU')
    
    args = parser.parse_args()
    
    # Resolver caminho do arquivo de input
    input_path = Path(args.input)
    
    if not input_path.is_absolute() and len(input_path.parts) == 1:
        project_root = Path(__file__).parent.parent
        input_path = project_root / input_path
    
    if not input_path.exists():
        print(f"❌ Arquivo não encontrado: {input_path}")
        sys.exit(1)
    
    # Verificar áudio
    if args.audio:
        audio_path = Path(args.audio)
        if not audio_path.is_absolute() and len(audio_path.parts) == 1:
            project_root = Path(__file__).parent.parent
            audio_path = project_root / audio_path
        if not audio_path.exists():
            print(f"❌ Arquivo de áudio não encontrado: {audio_path}")
            sys.exit(1)
        args.audio = str(audio_path)
    
    try:
        generator = ScrollingKaraokeGenerator(
            str(input_path),
            background_image=args.background,
            audio_file=args.audio,
            use_gpu=not args.no_gpu
        )
        generator.generate_video_with_scroll()
        
    except KeyboardInterrupt:
        print(f"\n🛑 Interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()