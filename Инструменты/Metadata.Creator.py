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
from rich import print
from rich.prompt import Prompt, Confirm

# ================= SETTINGS =================
SUPPORTED_EXT = (".mp3", ".flac", ".ogg", ".wav", ".m4a", ".aac", ".opus")

PATTERNS = {
    "basic": re.compile(r"^(?P<artist>.+?)\s*-\s*(?P<title>.+)$"),
    "tracknum": re.compile(r"^(?P<tracknumber>\d+)\s+(?P<artist>.+?)\s*-\s*(?P<title>.+)$"),
}

SETTINGS = {
    "write": True,
    "clean_underscores": True,
    "lang": "EN"  # по умолчанию английский
}

CURRENT_FOLDER = None

# ================= LANGUAGES =================
TEXTS = {
    "EN": {
        "select_folder": "Select folder with audio files",
        "folder_not_selected": "Folder not selected.",
        "meta_title": "MetaForge",
        "current_folder": "Current folder",
        "artist_track": "Artist - Track",
        "tracknum_artist_track": "01 Artist - Track",
        "all_title": "Use filename as TITLE",
        "dry_run": "Dry-run (no write)",
        "change_folder": "Change folder",
        "settings": "Settings",
        "exit": "Exit",
        "continue": "Continue?",
        "write_changes": "Write changes",
        "replace_underscores": "Replace _ with space",
        "skip": "SKIP",
        "unsupported": "Unsupported format",
        "error_save": "Error saving tags",
        "done": "Done. Files processed",
        "press_enter": "Press Enter to exit..."
    },
    "RU": {
        "select_folder": "Выберите папку с треками",
        "folder_not_selected": "Папка не выбрана.",
        "meta_title": "MetaForge",
        "current_folder": "Текущая папка",
        "artist_track": "Автор - Трек",
        "tracknum_artist_track": "01 Автор - Трек",
        "all_title": "Всё имя файла → TITLE",
        "dry_run": "Dry-run (без записи)",
        "change_folder": "Сменить папку",
        "settings": "Настройки",
        "exit": "Выход",
        "continue": "Продолжить?",
        "write_changes": "Записывать изменения",
        "replace_underscores": "Заменять _ на пробел",
        "skip": "SKIP",
        "unsupported": "Неподдерживаемый формат",
        "error_save": "Ошибка при сохранении тегов",
        "done": "Готово. Обработано файлов",
        "press_enter": "Нажмите Enter для выхода..."
    }
}

def t(key):
    return TEXTS[SETTINGS["lang"]].get(key, key)

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
        print(f"[red]{t('error_save')}[/red] {path} → {e}")

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
            print(f"[yellow]{t('unsupported')}:[/yellow] {path}")
    except Exception as e:
        print(f"[red]{t('error_save')}[/red] {path} → {e}")

# ================= FILE PROCESS =================
def process_file(path, mode=None, title_only=False):
    name = os.path.splitext(os.path.basename(path))[0]
    data = {}
    if mode:
        pattern = PATTERNS.get(mode)
        m = pattern.match(name) if pattern else None
        if not m:
            print(f"[yellow]{t('skip')}[/yellow] {name}")
            return
        data = {k: clean_value(v) for k, v in m.groupdict().items()}
    meta = parse_track_metadata(name)
    print(f"[cyan]{os.path.basename(path)}[/cyan]")
    if title_only:
        print(f"  TITLE → {meta['title'] or meta['clean']}")
        if SETTINGS["write"]:
            save_tags(path, title=meta['title'] or meta['clean'])
    else:
        for k in ["artist", "title", "mix", "bpm", "genre"]:
            if meta.get(k):
                print(f"  {k.upper()} → {meta[k]}")
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
    count = 0
    for root, _, files in os.walk(folder):
        for f in files:
            if f.lower().endswith(SUPPORTED_EXT):
                process_file(os.path.join(root, f), mode=mode, title_only=title_only)
                count += 1
    print(f"\n🎧 {t('done')}: {count}")

# ================= MENU =================
def settings_menu():
    while True:
        print("\n[bold]"+t("settings")+"[/bold]")
        print(f"1) {t('write_changes')}: {SETTINGS['write']}")
        print(f"2) {t('replace_underscores')}: {SETTINGS['clean_underscores']}")
        print(f"3) Language: {SETTINGS['lang']}")
        print("0) Back / Назад")
        c = Prompt.ask("Choice", choices=["1","2","3","0"])
        if c == "1":
            SETTINGS["write"] = not SETTINGS["write"]
        elif c == "2":
            SETTINGS["clean_underscores"] = not SETTINGS["clean_underscores"]
        elif c == "3":
            SETTINGS["lang"] = "RU" if SETTINGS["lang"]=="EN" else "EN"
        elif c == "0":
            return

def ask_folder():
    global CURRENT_FOLDER
    root = tk.Tk()
    root.withdraw()
    folder = filedialog.askdirectory(title=t("select_folder"))
    if folder:
        CURRENT_FOLDER = folder
        return folder
    print("[red]"+t("folder_not_selected")+"[/red]")
    return None

def main_menu():
    folder = ask_folder()
    if not folder:
        return
    while True:
        print(f"\n[bold cyan]{t('meta_title')}[/bold cyan]")
        print(f"[dim]{t('current_folder')}:[/dim] {CURRENT_FOLDER}\n")
        print("1) "+t("artist_track"))
        print("2) "+t("tracknum_artist_track"))
        print("3) "+t("all_title"))
        print("4) "+t("dry_run"))
        print("5) "+t("change_folder"))
        print("6) "+t("settings"))
        print("0) "+t("exit"))
        choice = Prompt.ask("Choice", choices=["1","2","3","4","5","6","0"])
        if choice == "0":
            break
        if choice == "5":
            folder = ask_folder()
            continue
        if choice == "6":
            settings_menu()
            continue
        if choice == "4":
            SETTINGS["write"] = False
            scan(CURRENT_FOLDER, mode="basic")
            SETTINGS["write"] = True
            continue
        if not Confirm.ask(t("continue")):
            continue
        if choice == "1":
            scan(CURRENT_FOLDER, mode="basic")
        elif choice == "2":
            scan(CURRENT_FOLDER, mode="tracknum")
        elif choice == "3":
            scan(CURRENT_FOLDER, title_only=True)

# ================= MAIN =================
if __name__ == "__main__":
    try:
        main_menu()
    except Exception as e:
        print(f"[red]Ошибка:[/red] {e}")
    input("\n"+t("press_enter"))
