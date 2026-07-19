"""
MetaForge v3.1 - Professional Audio Metadata Editor
Author: DJ Denicore
Description: Advanced tool for editing audio metadata with cover art support
Features: ffprobe integration, Drag & Drop support
"""

import os
import re
import tkinter as tk
from tkinter import filedialog
import sys
import io
import base64
import subprocess
import json
from datetime import datetime

try:
    from mutagen import File
    from mutagen.id3 import ID3, TIT2, TPE1, TCON, TBPM, TRCK, TXXX, ID3NoHeaderError, APIC
    from mutagen.flac import FLAC, Picture
    from mutagen.oggvorbis import OggVorbis
    from mutagen.mp4 import MP4
except ImportError:
    print("Mutagen not installed. Install with: pip install mutagen")
    sys.exit(1)

try:
    from PIL import Image
except ImportError:
    print("Pillow not installed. Install with: pip install Pillow")
    sys.exit(1)

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich import box
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

console = Console()

# ================= SETTINGS =================
VERSION = "3.1"
APP_NAME = "MetaForge"

SUPPORTED_EXT = (".mp3", ".flac", ".ogg", ".wav", ".m4a", ".aac", ".opus")
COVER_EXT = (".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp")

# Файлы обложек, которые нужно игнорировать
IGNORE_COVER_NAMES = [
    "albumartsmall", "folder", "thumb", "thumbs", 
    "small", "preview", "proxy", "icon"
]

SETTINGS = {
    "write": True,
    "clean_underscores": True,
    "lang": "EN",
    "cover_size": (1200, 1200),
    "cover_quality": 100,
    "recursive": True,
    "force_cover": True,
    "ignore_small_covers": True,
    "upscale_small": True,
    "use_ffprobe": True  # Использовать ffprobe для чтения метаданных
}

CURRENT_FOLDER = None

# ================= LANGUAGES =================
TEXTS = {
    "EN": {
        "app_title": f"MetaForge v{VERSION}",
        "select_folder": "Select folder with audio files",
        "folder_not_selected": "Folder not selected.",
        "current_folder": "Folder",
        "artist_track": "Artist - Track",
        "tracknum_artist_track": "01 Artist - Track",
        "all_title": "Use filename as TITLE only",
        "rename_basic": "Artist - Track",
        "rename_tracknum": "01 Artist - Track",
        "toggle_dry_run": "Toggle Safe Mode (Dry-Run)",
        "change_folder": "Change Folder",
        "settings": "Settings",
        "exit": "Exit",
        "continue": "Continue?",
        "status_write_on": "[bold green]ON (Changes will be saved)[/bold green]",
        "status_write_off": "[bold red]OFF (Dry-Run mode, no changes)[/bold red]",
        "write_mode_lbl": "Write Mode",
        "replace_underscores": "Replace _ with space",
        "skip": "SKIP",
        "unsupported": "Unsupported format",
        "error_save": "Error saving",
        "done": "Done. Files processed",
        "press_enter": "Press Enter to return to menu...",
        "folder_required": "Please select a folder first (option 7)",
        "goodbye": "Goodbye!",
        "cover_added": "Cover added",
        "cover_found": "Cover found",
        "cover_not_found": "No cover found",
        "cover_skipped": "Already has cover",
        "cover_replaced": "Cover replaced",
        "cover_ignored": "Ignored small preview",
        "cover_upscaled": "Upscaled small cover",
        "back": "Back",
        "cover_size_lbl": "Cover max size",
        "cover_quality_lbl": "Cover quality",
        "add_covers": "Add covers to all files (recursive)",
        "cover_operation": "Cover operation completed",
        "recursive_mode": "Recursive mode",
        "process_subfolders": "Process subfolders",
        "force_cover": "Force replace cover",
        "ignore_small": "Ignore small covers (AlbumArtSmall)",
        "upscale_small": "Upscale small covers",
        "drag_drop_detected": "Drag & Drop detected",
        "use_ffprobe": "Use ffprobe for metadata",
        "ffprobe_not_found": "ffprobe not found, using mutagen fallback"
    },
    "RU": {
        "app_title": f"MetaForge v{VERSION}",
        "select_folder": "Выберите папку с треками",
        "folder_not_selected": "Папка не выбрана.",
        "current_folder": "Папка",
        "artist_track": "Автор - Трек",
        "tracknum_artist_track": "01 Автор - Трек",
        "all_title": "Всё имя файла → в TITLE",
        "rename_basic": "Автор - Трек",
        "rename_tracknum": "01 Автор - Трек",
        "toggle_dry_run": "Переключить Безопасный режим (Dry-Run)",
        "change_folder": "Сменить папку",
        "settings": "Настройки",
        "exit": "Выход",
        "continue": "Начать обработку?",
        "status_write_on": "[bold green]ВКЛЮЧЕНА (Изменения сохранятся)[/bold green]",
        "status_write_off": "[bold red]ВЫКЛЮЧЕНА (Dry-Run, только просмотр)[/bold red]",
        "write_mode_lbl": "Запись",
        "replace_underscores": "Заменять _ на пробел",
        "skip": "ПРОПУСК",
        "unsupported": "Неподдерживаемый формат",
        "error_save": "Ошибка при сохранении",
        "done": "Готово. Обработано файлов",
        "press_enter": "Нажмите Enter для возврата в меню...",
        "folder_required": "Пожалуйста, сначала выберите папку (пункт 7)",
        "goodbye": "До свидания!",
        "cover_added": "Обложка добавлена",
        "cover_found": "Обложка найдена",
        "cover_not_found": "Обложка не найдена",
        "cover_skipped": "Обложка уже есть",
        "cover_replaced": "Обложка заменена",
        "cover_ignored": "Игнорируем маленькую превью",
        "cover_upscaled": "Увеличена маленькая обложка",
        "back": "Назад",
        "cover_size_lbl": "Макс. размер обложки",
        "cover_quality_lbl": "Качество обложки",
        "add_covers": "Добавить обложки ко всем файлам (рекурсивно)",
        "cover_operation": "Операция с обложками завершена",
        "recursive_mode": "Рекурсивный режим",
        "process_subfolders": "Обрабатывать подпапки",
        "force_cover": "Принудительно заменить обложку",
        "ignore_small": "Игнорировать маленькие обложки",
        "upscale_small": "Увеличивать маленькие обложки",
        "drag_drop_detected": "Обнаружено перетаскивание",
        "use_ffprobe": "Использовать ffprobe для метаданных",
        "ffprobe_not_found": "ffprobe не найден, используется mutagen"
    }
}

