import os
import re
import tkinter as tk
from tkinter import filedialog

from mutagen import File
from mutagen.id3 import ID3, TIT2, TPE1, TCON, TBPM, TRCK, TXXX, ID3NoHeaderError
from mutagen.flac import FLAC
from mutagen.wave import WAVE
from mutagen.oggvorbis import OggVorbis
from mutagen.mp4 import MP4

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich import box

console = Console()

# ================= SETTINGS =================
SUPPORTED_EXT = (".mp3", ".flac", ".ogg", ".wav", ".m4a", ".aac", ".opus")

PATTERNS = {
    "basic": re.compile(r"^(?P<artist>.+?)\s*-\s*(?P<title>.+)$"),
    "tracknum": re.compile(r"^(?P<tracknumber>\d+)\s+(?P<artist>.+?)\s*-\s*(?P<title>.+)$"),
}

SETTINGS = {
    "write": True,  # True = записываем, False = Dry-Run
    "clean_underscores": True,
    "lang": "EN"
}

CURRENT_FOLDER = None

# ================= LANGUAGES =================
TEXTS = {
    "EN": {
        "select_folder": "Select folder with audio files",
        "folder_not_selected": "Folder not selected.",
        "meta_title": "MetaForge v2.0",
        "current_folder": "Folder",
        
        "cat_tags": "WRITE TAGS (Filename → Tags)",
        "artist_track": "Artist - Track",
        "tracknum_artist_track": "01 Artist - Track",
        "all_title": "Use filename as TITLE only",
        
        "cat_rename": "RENAME FILES (Tags → Filename)",
        "rename_basic": "Artist - Track",
        "rename_tracknum": "01 Artist - Track",
        
        "cat_system": "SYSTEM",
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
        "press_exit": "Press Enter to exit...",
        "folder_required": "Please select a folder first (option 7)"
    },
    "RU": {
        "select_folder": "Выберите папку с треками",
        "folder_not_selected": "Папка не выбрана.",
        "meta_title": "MetaForge v2.0",
        "current_folder": "Папка",
        
        "cat_tags": "ЗАПИСЬ ТЕГОВ (Имя файла → Теги)",
        "artist_track": "Автор - Трек",
        "tracknum_artist_track": "01 Автор - Трек",
        "all_title": "Всё имя файла → в TITLE",
        
        "cat_rename": "ПЕРЕИМЕНОВАНИЕ (Теги → Имя файла)",
        "rename_basic": "Автор - Трек",
        "rename_tracknum": "01 Автор - Трек",
        
        "cat_system": "СИСТЕМА",
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
        "press_exit": "Нажмите Enter для выхода...",
        "folder_required": "Пожалуйста, сначала выберите папку (пункт 7)"
    }
}

def t(key):
    return TEXTS[SETTINGS["lang"]].get(key, key)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# ================= PARSER =================
MIX_KEYWORDS = [
    "VIP", "REMIX", "EDIT", "BOOTLEG", "REWORK",
    "FLIP", "EXTENDED", "CLUB MIX", "RADIO EDIT", "MASHUP"
]

GENRES = [
    "DRUM & BASS", "DNB", "NEUROFUNK", "NEURO",
    "LIQUID", "JUMP UP", "HARDSTYLE",
    "TECHNO", "HOUSE", "TRANCE", "DUBSTEP"
]

def normalize(text):
    return re.sub(r"\s+", " ", text.replace("_", " ")).strip()

def extract_bpm(text):
    m = re.search(r"\b(\d{2,3})\s*BPM\b", text, re.IGNORECASE)
    return int(m.group(1)) if m else None

def extract_genre(text):
    up = text.upper()
    for g in GENRES:
        if g in up:
            return g
    return None

def extract_mix(text):
    mixes = set()
    for m in re.findall(r"[\(\[]([^\)\]]+)[\)\]]", text):
        u = m.upper()
        for k in MIX_KEYWORDS:
            if k in u:
                mixes.add(u)
                break
    for k in MIX_KEYWORDS:
        if re.search(rf"\b{re.escape(k)}\b", text, re.IGNORECASE):
            mixes.add(k)
    return " / ".join(sorted(mixes)) if mixes else None

def strip_extra(text):
    text = re.sub(r"\|.*$", "", text)
    text = re.sub(r"\b\d{2,3}\s*BPM\b", "", text, flags=re.IGNORECASE)
    text = re.sub(r"[\(\[].*?[\)\]]", "", text)
    return normalize(text)

def split_artist_title(text):
    for sep in [" - ", " – ", " | "]:
        if sep in text:
            a, t = text.split(sep, 1)
            return normalize(a), normalize(t)
    return None, normalize(text)

