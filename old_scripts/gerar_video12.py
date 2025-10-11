#!/usr/bin/env python3
"""
Gerador de Vídeo Karaokê ULTRA RÁPIDO - Com Fontes Bonitas
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
    fonts_dir = os.path.join(project_root, "fonts")
    
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
    
    # Verificar se a pasta fonts existe
    if not os.path.exists(fonts_dir):
        print(f"   ⚠️  Pasta fonts não existe: {fonts_dir}")
        print(f"   💡 Crie a pasta 'fonts' no diretório do projeto")
        print(f"   💡 Baixe as fontes recomendadas:")
        print(f"      - PlayfairDisplay-Bold.ttf (Google Fonts)")
        print(f"      - Lato-Light.ttf (Google Fonts)")
        print(f"      - Poppins-Bold.ttf (Google Fonts)")
        print(f"      - Poppins-Regular.ttf (Google Fonts)")
    
    # Listar arquivos na pasta fonts se existir
    if os.path.exists(fonts_dir):
        print(f"   📁 Arquivos na pasta fonts:")
        for arquivo in os.listdir(fonts_dir):
            print(f"      - {arquivo}")
    
    # Fallbacks do sistema se necessário
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
            print("   📝 Fallback: Georgia, Segoe UI, Arial Bold e Arial")
    
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
        # Menos pontos para velocidade (a cada 4 pixels)
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

# ==================== RENDERIZADOR ULTRA RÁPIDO ====================

class UltraFastTextRenderer:
    def __init__(self, width=1920, height=1080, project_root="."):
        self.width = width
        self.height = height
        self.project_root = project_root
        self.fonts = self.load_custom_fonts()
        
        # Cache para frames gerados
        self.frame_cache = {}
        
    def load_custom_fonts(self):
        """Carrega fontes personalizadas com verificação detalhada"""
        font_files = get_custom_fonts(self.project_root)
        fonts = {}
        
        print("🔤 Carregando fontes personalizadas...")
        
        sizes = {
            'title': 95,      # Playfair Display - Elegante para título
            'artist': 50,     # Lato Light - Leve e moderna para artista
            'main': 85,       # Poppins Bold - Forte e legível para letra atual
            'preview': 68     # Poppins Regular - Suave para próxima linha
        }
        
        # Mapeamento de fontes para cada tamanho
        font_mapping = {
            'title': 'playfair_bold',
            'artist': 'lato_light',
            'main': 'poppins_bold',
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
                    # Fallback para fonte do sistema
                    print(f"   ⚠️  {size_name}: {preferred_font} não encontrada, usando fallback")
                    
                    # Tentar fontes do sistema
                    system_fonts = []
                    if platform.system().lower() == 'windows':
                        if size_name == 'title':
                            system_fonts = [r"C:\Windows\Fonts\georgia.ttf", r"C:\Windows\Fonts\times.ttf"]
                        elif size_name == 'artist':
                            system_fonts = [r"C:\Windows\Fonts\segoeui.ttf", r"C:\Windows\Fonts\calibri.ttf"]
                        elif size_name == 'main':
                            system_fonts = [r"C:\Windows\Fonts\arialbd.ttf", r"C:\Windows\Fonts\verdanab.ttf"]
                        else:  # preview
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
        
        print("   💡 Fontes recomendadas disponíveis no Google Fonts:")
        print("      https://fonts.google.com/specimen/Playfair+Display")
        print("      https://fonts.google.com/specimen/Lato")
        print("      https://fonts.google.com/specimen/Poppins")
        
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
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def create_text_enhanced(self, text, font_type='main', color=(255, 255, 255), 
                           stroke_width=4, stroke_color=(0, 0, 0), max_width=None):
        """Renderização com cache e posicionamento corrigido"""
        
        # Criar chave de cache
        cache_key = f"{text}_{font_type}_{color}_{stroke_width}_{stroke_color}_{max_width}"
        
        if cache_key in self.frame_cache:
            return self.frame_cache[cache_key]
        
        font = self.fonts.get(font_type)
        if not font:
            return None
        
        if max_width is None:
            if font_type == 'title':
                max_width = self.width - 200
            elif font_type == 'artist':
                max_width = self.width - 300
            else:
                max_width = self.width - 150  # Margem maior para evitar corte
        
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
        
        # Dimensões com margem extra para evitar corte
        margin_extra = 40  # Margem extra para evitar corte
        total_width = max(line_widths) + (stroke_width * 2) + margin_extra
        total_height = sum(line_heights) + (len(text_lines) - 1) * 15 + (stroke_width * 2) + margin_extra
        
        img = Image.new('RGBA', (total_width, total_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        y_offset = stroke_width + (margin_extra // 2)
        
        for i, line in enumerate(text_lines):
            line_width = line_widths[i]
            line_height = line_heights[i]
            
            x = (total_width - line_width) // 2
            
            # Contorno otimizado
            if stroke_width > 0:
                for dx in range(-stroke_width, stroke_width + 1, 2):
                    for dy in range(-stroke_width, stroke_width + 1, 2):
                        if dx*dx + dy*dy <= stroke_width*stroke_width:
                            draw.text((x + dx, y_offset + dy), line, font=font, fill=stroke_color)
            
            draw.text((x, y_offset), line, font=font, fill=color)
            y_offset += line_height + 15  # Espaçamento maior entre linhas
        
        # Armazenar no cache
        self.frame_cache[cache_key] = img
        
        return img
    
    def create_background_with_effects(self, background_image=None):
        """Cria fundo com efeitos igual ao script de exemplo"""
        print("📸 Processando fundo com efeitos visuais...")
        
        # Criar fundo base (igual ao script de exemplo)
        fundo_base = Image.new("RGB", (self.width, self.height), color=(0, 0, 0))
        draw_fundo_base = ImageDraw.Draw(fundo_base)

        if background_image and os.path.exists(background_image):
            try:
                # Carregar imagem de fundo (igual ao script de exemplo)
                img_fundo_artista = Image.open(background_image).convert("RGB")
                img_fundo_artista = img_fundo_artista.resize((self.width, self.height), Image.Resampling.LANCZOS)
                # Converter para escala de cinza (igual ao script de exemplo)
                img_fundo_artista = img_fundo_artista.convert("L").convert("RGB") 
                fundo_base = img_fundo_artista
                print("   ✅ Imagem de fundo carregada e convertida para escala de cinza")
                
            except Exception as e:
                print(f"   ⚠️  Erro ao carregar imagem: {e}. Usando fundo gradiente.")
                # Fundo gradiente padrão (igual ao script de exemplo)
                cor_topo = (20, 20, 20)
                cor_base = (0, 0, 0)
                for y in range(self.height):
                    r = int(cor_topo[0] + (cor_base[0] - cor_topo[0]) * (y / self.height))
                    g = int(cor_topo[1] + (cor_base[1] - cor_topo[1]) * (y / self.height))
                    b = int(cor_topo[2] + (cor_base[2] - cor_topo[2]) * (y / self.height))
                    draw_fundo_base.line([(0, y), (self.width, y)], fill=(r, g, b))
        else:
            # Fundo gradiente padrão (igual ao script de exemplo)
            cor_topo = (20, 20, 20)
            cor_base = (0, 0, 0)
            for y in range(self.height):
                r = int(cor_topo[0] + (cor_base[0] - cor_topo[0]) * (y / self.height))
                g = int(cor_topo[1] + (cor_base[1] - cor_topo[1]) * (y / self.height))
                b = int(cor_topo[2] + (cor_base[2] - cor_topo[2]) * (y / self.height))
                draw_fundo_base.line([(0, y), (self.width, y)], fill=(r, g, b))
            print("   ✅ Fundo gradiente padrão criado")

        # Camada de ondas (igual ao script de exemplo)
        ondas_layer = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        draw_ondas = ImageDraw.Draw(ondas_layer)
        desenhar_ondas(draw_ondas, self.width, self.height, cor_onda=(50, 50, 50), num_ondas=4, intensidade=0.1)

        # Camada de legibilidade (igual ao script de exemplo)
        camada_legibilidade = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 180))
        
        # Combinar todas as camadas (igual ao script de exemplo)
        img = fundo_base.copy()
        img.paste(ondas_layer, (0, 0), ondas_layer)
        img.paste(camada_legibilidade, (0, 0), camada_legibilidade)

        print("   ✅ Efeitos visuais aplicados:")
        print("      - Imagem em escala de cinza")
        print("      - Ondas translúcidas (4 ondas, intensidade 0.1)")
        print("      - Camada de legibilidade preta (alpha 180)")
        
        return img

# ==================== GERADOR ULTRA RÁPIDO ====================

class UltraFastKaraokeGenerator:
    def __init__(self, ultrastar_file, background_image=None, output_file='karaoke_ultra_fast.mp4', use_gpu=True):
        self.parser = UltraStarParser(ultrastar_file)
        self.output_file = output_file
        self.background_image = background_image
        
        self.project_root = str(Path(ultrastar_file).parent)
        print(f"📁 Diretório do projeto: {self.project_root}")
        
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
        
        self.text_renderer = UltraFastTextRenderer(self.width, self.height, self.project_root)
        
        audio_filename = self.parser.header.get('MP3', 'audio.mp3')
        self.audio_path = Path(ultrastar_file).parent / audio_filename
        
        if not self.audio_path.exists():
            raise FileNotFoundError(f"Arquivo de áudio não encontrado: {self.audio_path}")
        
        self.duration = self.get_audio_duration()
        
        # Posições corrigidas para evitar corte
        self.pos_title = self.height // 2 - 120  # Mais para cima
        self.pos_main = self.height // 2 - 50    # Mais para cima
        self.pos_preview = self.height // 2 + 40 # Mais para cima
        
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
    
    def calculate_unique_frames(self, lines):
        """Calcula os momentos únicos que precisam de frames diferentes"""
        unique_moments = []
        
        # Frame inicial (título + artista)
        unique_moments.append({
            'start_time': 0,
            'end_time': 4,
            'type': 'title',
            'title': self.parser.header.get('TITLE', 'Música'),
            'artist': self.parser.header.get('ARTIST', 'Artista')
        })
        
        # Frames para cada mudança de linha
        for i, line_notes in enumerate(lines):
            if not line_notes:
                continue
                
            line_start = self.parser.beat_to_seconds(line_notes[0]['beat'])
            line_end = self.parser.beat_to_seconds(line_notes[-1]['beat'] + line_notes[-1]['duration'])
            
            current_line = ' '.join([note['text'] for note in line_notes]).strip()
            next_line = None
            
            if i + 1 < len(lines):
                next_line_notes = lines[i + 1]
                if next_line_notes:
                    next_line = ' '.join([note['text'] for note in next_line_notes]).strip()
            
            unique_moments.append({
                'start_time': max(4, line_start),
                'end_time': line_end + 2,
                'type': 'lyrics',
                'current_line': current_line,
                'next_line': next_line
            })
        
        # Frame final (sem texto)
        if unique_moments:
            last_end = unique_moments[-1]['end_time']
            if last_end < self.duration:
                unique_moments.append({
                    'start_time': last_end,
                    'end_time': self.duration,
                    'type': 'empty'
                })
        
        return unique_moments
    
    def create_unique_frame(self, moment, background_frame):
        """Cria um frame único baseado no momento com posicionamento corrigido"""
        frame = background_frame.copy()
        
        if moment['type'] == 'title':
            # Título e artista
            title_img = self.text_renderer.create_text_enhanced(
                moment['title'], 'title', color=(255, 255, 255), stroke_width=5
            )
            if title_img:
                x = (self.width - title_img.width) // 2
                # Garantir que não saia da tela
                y = max(50, min(self.pos_title, self.height - title_img.height - 100))
                frame.paste(title_img, (x, y), title_img)
            
            artist_img = self.text_renderer.create_text_enhanced(
                moment['artist'], 'artist', color=(200, 200, 200), stroke_width=4
            )
            if artist_img:
                x = (self.width - artist_img.width) // 2
                y = max(150, min(self.pos_title + (title_img.height if title_img else 0) + 30, 
                               self.height - artist_img.height - 50))
                frame.paste(artist_img, (x, y), artist_img)
        
        elif moment['type'] == 'lyrics':
            # Linha atual
            if moment['current_line']:
                main_img = self.text_renderer.create_text_enhanced(
                    moment['current_line'], 'main', color=(255, 255, 255), stroke_width=5
                )
                if main_img:
                    x = (self.width - main_img.width) // 2
                    # Garantir que não saia da tela
                    y = max(200, min(self.pos_main, self.height - main_img.height - 150))
                    frame.paste(main_img, (x, y), main_img)
            
            # Próxima linha
            if moment['next_line']:
                preview_img = self.text_renderer.create_text_enhanced(
                    moment['next_line'], 'preview', color=(170, 170, 170), stroke_width=3
                )
                if preview_img:
                    x = (self.width - preview_img.width) // 2
                    y = self.pos_preview
                    
                    # Ajustar posição baseada na linha atual
                    if moment['current_line']:
                        main_img = self.text_renderer.create_text_enhanced(
                            moment['current_line'], 'main', color=(255, 255, 255), stroke_width=5
                        )
                        if main_img:
                            y = max(400, min(self.pos_main + main_img.height + 40, 
                                           self.height - preview_img.height - 50))
                    
                    # Garantir que não saia da tela
                    y = max(400, min(y, self.height - preview_img.height - 50))
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
    
    def generate_video_ultra_fast(self):
        """Geração ultra rápida com frames únicos"""
        print(f"🚀 Gerador de Karaokê ULTRA RÁPIDO - Com Fontes Bonitas")
        print(f"   📺 Resolução: {self.width}x{self.height} @ {self.fps}fps")
        print(f"   🎵 Música: {self.parser.header.get('TITLE', 'Desconhecida')}")
        print(f"   🎤 Artista: {self.parser.header.get('ARTIST', 'Desconhecido')}")
        print(f"   ⏱️  Duração: {self.duration:.1f}s")
        print(f"   🎮 Encoder: {self.gpu_name} ({self.encoder})")
        
        lines = self.parser.get_lines()
        print(f"   📝 Linhas: {len(lines)}")
        
        # Calcular momentos únicos
        unique_moments = self.calculate_unique_frames(lines)
        print(f"   🎯 Frames únicos: {len(unique_moments)} (vs {int(self.duration * self.fps)} total)")
        print(f"   ⚡ Otimização: {((int(self.duration * self.fps) - len(unique_moments)) / int(self.duration * self.fps) * 100):.1f}% menos frames")
        
        # Fundo com efeitos
        background_frame = self.text_renderer.create_background_with_effects(self.background_image)
        
        # Gerar frames únicos
        print(f"\n🎨 Gerando frames únicos...")
        unique_frames = {}
        
        for i, moment in enumerate(unique_moments):
            frame = self.create_unique_frame(moment, background_frame)
            unique_frames[i] = np.array(frame)
            print(f"\r   Frame {i+1}/{len(unique_moments)} gerado", end='', flush=True)
        
        print(f"\n   ✅ {len(unique_frames)} frames únicos gerados")
        
        total_frames = int(self.duration * self.fps)
        print(f"   🎬 Total de frames a enviar: {total_frames}")
        
        # Comando FFmpeg
        print(f"\n🎬 Preparando encoding...")
        
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
            print(f"🚀 Iniciando encoding ultra rápido com {self.gpu_name}...")
            self.process = subprocess.Popen(video_cmd, stdin=subprocess.PIPE, 
                                          stderr=subprocess.PIPE, stdout=subprocess.PIPE,
                                          bufsize=2*1024*1024)
            
            monitor_thread = self.monitor_ffmpeg_optimized(self.process)
            
            print(f"📡 Enviando frames otimizados...")
            self.start_time = time.time()
            
            # Enviar frames reutilizando os únicos
            for frame_num in range(total_frames):
                timestamp = frame_num / self.fps
                
                # Encontrar qual frame único usar
                current_frame_data = None
                for i, moment in enumerate(unique_moments):
                    if moment['start_time'] <= timestamp <= moment['end_time']:
                        current_frame_data = unique_frames[i]
                        break
                
                # Se não encontrou, usar o último frame disponível
                if current_frame_data is None and unique_frames:
                    current_frame_data = unique_frames[len(unique_frames) - 1]
                
                if current_frame_data is not None:
                    try:
                        self.process.stdin.write(current_frame_data.tobytes())
                        if frame_num % 100 == 0:
                            self.process.stdin.flush()
                    except (BrokenPipeError, OSError):
                        print(f"\n💥 Conexão perdida no frame {frame_num}")
                        break
                
                # Progresso otimizado
                if frame_num % 100 == 0 or frame_num == total_frames - 1:
                    percentage = (frame_num / total_frames) * 100
                    elapsed = time.time() - self.start_time
                    fps_current = frame_num / elapsed if elapsed > 0 else 0
                    eta_seconds = (total_frames - frame_num) / fps_current if fps_current > 0 else 0
                    print(f"\rEnviando: {percentage:.1f}% | {fps_current:.1f}fps | ETA: {int(eta_seconds//60):02d}:{int(eta_seconds%60):02d}", end='', flush=True)
            
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
                print(f"\n✅ Vídeo ULTRA RÁPIDO gerado com sucesso!")
                print(f"   📁 Arquivo: {self.output_file}")
                print(f"   📏 Tamanho: {file_size:.1f} MB")
                print(f"   ⏱️  Tempo total: {elapsed:.1f}s")
                print(f"   🚀 Velocidade média: {total_frames/elapsed:.1f} fps")
                print(f"   ⚡ Otimização: {len(unique_frames)} frames únicos reutilizados")
                print(f"   🎨 Efeitos: Escala de cinza + Ondas + Legibilidade")
                print(f"   🔤 Fontes: Playfair Display, Lato, Poppins")
                print(f"   📐 Posicionamento: Corrigido para evitar cortes")
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
    
    parser = argparse.ArgumentParser(description='Gerador de Karaokê ULTRA RÁPIDO - Com Fontes Bonitas')
    parser.add_argument('input', help='Arquivo UltraStar TXT')
    parser.add_argument('--background', '-bg', help='Imagem de fundo')
    parser.add_argument('--output', '-o', default='karaoke_ultra_fast.mp4', help='Arquivo de saída')
    parser.add_argument('--no-gpu', action='store_true', help='Usar CPU')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        print(f"❌ Arquivo não encontrado: {args.input}")
        sys.exit(1)
    
    try:
        generator = UltraFastKaraokeGenerator(
            args.input,
            background_image=args.background,
            output_file=args.output,
            use_gpu=not args.no_gpu
        )
        generator.generate_video_ultra_fast()
        
    except KeyboardInterrupt:
        print(f"\n🛑 Interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()