def t(key):
    return TEXTS[SETTINGS["lang"]].get(key, key)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# ================= FFPROBE FUNCTIONS =================
def check_ffprobe():
    """Проверяет доступность ffprobe"""
    try:
        subprocess.run(['ffprobe', '-version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def get_audio_info_ffprobe(filepath: str) -> dict:
    """Получает информацию об аудиофайле через ffprobe"""
    info = {
        'artist': '',
        'title': '',
        'album': '',
        'track': '',
        'duration': 0,
        'bitrate': 0,
        'sample_rate': 0,
        'codec': '',
        'size': os.path.getsize(filepath),
        'path': filepath,
        'filename': os.path.basename(filepath),
    }
    
    try:
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            filepath
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        
        if result.returncode == 0 and result.stdout:
            data = json.loads(result.stdout)
            
            # Находим аудио поток
            audio_stream = None
            for stream in data.get('streams', []):
                if stream.get('codec_type') == 'audio':
                    audio_stream = stream
                    break
            
            if audio_stream:
                info['duration'] = float(audio_stream.get('duration', 0))
                info['bitrate'] = int(audio_stream.get('bit_rate', 0))
                info['sample_rate'] = int(audio_stream.get('sample_rate', 0))
                info['codec'] = audio_stream.get('codec_name', '')
            
            # Информация из формата
            if data.get('format'):
                fmt = data['format']
                info['duration'] = float(fmt.get('duration', info['duration']))
                info['bitrate'] = int(fmt.get('bit_rate', info['bitrate']))
                
                tags = fmt.get('tags', {})
                info['artist'] = tags.get('artist', '')
                info['title'] = tags.get('title', '')
                info['album'] = tags.get('album', '')
                info['track'] = tags.get('track', '')
    except Exception as e:
        if SETTINGS["lang"] == "RU":
            console.print(f"[yellow]Ошибка ffprobe: {e}[/yellow]")
        else:
            console.print(f"[yellow]ffprobe error: {e}[/yellow]")
    
    return info

# ================= COVER FUNCTIONS =================
def is_small_cover(filename):
    """Проверяет, является ли файл маленькой превьюшкой"""
    if not SETTINGS["ignore_small_covers"]:
        return False
    
    name_lower = filename.lower()
    
    for ignore in IGNORE_COVER_NAMES:
        if ignore in name_lower:
            return True
    
    return False

def find_cover_in_folder(folder_path):
    """Находит лучшую обложку в папке"""
    if not os.path.exists(folder_path):
        return None
    
    images = []
    small_images = []
    
    try:
        for f in os.listdir(folder_path):
            if f.lower().endswith(COVER_EXT):
                full_path = os.path.join(folder_path, f)
                if os.path.isfile(full_path):
                    if is_small_cover(f):
                        small_images.append((f, full_path))
                    else:
                        images.append((f, full_path))
    except:
        return None
    
    if images:
        for f, path in images:
            if f.startswith('00') or f.startswith('0_'):
                return path
        
        keywords = ["cover", "front", "album", "artwork", "scan", "обложк"]
        for f, path in images:
            f_lower = f.lower()
            for kw in keywords:
                if kw in f_lower:
                    return path
        
        for f, path in images:
            if f.lower().endswith(('.jpg', '.jpeg')):
                return path
        
        return images[0][1]
    
    if small_images:
        return small_images[0][1]
    
    return None

def optimize_cover(image_path, max_size=(1200, 1200), quality=100, upscale=True):
    """Оптимизирует изображение с возможностью увеличения маленьких"""
    try:
        img = Image.open(image_path)
        
        original_size = img.size
        is_small = original_size[0] < 300 or original_size[1] < 300
        
        if is_small:
            console.print(f"[yellow]Warning: Small image detected ({original_size[0]}x{original_size[1]})[/yellow]")
            if upscale and SETTINGS["upscale_small"]:
                new_size = (max_size[0], max_size[1])
                img = img.resize(new_size, Image.Resampling.LANCZOS)
                console.print(f"[green]Upscaled to {new_size[0]}x{new_size[1]}[/green]")
        
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        
        if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=quality, optimize=False, subsampling=0)
        return buffer.getvalue()
    except Exception as e:
        console.print(f"[red]Error optimizing cover: {e}[/red]")
        return None

def has_cover(path):
    """Проверяет наличие обложки"""
    ext = os.path.splitext(path)[1].lower()
    try:
        if ext == ".mp3":
            audio = ID3(path)
            return len(audio.getall('APIC')) > 0
        elif ext == ".flac":
            audio = FLAC(path)
            return len(audio.pictures) > 0
        elif ext in [".m4a", ".aac"]:
            audio = MP4(path)
            return 'covr' in audio
        elif ext == ".ogg":
            audio = OggVorbis(path)
            return 'metadata_block_picture' in audio
        elif ext == ".wav":
            try:
                audio = ID3(path)
                return len(audio.getall('APIC')) > 0
            except:
                return False
    except:
        return False
    return False

def add_cover_to_file(path, cover_data):
    """Добавляет обложку в теги"""
    ext = os.path.splitext(path)[1].lower()
    try:
        if ext == ".mp3":
            audio = ID3(path)
            audio.delall('APIC')
            audio.add(APIC(
                encoding=3,
                mime='image/jpeg',
                type=3,
                desc='Cover',
                data=cover_data
            ))
            audio.save()
            return True
        elif ext == ".flac":
            audio = FLAC(path)
            audio.clear_pictures()
            pic = Picture()
            pic.type = 3
            pic.mime = 'image/jpeg'
            pic.desc = 'Cover'
            pic.data = cover_data
            audio.add_picture(pic)
            audio.save()
            return True
        elif ext in [".m4a", ".aac"]:
            audio = MP4(path)
            audio['covr'] = [cover_data]
            audio.save()
            return True
        elif ext == ".ogg":
            audio = OggVorbis(path)
            cover_b64 = base64.b64encode(cover_data).decode('ascii')
            if 'metadata_block_picture' in audio:
                del audio['metadata_block_picture']
            audio['metadata_block_picture'] = [cover_b64]
            audio.save()
            return True
        elif ext == ".wav":
            try:
                audio = ID3(path)
                audio.delall('APIC')
                audio.add(APIC(
                    encoding=3,
                    mime='image/jpeg',
                    type=3,
                    desc='Cover',
                    data=cover_data
                ))
                audio.save()
                return True
            except:
                return False
    except Exception as e:
        console.print(f"[red]Error adding cover: {e}[/red]")
        return False
    return False

def add_covers_to_folder(folder, recursive=True, force=False):
    """Добавляет обложки ко всем файлам в папке (и подпапках)"""
    clear_screen()
    console.print(Panel(f"[bold green]{t('add_covers')}...[/bold green]\n[dim]{folder}[/dim]"))
    
    if force:
        console.print("[bold yellow]Force mode: replacing existing covers[/bold yellow]")
    if SETTINGS["ignore_small_covers"]:
        console.print("[dim]Ignoring small preview covers (AlbumArtSmall, etc.)[/dim]")
    if SETTINGS["upscale_small"]:
        console.print("[dim]Upscaling small covers to target size[/dim]")
    
    console.print(f"[dim]Target size: {SETTINGS['cover_size'][0]}x{SETTINGS['cover_size'][1]}[/dim]")
    console.print(f"[dim]Quality: {SETTINGS['cover_quality']}%[/dim]")
    
    folders_to_process = [folder]
    if recursive:
        for root, dirs, _ in os.walk(folder):
            for d in dirs:
                folders_to_process.append(os.path.join(root, d))
    
    total_added = 0
    total_skipped = 0
    total_errors = 0
    total_folders = 0
    total_small_covers = 0
    total_upscaled = 0
    
    for folder_path in folders_to_process:
        cover_file = find_cover_in_folder(folder_path)
        if not cover_file:
            continue
        
        total_folders += 1
        
        is_small = is_small_cover(os.path.basename(cover_file))
        if is_small:
            total_small_covers += 1
        
        console.print(f"\n[cyan]{os.path.basename(folder_path) or folder_path}[/cyan]")
        cover_status = "[yellow]SMALL PREVIEW[/yellow]" if is_small else "[green]FULL SIZE[/green]"
        console.print(f"[dim]Cover: {os.path.basename(cover_file)} {cover_status}[/dim]")
        
        cover_data = optimize_cover(
            cover_file, 
            SETTINGS["cover_size"], 
            SETTINGS["cover_quality"],
            SETTINGS["upscale_small"]
        )
        if not cover_data:
            console.print("[red]Failed to process cover[/red]")
            continue
        
        count = 0
        skipped = 0
        errors = 0
        replaced = 0
        upscaled = 0
        
        for f in os.listdir(folder_path):
            if f.lower().endswith(SUPPORTED_EXT):
                path = os.path.join(folder_path, f)
                
                has_cover_flag = has_cover(path)
                
                if has_cover_flag and not force:
                    skipped += 1
                    continue
                
                if SETTINGS["write"]:
                    if add_cover_to_file(path, cover_data):
                        count += 1
                        if is_small and SETTINGS["upscale_small"]:
                            upscaled += 1
                        if has_cover_flag and force:
                            replaced += 1
                            console.print(f"  [yellow]↻[/yellow] {f} ({t('cover_replaced')})")
                        else:
                            console.print(f"  [green]✓[/green] {f}")
                    else:
                        errors += 1
                        console.print(f"  [red]✗[/red] {f}")
                else:
                    count += 1
                    if has_cover_flag and force:
                        console.print(f"  [yellow]DRY-RUN:[/yellow] {f} ({t('cover_replaced')})")
                    else:
                        console.print(f"  [cyan]DRY-RUN:[/cyan] {f}")
        
        total_added += count
        total_skipped += skipped
        total_errors += errors
        total_upscaled += upscaled
        
        if count > 0 or skipped > 0:
            status = f"Added: {count}"
            if replaced > 0:
                status += f" (Replaced: {replaced})"
            if upscaled > 0:
                status += f" (Upscaled: {upscaled})"
            if skipped > 0:
                status += f", Skipped: {skipped}"
            console.print(f"  └── {status}")
    
    console.print(f"\n[bold green]{t('cover_operation')}[/bold green]")
    console.print(f"  ├── Folders processed: [cyan]{total_folders}[/cyan]")
    console.print(f"  ├── Covers added/replaced: [green]{total_added}[/green]")
    console.print(f"  ├── Skipped (already have cover): [yellow]{total_skipped}[/yellow]")
    if total_upscaled > 0:
        console.print(f"  ├── Upscaled from small: [yellow]{total_upscaled}[/yellow]")
    if total_small_covers > 0:
        console.print(f"  ├── Folders using small previews: [yellow]{total_small_covers}[/yellow]")
    if total_errors:
        console.print(f"  └── Errors: [red]{total_errors}[/red]")
    
    if total_small_covers > 0:
        console.print("\n[yellow]Tip: Some folders used small preview covers (AlbumArtSmall.jpg).[/yellow]")
        console.print("[yellow]For better quality, replace them with full-size cover images.[/yellow]")
    
    Prompt.ask(f"\n[dim]{t('press_enter')}[/dim]")

# ================= PARSER =================
def normalize(text):
    """Нормализует текст: заменяет _ на пробел, убирает лишние пробелы"""
    if not text:
        return text
    text = text.replace("_", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def parse_filename(filename):
    """Парсит имя файла в artist и title"""
    name = os.path.splitext(filename)[0]
    
    clean_name = name
    clean_name = re.sub(r"\s*\d{2,3}\s*BPM\s*", "", clean_name, flags=re.IGNORECASE)
    clean_name = re.sub(r"\s*\(\d{4}\)\s*", "", clean_name)
    clean_name = re.sub(r"\s*\[\d+\]\s*", "", clean_name)
    
    separators = [" - ", " – ", " — ", " | "]
    
    artist = None
    title = None
    
    for sep in separators:
        if sep in clean_name:
            parts = clean_name.split(sep, 1)
            artist = normalize(parts[0])
            title = normalize(parts[1])
            break
    
    if not artist:
        match = re.match(r"^(\d+)\s+(.+)$", clean_name)
        if match:
            track_num = match.group(1)
            rest = match.group(2)
            for sep in separators:
                if sep in rest:
                    parts = rest.split(sep, 1)
                    artist = normalize(parts[0])
                    title = normalize(parts[1])
                    break
            if not artist:
                artist = None
                title = normalize(rest)
        else:
            artist = None
            title = normalize(clean_name)
    
    return artist, title

def parse_track_metadata(name):
    """Парсит полные метаданные из имени файла"""
    artist, title = parse_filename(name)
    
    genres = ["DRUM & BASS", "DNB", "NEUROFUNK", "NEURO", "LIQUID", "JUMP UP", 
              "HARDSTYLE", "TECHNO", "HOUSE", "TRANCE", "DUBSTEP"]
    
    genre = None
    if title:
        title_upper = title.upper()
        for g in genres:
            if g in title_upper:
                genre = g
                break
    
    bpm = None
    if title:
        bpm_match = re.search(r"(\d{2,3})\s*BPM", title, re.IGNORECASE)
        if bpm_match:
            bpm = int(bpm_match.group(1))
    
    mix = None
    mix_keywords = ["VIP", "REMIX", "EDIT", "BOOTLEG", "REWORK", "FLIP", 
                    "EXTENDED", "CLUB MIX", "RADIO EDIT", "MASHUP"]
    
    if title:
        title_upper = title.upper()
        for kw in mix_keywords:
            if kw in title_upper:
                mix = kw
                break
    
    return {
        "artist": artist,
        "title": title,
        "genre": genre,
        "bpm": bpm,
        "mix": mix
    }

# ================= TAGGING =================
def clean_value(v: str):
    if SETTINGS["clean_underscores"] and v:
        return v.replace("_", " ").strip()
    return v.strip() if v else v

def save_wav_tags(path, artist=None, title=None, tracknumber=None, genre=None, bpm=None, mix=None):
    try:
        try:
            id3 = ID3(path)
        except ID3NoHeaderError:
            id3 = ID3()
        if title: id3.add(TIT2(encoding=3, text=title))
        if artist: id3.add(TPE1(encoding=3, text=artist))
        if tracknumber: id3.add(TRCK(encoding=3, text=tracknumber))
        if genre: id3.add(TCON(encoding=3, text=genre))
        if bpm: id3.add(TBPM(encoding=3, text=str(bpm)))
        if mix: id3.add(TXXX(encoding=3, desc="Mix", text=mix))
        id3.save(path)
    except Exception as e:
        console.print(f"[red]{t('error_save')}[/red] {os.path.basename(path)} → {e}")

def save_tags(path, artist=None, title=None, tracknumber=None, genre=None, bpm=None, mix=None):
    ext = os.path.splitext(path)[1].lower()
    try:
        if ext == ".mp3":
            audio = ID3(path)
            if title: audio.add(TIT2(encoding=3, text=title))
            if artist: audio.add(TPE1(encoding=3, text=artist))
            if tracknumber: audio.add(TRCK(encoding=3, text=tracknumber))
            if genre: audio.add(TCON(encoding=3, text=genre))
            if bpm: audio.add(TBPM(encoding=3, text=str(bpm)))
            if mix: audio.add(TXXX(encoding=3, desc="Mix", text=mix))
            audio.save()
        elif ext == ".flac":
            audio = FLAC(path)
            if title: audio["title"] = [title]
            if artist: audio["artist"] = [artist]
            if tracknumber: audio["tracknumber"] = [tracknumber]
            if genre: audio["genre"] = [genre] if genre else None
            if bpm: audio["bpm"] = [str(bpm)]
            if mix: audio["mix"] = [mix]
            audio.save()
        elif ext == ".wav":
            save_wav_tags(path, artist, title, tracknumber, genre, bpm, mix)
        elif ext == ".ogg":
            audio = OggVorbis(path)
            if title: audio["title"] = [title]
            if artist: audio["artist"] = [artist]
            if tracknumber: audio["tracknumber"] = [tracknumber]
            if genre: audio["genre"] = [genre] if genre else None
            if bpm: audio["bpm"] = [str(bpm)]
            if mix: audio["mix"] = [mix]
            audio.save()
        elif ext in [".m4a", ".aac"]:
            audio = MP4(path)
            if title: audio["\xa9nam"] = [title]
            if artist: audio["\xa9ART"] = [artist]
            if tracknumber: audio["trkn"] = [(int(tracknumber) if tracknumber else 0, 0)]
            if genre: audio["\xa9gen"] = [genre]
            if bpm: audio["tmpo"] = int(bpm) if bpm else 0
            if mix: audio["----:com.apple.iTunes:Mix"] = [mix]
            audio.save()
        else:
            console.print(f"[yellow]{t('unsupported')}:[/yellow] {os.path.basename(path)}")
    except Exception as e:
        console.print(f"[red]{t('error_save')}[/red] {os.path.basename(path)} → {e}")

# ================= SCAN =================
def scan_files(folder, mode=None, title_only=False, recursive=True):
    """Сканирует файлы в папке и подпапках"""
    clear_screen()
    console.print(Panel(f"[bold cyan]Processing files...[/bold cyan]\n[dim]{folder}[/dim]"))
    
    if recursive:
        console.print("[dim]Recursive mode: processing all subfolders[/dim]")
    
    if SETTINGS["use_ffprobe"] and check_ffprobe():
        console.print("[dim]Using ffprobe for metadata extraction[/dim]")
    elif SETTINGS["use_ffprobe"]:
        console.print("[yellow]" + t('ffprobe_not_found') + "[/yellow]")
    
    count = 0
    audio_files = []
    
    if recursive:
        for root, _, files in os.walk(folder):
            for f in files:
                if f.lower().endswith(SUPPORTED_EXT):
                    audio_files.append(os.path.join(root, f))
    else:
        for f in os.listdir(folder):
            if f.lower().endswith(SUPPORTED_EXT):
                audio_files.append(os.path.join(folder, f))
    
    if not audio_files:
        console.print("[yellow]No audio files found[/yellow]")
        Prompt.ask(f"\n[dim]{t('press_enter')}[/dim]")
        return
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]Processing...", total=len(audio_files))
        
        for path in audio_files:
            process_file(path, mode, title_only)
            progress.advance(task)
    
    console.print(f"\n[bold green]{t('done')}: {len(audio_files)}[/bold green]")
    Prompt.ask(f"\n[dim]{t('press_enter')}[/dim]")

def process_file(path, mode=None, title_only=False):
    """Обрабатывает один файл"""
    filename = os.path.basename(path)
    name = os.path.splitext(filename)[0]
    
    console.print(f"\n[cyan]{filename}[/cyan]")
    
    # Пробуем получить метаданные через ffprobe если включено
    meta_from_file = {}
    if SETTINGS["use_ffprobe"] and check_ffprobe():
        info = get_audio_info_ffprobe(path)
        if info.get('artist') or info.get('title'):
            meta_from_file = {
                'artist': info.get('artist', ''),
                'title': info.get('title', ''),
                'genre': info.get('genre', ''),
                'bpm': None,
                'mix': None
            }
            console.print(f"  [dim]Using ffprobe metadata[/dim]")
    
    # Парсим из имени файла
    meta = parse_track_metadata(name)
    
    # Если есть данные из ffprobe, используем их как основу
    if meta_from_file.get('artist') or meta_from_file.get('title'):
        if not meta_from_file.get('artist') and meta.get('artist'):
            meta_from_file['artist'] = meta['artist']
        if not meta_from_file.get('title') and meta.get('title'):
            meta_from_file['title'] = meta['title']
        meta = meta_from_file
    
    if title_only:
        meta["title"] = normalize(name)
        meta["artist"] = None
    
    tracknumber = None
    if mode == "tracknum":
        match = re.match(r"^(\d+)\s+", name)
        if match:
            tracknumber = match.group(1)
    
    if meta.get("artist"):
        console.print(f"  ├── ARTIST: [white]{meta['artist']}[/white]")
    if meta.get("title"):
        console.print(f"  ├── TITLE: [white]{meta['title']}[/white]")
    if meta.get("genre"):
        console.print(f"  ├── GENRE: [white]{meta['genre']}[/white]")
    if meta.get("bpm"):
        console.print(f"  ├── BPM: [white]{meta['bpm']}[/white]")
    if meta.get("mix"):
        console.print(f"  ├── MIX: [white]{meta['mix']}[/white]")
    if tracknumber:
        console.print(f"  ├── TRACK: [white]{tracknumber}[/white]")
    
    if SETTINGS["write"]:
        save_tags(
            path,
            artist=meta.get("artist"),
            title=meta.get("title"),
            tracknumber=tracknumber,
            genre=meta.get("genre"),
            bpm=meta.get("bpm"),
            mix=meta.get("mix")
        )

# ================= RENAMING =================
def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", str(name)).strip()

def rename_files(folder, format_type="basic", recursive=True):
    """Переименовывает файлы в папке и подпапках"""
    clear_screen()
    console.print(Panel(f"[bold magenta]Renaming files...[/bold magenta]\n[dim]{folder}[/dim]"))
    
    if recursive:
        console.print("[dim]Recursive mode: processing all subfolders[/dim]")
    
    count = 0
    audio_files = []
    
    if recursive:
        for root, _, files in os.walk(folder):
            for f in files:
                if f.lower().endswith(SUPPORTED_EXT):
                    audio_files.append(os.path.join(root, f))
    else:
        for f in os.listdir(folder):
            if f.lower().endswith(SUPPORTED_EXT):
                audio_files.append(os.path.join(folder, f))
    
    if not audio_files:
        console.print("[yellow]No audio files found[/yellow]")
        Prompt.ask(f"\n[dim]{t('press_enter')}[/dim]")
        return
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]Renaming...", total=len(audio_files))
        
        for path in audio_files:
            rename_file(path, format_type)
            progress.advance(task)
    
    console.print(f"\n[bold green]{t('done')}: {len(audio_files)}[/bold green]")
    Prompt.ask(f"\n[dim]{t('press_enter')}[/dim]")