def parse_track_metadata(name):
    raw = name
    w = normalize(name)
    bpm = extract_bpm(w)
    genre = extract_genre(w)
    mix = extract_mix(w)
    w = strip_extra(w)
    artist, title = split_artist_title(w)
    clean = normalize(" - ".join(x for x in [artist, title, mix] if x))
    return {
        "raw": raw,
        "artist": artist,
        "title": title,
        "mix": mix,
        "bpm": bpm,
        "genre": genre,
        "clean": clean
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

# ================= FILE PROCESS =================
def process_file(path, mode=None, title_only=False):
    name = os.path.splitext(os.path.basename(path))[0]
    data = {}
    if mode:
        pattern = PATTERNS.get(mode)
        m = pattern.match(name) if pattern else None
        if not m:
            console.print(f"[yellow]{t('skip')}[/yellow] {name}")
            return
        data = {k: clean_value(v) for k, v in m.groupdict().items()}
    meta = parse_track_metadata(name)
    console.print(f"\n[cyan]{os.path.basename(path)}[/cyan]")
    
    if title_only:
        console.print(f"  └── TITLE: [white]{meta['title'] or meta['clean']}[/white]")
        if SETTINGS["write"]:
            save_tags(path, title=meta['title'] or meta['clean'])
    else:
        for k in ["artist", "title", "mix", "bpm", "genre"]:
            if meta.get(k):
                console.print(f"  ├── {k.upper()}: [white]{meta[k]}[/white]")
        if SETTINGS["write"]:
            save_tags(
                path,
                artist=meta.get("artist"),
                title=meta.get("title"),
                tracknumber=data.get("tracknumber"),
                genre=meta.get("genre"),
                bpm=meta.get("bpm"),
                mix=meta.get("mix")
            )

def scan(folder, mode=None, title_only=False):
    clear_screen()
    console.print(Panel(f"[bold cyan]Scanning...[/bold cyan]\n[dim]{folder}[/dim]"))
    count = 0
    for root, _, files in os.walk(folder):
        for f in files:
            if f.lower().endswith(SUPPORTED_EXT):
                process_file(os.path.join(root, f), mode=mode, title_only=title_only)
                count += 1
    console.print(f"\n[bold green]{t('done')}: {count}[/bold green]")
    Prompt.ask(f"\n[dim]{t('press_enter')}[/dim]")

# ================= RENAMING =================
def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", str(name)).strip()

def rename_file(path, format_type="basic"):
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

def scan_rename(folder, format_type="basic"):
    clear_screen()
    console.print(Panel(f"[bold magenta]Renaming Files...[/bold magenta]\n[dim]{folder}[/dim]"))
    count = 0
    for root, _, files in os.walk(folder):
        for f in files:
            if f.lower().endswith(SUPPORTED_EXT):
                rename_file(os.path.join(root, f), format_type)
                count += 1
    console.print(f"\n[bold green]{t('done')}: {count}[/bold green]")
    Prompt.ask(f"\n[dim]{t('press_enter')}[/dim]")

# ================= MENUS =================
def ask_folder():
    global CURRENT_FOLDER
    root = tk.Tk()
    root.withdraw()
    folder = filedialog.askdirectory(title=t("select_folder"))
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
        table.add_row("0", f"[dim]{t('back')}[/dim]")
        
        console.print(Panel(table, title=f"[bold]{t('settings')}[/bold]", expand=False, border_style="blue"))
        
        c = Prompt.ask("Choice", choices=["1", "2", "0"])
        if c == "1":
            SETTINGS["clean_underscores"] = not SETTINGS["clean_underscores"]
        elif c == "2":
            SETTINGS["lang"] = "RU" if SETTINGS["lang"] == "EN" else "EN"
        elif c == "0":
            return

def ensure_folder():
    """Проверяет, выбрана ли папка; если нет – запрашивает."""
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
    
    folder_display = CURRENT_FOLDER if CURRENT_FOLDER else "[dim]Not selected[/dim]"
    
    # Шапка программы
    header = (
        f"[dim]{t('current_folder')}:[/dim] [bold cyan]{folder_display}[/bold cyan]\n"
        f"[dim]{t('write_mode_lbl')}:[/dim] {write_status}"
    )
    console.print(Panel(header, title=f"[bold magenta]{t('meta_title')}[/bold magenta]", expand=False, box=box.ROUNDED))
    
    # Тело меню в стиле Audio Converter (без иконок)
    menu_table = Table(box=box.SIMPLE, show_header=False)
    menu_table.add_column("Key", style="bold yellow", justify="right")
    menu_table.add_column("Action", style="white")
    
    # Группа 1: запись тегов
    menu_table.add_row("1", t("artist_track"))
    menu_table.add_row("2", t("tracknum_artist_track"))
    menu_table.add_row("3", t("all_title"))
    menu_table.add_row("")  # разделитель
    
    # Группа 2: переименование
    menu_table.add_row("4", t("rename_basic"))
    menu_table.add_row("5", t("rename_tracknum"))
    menu_table.add_row("")  # разделитель
    
    # Группа 3: системные
    menu_table.add_row("6", t("toggle_dry_run"))
    menu_table.add_row("7", t("change_folder"))
    menu_table.add_row("8", t("settings"))
    menu_table.add_row("")  # разделитель
    
    menu_table.add_row("0", f"[dim]{t('exit')}[/dim]")
    
    console.print(menu_table)
    console.print()

def main_loop():
    while True:
        draw_main_menu()
        choice = Prompt.ask("Choice", choices=["1","2","3","4","5","6","7","8","0"])
        
        if choice == "0":
            break
        elif choice == "7":
            # Сменить папку
            ask_folder()
        elif choice == "8":
            settings_menu()
        elif choice == "6":
            SETTINGS["write"] = not SETTINGS["write"]
        elif choice in ["1", "2", "3", "4", "5"]:
            # Действия, требующие папку
            if not ensure_folder():
                continue
            if SETTINGS["write"] and not Confirm.ask(f"[bold red]WARNING:[/bold red] {t('continue')}"):
                continue
                
            if choice == "1":
                scan(CURRENT_FOLDER, mode="basic")
            elif choice == "2":
                scan(CURRENT_FOLDER, mode="tracknum")
            elif choice == "3":
                scan(CURRENT_FOLDER, title_only=True)
            elif choice == "4":
                scan_rename(CURRENT_FOLDER, format_type="basic")
            elif choice == "5":
                scan_rename(CURRENT_FOLDER, format_type="tracknum")

# ================= RUN =================
if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        console.print("\n[yellow]Aborted.[/yellow]")
    except Exception as e:
        console.print(f"[red]FATAL ERROR:[/red] {e}")
    finally:
        Prompt.ask(f"\n[dim]{t('press_exit')}[/dim]")