def rename_file(path, format_type="basic"):
    """Переименовывает один файл"""
    try:
        audio = File(path, easy=True)
        if audio is None:
            console.print(f"[yellow]{t('unsupported')}[/yellow] {os.path.basename(path)}")
            return

        artist = audio.get("artist", ["Unknown Artist"])[0]
        title = audio.get("title", ["Unknown Title"])[0]
        
        clean_artist = sanitize_filename(artist)
        clean_title = sanitize_filename(title)
        
        if format_type == "basic":
            new_name = f"{clean_artist} - {clean_title}"
        elif format_type == "tracknum":
            track_raw = str(audio.get("tracknumber", ["00"])[0])
            tracknum = track_raw.split('/')[0].zfill(2)
            new_name = f"{tracknum} {clean_artist} - {clean_title}"
        else:
            return

        dir_name = os.path.dirname(path)
        ext = os.path.splitext(path)[1].lower()
        new_path = os.path.join(dir_name, new_name + ext)
        
        if path == new_path:
            return
            
        if not SETTINGS["write"]:
            console.print(f"[cyan]DRY-RUN:[/cyan] {os.path.basename(path)} [bold white]→[/bold white] {new_name}{ext}")
        else:
            os.rename(path, new_path)
            console.print(f"[dim]{os.path.basename(path)}[/dim] [bold white]→[/bold white] [green]{new_name}{ext}[/green]")
            
    except Exception as e:
        console.print(f"[red]Error renaming {os.path.basename(path)}:[/red] {e}")

# ================= MENUS =================
def ask_folder():
    global CURRENT_FOLDER
    root = tk.Tk()
    root.withdraw()
    folder = filedialog.askdirectory(title=t("select_folder"))
    root.destroy()
    if folder:
        CURRENT_FOLDER = folder
        return folder
    console.print(f"[red]{t('folder_not_selected')}[/red]")
    return None

def settings_menu():
    while True:
        clear_screen()
        table = Table(box=box.SIMPLE, show_header=False)
        table.add_column("Key", style="bold yellow")
        table.add_column("Setting", style="white")
        
        table.add_row("1", f"{t('replace_underscores')}: [bold cyan]{SETTINGS['clean_underscores']}[/bold cyan]")
        table.add_row("2", f"Language: [bold cyan]{SETTINGS['lang']}[/bold cyan]")
        table.add_row("3", f"{t('cover_size_lbl')}: [bold cyan]{SETTINGS['cover_size'][0]}x{SETTINGS['cover_size'][1]}[/bold cyan]")
        table.add_row("4", f"{t('cover_quality_lbl')}: [bold cyan]{SETTINGS['cover_quality']}%[/bold cyan]")
        table.add_row("5", f"{t('recursive_mode')}: [bold cyan]{SETTINGS['recursive']}[/bold cyan]")
        table.add_row("6", f"{t('force_cover')}: [bold cyan]{SETTINGS['force_cover']}[/bold cyan]")
        table.add_row("7", f"{t('ignore_small')}: [bold cyan]{SETTINGS['ignore_small_covers']}[/bold cyan]")
        table.add_row("8", f"{t('upscale_small')}: [bold cyan]{SETTINGS['upscale_small']}[/bold cyan]")
        table.add_row("9", f"{t('use_ffprobe')}: [bold cyan]{SETTINGS['use_ffprobe']}[/bold cyan]")
        table.add_row("0", f"[dim]{t('back')}[/dim]")
        
        console.print(Panel(table, title=f"[bold]{t('settings')}[/bold]", expand=False, border_style="blue"))
        
        c = Prompt.ask("Choice", choices=["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"])
        if c == "1":
            SETTINGS["clean_underscores"] = not SETTINGS["clean_underscores"]
        elif c == "2":
            SETTINGS["lang"] = "RU" if SETTINGS["lang"] == "EN" else "EN"
        elif c == "3":
            try:
                console.print("[dim]Enter max size (width height), e.g. 1200 1200[/dim]")
                size_input = Prompt.ask("Size")
                w, h = map(int, size_input.split())
                if w > 0 and h > 0:
                    SETTINGS["cover_size"] = (w, h)
            except:
                console.print("[red]Invalid size, keeping current[/red]")
        elif c == "4":
            try:
                quality = int(Prompt.ask("Quality (1-100)", default="100"))
                if 1 <= quality <= 100:
                    SETTINGS["cover_quality"] = quality
            except:
                console.print("[red]Invalid quality, keeping current[/red]")
        elif c == "5":
            SETTINGS["recursive"] = not SETTINGS["recursive"]
        elif c == "6":
            SETTINGS["force_cover"] = not SETTINGS["force_cover"]
        elif c == "7":
            SETTINGS["ignore_small_covers"] = not SETTINGS["ignore_small_covers"]
        elif c == "8":
            SETTINGS["upscale_small"] = not SETTINGS["upscale_small"]
        elif c == "9":
            SETTINGS["use_ffprobe"] = not SETTINGS["use_ffprobe"]
            if SETTINGS["use_ffprobe"] and not check_ffprobe():
                console.print("[yellow]" + t('ffprobe_not_found') + "[/yellow]")
                Prompt.ask("Press Enter to continue...")
        elif c == "0":
            return

def ensure_folder():
    global CURRENT_FOLDER
    if CURRENT_FOLDER is None:
        console.print(f"[yellow]{t('folder_required')}[/yellow]")
        folder = ask_folder()
        if folder is None:
            return False
    return True

def draw_main_menu():
    clear_screen()
    write_status = t("status_write_on") if SETTINGS["write"] else t("status_write_off")
    recursive_status = "[green]ON[/green]" if SETTINGS["recursive"] else "[red]OFF[/red]"
    force_status = "[green]ON[/green]" if SETTINGS["force_cover"] else "[red]OFF[/red]"
    ignore_status = "[green]ON[/green]" if SETTINGS["ignore_small_covers"] else "[red]OFF[/red]"
    upscale_status = "[green]ON[/green]" if SETTINGS["upscale_small"] else "[red]OFF[/red]"
    ffprobe_status = "[green]ON[/green]" if SETTINGS["use_ffprobe"] else "[red]OFF[/red]"
    folder_display = CURRENT_FOLDER if CURRENT_FOLDER else "[dim]Not selected[/dim]"
    
    header = (
        f"[dim]{t('current_folder')}:[/dim] [bold cyan]{folder_display}[/bold cyan]\n"
        f"[dim]{t('write_mode_lbl')}:[/dim] {write_status}  |  [dim]Recursive:[/dim] {recursive_status}  |  [dim]Force:[/dim] {force_status}\n"
        f"[dim]Ignore Small:[/dim] {ignore_status}  |  [dim]Upscale:[/dim] {upscale_status}  |  [dim]ffprobe:[/dim] {ffprobe_status}\n"
        f"[dim]Size:[/dim] {SETTINGS['cover_size'][0]}x{SETTINGS['cover_size'][1]}"
    )
    console.print(Panel(header, title=f"[bold magenta]{t('app_title')}[/bold magenta]", expand=False, box=box.ROUNDED))
    
    menu_table = Table(box=box.SIMPLE, show_header=False)
    menu_table.add_column("Key", style="bold yellow", justify="right")
    menu_table.add_column("Action", style="white")
    
    menu_table.add_row("1", t("artist_track"))
    menu_table.add_row("2", t("tracknum_artist_track"))
    menu_table.add_row("3", t("all_title"))
    menu_table.add_row("")
    menu_table.add_row("4", t("rename_basic"))
    menu_table.add_row("5", t("rename_tracknum"))
    menu_table.add_row("")
    menu_table.add_row("6", f"[bold green]{t('add_covers')}[/bold green]")
    menu_table.add_row("")
    menu_table.add_row("7", t("toggle_dry_run"))
    menu_table.add_row("8", t("change_folder"))
    menu_table.add_row("9", t("settings"))
    menu_table.add_row("")
    menu_table.add_row("0", f"[dim]{t('exit')}[/dim]")
    
    console.print(menu_table)
    console.print()

def main_loop():
    while True:
        draw_main_menu()
        choice = Prompt.ask("Choice", choices=["1","2","3","4","5","6","7","8","9","0"])
        
        if choice == "0":
            console.print(f"[green]{t('goodbye')}[/green]")
            sys.exit(0)
        elif choice == "8":
            ask_folder()
        elif choice == "9":
            settings_menu()
        elif choice == "7":
            SETTINGS["write"] = not SETTINGS["write"]
        elif choice == "6":
            if not ensure_folder():
                continue
            add_covers_to_folder(CURRENT_FOLDER, SETTINGS["recursive"], SETTINGS["force_cover"])
        elif choice in ["1", "2", "3", "4", "5"]:
            if not ensure_folder():
                continue
            if SETTINGS["write"] and not Confirm.ask(f"[bold red]WARNING:[/bold red] {t('continue')}"):
                continue
                
            if choice == "1":
                scan_files(CURRENT_FOLDER, mode="basic", recursive=SETTINGS["recursive"])
            elif choice == "2":
                scan_files(CURRENT_FOLDER, mode="tracknum", recursive=SETTINGS["recursive"])
            elif choice == "3":
                scan_files(CURRENT_FOLDER, title_only=True, recursive=SETTINGS["recursive"])
            elif choice == "4":
                rename_files(CURRENT_FOLDER, format_type="basic", recursive=SETTINGS["recursive"])
            elif choice == "5":
                rename_files(CURRENT_FOLDER, format_type="tracknum", recursive=SETTINGS["recursive"])

## ================= RUN =================
if __name__ == "__main__":
    try:
        # Проверка на drag & drop (передача папки как аргумент)
        args = sys.argv[1:]
        if args:
            first_path = os.path.abspath(args[0])
            if os.path.isdir(first_path):
                folder = first_path
            elif os.path.isfile(first_path):
                folder = os.path.dirname(first_path)
            else:
                folder = None
            
            if folder:
                global CURRENT_FOLDER
                CURRENT_FOLDER = folder
                console.print(f"\n[bold green]📁 {t('drag_drop_detected')}:[/bold green] {folder}")
                if Confirm.ask(f"[bold]Process files in this folder?[/bold]", default=True):
                    console.print("\n[dim]Select action:[/dim]")
                    console.print("1. Artist - Track")
                    console.print("2. 01 Artist - Track")
                    console.print("3. All filename as TITLE")
                    console.print("4. Rename: Artist - Track")
                    console.print("5. Rename: 01 Artist - Track")
                    console.print("6. Add covers")
                    action = Prompt.ask("Choice", choices=["1","2","3","4","5","6"])
                    
                    if action == "1":
                        scan_files(folder, mode="basic", recursive=SETTINGS["recursive"])
                    elif action == "2":
                        scan_files(folder, mode="tracknum", recursive=SETTINGS["recursive"])
                    elif action == "3":
                        scan_files(folder, title_only=True, recursive=SETTINGS["recursive"])
                    elif action == "4":
                        rename_files(folder, format_type="basic", recursive=SETTINGS["recursive"])
                    elif action == "5":
                        rename_files(folder, format_type="tracknum", recursive=SETTINGS["recursive"])
                    elif action == "6":
                        add_covers_to_folder(folder, SETTINGS["recursive"], SETTINGS["force_cover"])
                    sys.exit(0)
        
        main_loop()
    except KeyboardInterrupt:
        console.print("\n[yellow]Aborted.[/yellow]")
        input("\nPress Enter to exit...")
    except Exception as e:
        console.print(f"[red]FATAL ERROR:[/red] {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
