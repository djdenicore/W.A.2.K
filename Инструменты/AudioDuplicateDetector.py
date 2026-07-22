#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Audio Duplicate Detector v4.2
Author: DJ Denicore
Professional tool for finding duplicate audio tracks.
"""

import sys
import os
import re
import json
import time
import hashlib
import subprocess
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any, Set
from collections import defaultdict
from pathlib import Path
from datetime import datetime
import signal

# =============================================================================
# GUI and Rich imports
# =============================================================================
try:
    import tkinter as tk
    from tkinter import filedialog
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm
    from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn, SpinnerColumn
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

try:
    import mutagen
    from mutagen import File
    from mutagen.easyid3 import EasyID3
    from mutagen.id3 import ID3, APIC
    from mutagen.flac import FLAC, Picture
    from mutagen.mp4 import MP4
    MUTAGEN_AVAILABLE = True
except ImportError:
    MUTAGEN_AVAILABLE = False

# =============================================================================
# Constants
# =============================================================================
APP_NAME = "Audio Duplicate Detector"
APP_VERSION = "4.2"
CONFIG_FILE = Path.home() / ".audio_duplicate_detector_config.json"

SUPPORTED_EXT = ('.mp3', '.flac', '.m4a', '.aac', '.ogg', '.opus', '.wav', '.aiff', '.wma', '.ape', '.dsf', '.dff')

WEIGHTS = {
    'artist_exact': 40,
    'artist_partial': 25,
    'title_exact': 40,
    'title_partial': 25,
    'duration_exact': 15,
    'duration_close': 10,
    'duration_far': 5,
    'album': 5,
    'bpm': 5,
    'cover': 3,
    'codec': 2,
    'fingerprint': 15,
}

# =============================================================================
# Settings
# =============================================================================
class Settings:
    def __init__(self):
        self.language = 'en'
        self.recursive = True
        self.dry_run = False
        self.auto_confirm = False
        self.keep_strategy = 'auto'
        self.scan_mode = 'smart'
        self.show_progress = True
        self.ignore_small_files = True
        self.min_file_size_mb = 1
        self.export_report = False
        self.report_format = 'html'
        self.last_folder = ''
        self.load()

    def load(self):
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for key, value in data.items():
                        if hasattr(self, key):
                            setattr(self, key, value)
            except:
                pass

    def save(self):
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.__dict__, f, indent=2, ensure_ascii=False)
        except:
            pass

# =============================================================================
# Localization
# =============================================================================
TRANSLATIONS = {
    'en': {
        'app_title': f"{APP_NAME} v{APP_VERSION}",
        'menu_scan': 'Scan for duplicates',
        'menu_toggle_dryrun': 'Toggle Dry-Run',
        'menu_change_folder': 'Change Folder',
        'menu_toggle_mode': 'Toggle Scan Mode',
        'menu_settings': 'Settings',
        'menu_about': 'About',
        'menu_exit': 'Exit',
        'settings_title': 'SETTINGS',
        'setting_language': 'Language',
        'setting_recursive': 'Scan subfolders recursively',
        'setting_dry_run': 'Dry-run (no actual deletion)',
        'setting_auto_confirm': 'Auto-confirm deletion',
        'setting_keep_strategy': 'Keep strategy',
        'setting_scan_mode': 'Scan mode',
        'setting_show_progress': 'Show progress bar',
        'setting_ignore_small': 'Ignore files < 1MB',
        'setting_export_report': 'Export report after scan',
        'setting_report_format': 'Report format',
        'back': 'Back',
        'select_folder': 'Select folder with audio files',
        'folder_not_selected': 'Folder not selected.',
        'current_folder': 'Folder',
        'folder_not_found': 'Folder not found',
        'no_files': 'No supported audio files found',
        'scanning': 'Scanning files...',
        'files_found': 'Files found',
        'duplicates_found': 'Duplicate groups found',
        'duplicates_total': 'Total duplicate files (to be removed)',
        'group_list_title': 'Duplicate groups',
        'group_info': 'Group #{idx}: {count} files (score: {score}%)',
        'reasons': 'Reasons',
        'best_file': 'Best file',
        'keep_strategy_auto': 'Auto: keep best quality',
        'keep_strategy_first': 'Keep first file',
        'keep_strategy_manual': 'Manual selection',
        'choose_keep': 'Which file to keep? (1-{count}, 0=skip group)',
        'confirm_delete': 'Delete all duplicates (except kept files)?',
        'deleting': 'Deleting duplicates...',
        'deletion_complete': 'Deletion complete!',
        'stats_total_groups': 'Total groups',
        'stats_files_kept': 'Files kept',
        'stats_files_deleted': 'Files deleted',
        'stats_errors': 'Errors',
        'stats_time': 'Time elapsed',
        'log_file': 'Log file',
        'dry_run_mode': 'DRY-RUN MODE - no files will be deleted',
        'cancel': 'Cancel',
        'about_version': f'Version {APP_VERSION}',
        'about_desc': 'Find and remove duplicate audio files using intelligent scoring.',
        'about_features': 'Features',
        'about_tech': 'Technologies',
        'yes': 'Yes',
        'no': 'No',
        'enter_choice': 'Enter your choice',
        'press_enter': 'Press Enter to continue...',
        'error_reading': 'Could not read metadata',
        'success': 'Success',
        'warning': 'Warning',
        'error': 'Error',
        'keep_strategy': 'Keep strategy',
        'strategy_auto': 'Auto (best quality)',
        'strategy_first': 'First encountered',
        'strategy_manual': 'Manual',
        'scan_mode': 'Scan mode',
        'mode_fast': 'Fast (artist + title + duration)',
        'mode_smart': 'Smart (+ BPM, cover)',
        'mode_deep': 'Deep (+ fingerprint, codec, album)',
        'strategy_now': 'Strategy',
        'mode_now': 'Scan mode',
        'drag_drop_detected': 'Drag & Drop detected',
        'goodbye': 'Goodbye!',
        'status_write_on': 'ON (Changes will be saved)',
        'status_write_off': 'OFF (Dry-Run mode, no changes)',
        'write_mode_lbl': 'Write Mode',
        'folder_required': 'Please select a folder first',
        'continue': 'Continue?',
        'report_exported': 'Report exported to',
        'report_format_html': 'HTML',
        'report_format_json': 'JSON',
        'report_format_csv': 'CSV',
        'enter_path': 'Enter path (or drag folder)',
        'scan_this_folder': 'Scan this folder?',
        'no_duplicates_found': 'No duplicates found.',
        'folder_set': 'Folder set',
        'reading_files': 'Reading files...',
        'clustering': 'Clustering...',
        'estimated_space_saved': 'Estimated space saved',
        'space_saved': 'Space saved',
        'quality_score': 'Quality score',
        'bit_depth': 'Bit depth',
        'lossless': 'Lossless',
        'lossy': 'Lossy',
        'cover_art': 'Cover art',
        'tags_count': 'Tags count',
        'scan_duration': 'Scan duration',
        'deletion_cancelled': 'Deletion cancelled.',
        'error_ffprobe': 'ffprobe not found, using Mutagen.',
    },
    'ru': {
        'app_title': f"{APP_NAME} v{APP_VERSION}",
        'menu_scan': 'Поиск дубликатов',
        'menu_toggle_dryrun': 'Переключить Dry-Run',
        'menu_change_folder': 'Сменить папку',
        'menu_toggle_mode': 'Переключить режим сканирования',
        'menu_settings': 'Настройки',
        'menu_about': 'О программе',
        'menu_exit': 'Выход',
        'settings_title': 'НАСТРОЙКИ',
        'setting_language': 'Язык',
        'setting_recursive': 'Сканировать подпапки рекурсивно',
        'setting_dry_run': 'Пробный запуск (без реального удаления)',
        'setting_auto_confirm': 'Автоподтверждение удаления',
        'setting_keep_strategy': 'Стратегия сохранения',
        'setting_scan_mode': 'Режим сканирования',
        'setting_show_progress': 'Показывать прогресс-бар',
        'setting_ignore_small': 'Игнорировать файлы < 1MB',
        'setting_export_report': 'Экспортировать отчёт после сканирования',
        'setting_report_format': 'Формат отчёта',
        'back': 'Назад',
        'select_folder': 'Выберите папку с аудиофайлами',
        'folder_not_selected': 'Папка не выбрана.',
        'current_folder': 'Папка',
        'folder_not_found': 'Папка не найдена',
        'no_files': 'Не найдено поддерживаемых аудиофайлов',
        'scanning': 'Сканирование файлов...',
        'files_found': 'Найдено файлов',
        'duplicates_found': 'Найдено групп дубликатов',
        'duplicates_total': 'Всего дубликатов (будут удалены)',
        'group_list_title': 'Группы дубликатов',
        'group_info': 'Группа #{idx}: {count} файлов (оценка: {score}%)',
        'reasons': 'Причины',
        'best_file': 'Лучший файл',
        'keep_strategy_auto': 'Авто: оставить лучшее качество',
        'keep_strategy_first': 'Оставить первый файл',
        'keep_strategy_manual': 'Ручной выбор',
        'choose_keep': 'Какой файл оставить? (1-{count}, 0=пропустить группу)',
        'confirm_delete': 'Удалить все дубликаты (кроме сохранённых)?',
        'deleting': 'Удаление дубликатов...',
        'deletion_complete': 'Удаление завершено!',
        'stats_total_groups': 'Всего групп',
        'stats_files_kept': 'Файлов сохранено',
        'stats_files_deleted': 'Файлов удалено',
        'stats_errors': 'Ошибок',
        'stats_time': 'Затрачено времени',
        'log_file': 'Лог-файл',
        'dry_run_mode': 'РЕЖИМ ПРОБНОГО ЗАПУСКА - изменения не будут записаны',
        'cancel': 'Отмена',
        'about_version': f'Версия {APP_VERSION}',
        'about_desc': 'Поиск и удаление дублирующихся аудиофайлов с интеллектуальной системой оценки.',
        'about_features': 'Возможности',
        'about_tech': 'Технологии',
        'yes': 'Да',
        'no': 'Нет',
        'enter_choice': 'Выберите вариант',
        'press_enter': 'Нажмите Enter для продолжения...',
        'error_reading': 'Не удалось прочитать метаданные',
        'success': 'Успешно',
        'warning': 'Предупреждение',
        'error': 'Ошибка',
        'keep_strategy': 'Стратегия сохранения',
        'strategy_auto': 'Авто (лучшее качество)',
        'strategy_first': 'Первый попавшийся',
        'strategy_manual': 'Вручную',
        'scan_mode': 'Режим сканирования',
        'mode_fast': 'Быстрый (исполнитель + название + длительность)',
        'mode_smart': 'Умный (+ BPM, обложка)',
        'mode_deep': 'Глубокий (+ отпечаток, кодек, альбом)',
        'strategy_now': 'Стратегия',
        'mode_now': 'Режим сканирования',
        'drag_drop_detected': 'Обнаружено перетаскивание',
        'goodbye': 'До свидания!',
        'status_write_on': 'ВКЛЮЧЕНА (Изменения сохранятся)',
        'status_write_off': 'ВЫКЛЮЧЕНА (Dry-Run, только просмотр)',
        'write_mode_lbl': 'Запись',
        'folder_required': 'Пожалуйста, сначала выберите папку',
        'continue': 'Начать обработку?',
        'report_exported': 'Отчёт экспортирован в',
        'report_format_html': 'HTML',
        'report_format_json': 'JSON',
        'report_format_csv': 'CSV',
        'enter_path': 'Введите путь (или перетащите папку)',
        'scan_this_folder': 'Сканировать эту папку?',
        'no_duplicates_found': 'Дубликатов не найдено.',
        'folder_set': 'Папка установлена',
        'reading_files': 'Чтение файлов...',
        'clustering': 'Кластеризация...',
        'estimated_space_saved': 'Предполагаемое освобождение места',
        'space_saved': 'Освобождено места',
        'quality_score': 'Оценка качества',
        'bit_depth': 'Битность',
        'lossless': 'Без потерь',
        'lossy': 'С потерями',
        'cover_art': 'Обложка',
        'tags_count': 'Количество тегов',
        'scan_duration': 'Длительность сканирования',
        'deletion_cancelled': 'Удаление отменено.',
        'error_ffprobe': 'ffprobe не найден, используется Mutagen.',
    }
}

class Locale:
    def __init__(self, lang='en'):
        self.lang = lang
    def t(self, key):
        return TRANSLATIONS.get(self.lang, TRANSLATIONS['en']).get(key, key)

# =============================================================================
# Data Models
# =============================================================================
class ScanMode(Enum):
    FAST = 'fast'
    SMART = 'smart'
    DEEP = 'deep'

@dataclass
class AudioInfo:
    path: str
    filename: str
    artist_raw: str = ''
    title_raw: str = ''
    artist_clean: str = ''
    title_clean: str = ''
    album: str = ''
    track: str = ''
    duration: float = 0.0
    bitrate: int = 0
    sample_rate: int = 0
    codec: str = ''
    size: int = 0
    has_cover: bool = False
    bpm: Optional[float] = None
    key: Optional[str] = None
    replaygain: Optional[float] = None
    tags_count: int = 0
    fingerprint: str = ''
    normalized_artist: str = ''
    normalized_title: str = ''
    quality_score: float = 0.0
    bit_depth: int = 0

@dataclass
class MatchScore:
    score: int
    reasons: List[str] = field(default_factory=list)
    is_duplicate: bool = False

@dataclass
class DuplicateGroup:
    files: List[AudioInfo]
    score: int
    reasons: List[str]
    best_file: Optional[AudioInfo] = None
    quality_rank: List[AudioInfo] = field(default_factory=list)
    space_saved: int = 0

# =============================================================================
# Audio Reader Module
# =============================================================================
class AudioReader:
    _ffprobe_warned = False

    @staticmethod
    def read(filepath: str, deep: bool = False) -> Optional[AudioInfo]:
        try:
            info = AudioInfo(
                path=filepath,
                filename=os.path.basename(filepath),
                size=os.path.getsize(filepath)
            )

            # Try ffprobe first
            try:
                cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams', filepath]
                res = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=10)
                if res.returncode == 0:
                    data = json.loads(res.stdout)
                    stream = next((s for s in data.get('streams', []) if s.get('codec_type') == 'audio'), None)
                    if stream:
                        info.duration = float(stream.get('duration', 0))
                        info.bitrate = int(stream.get('bit_rate', 0))
                        info.sample_rate = int(stream.get('sample_rate', 0))
                        info.codec = stream.get('codec_name', '')
                        info.bit_depth = int(stream.get('bits_per_sample', 0))
                    fmt = data.get('format', {})
                    tags = fmt.get('tags', {})
                    info.artist_raw = tags.get('artist', '')
                    info.title_raw = tags.get('title', '')
                    info.album = tags.get('album', '')
                    info.track = tags.get('track', '')
            except Exception:
                if not AudioReader._ffprobe_warned:
                    AudioReader._ffprobe_warned = True

            # Если ffprobe не дал тегов или не отработал, используем mutagen
            if MUTAGEN_AVAILABLE and (not info.artist_raw or not info.title_raw):
                try:
                    audio = mutagen.File(filepath)
                    if audio:
                        if hasattr(audio.info, 'length'):
                            info.duration = audio.info.length
                        if hasattr(audio.info, 'bitrate'):
                            info.bitrate = audio.info.bitrate
                        if hasattr(audio.info, 'sample_rate'):
                            info.sample_rate = audio.info.sample_rate
                        if hasattr(audio.info, 'bits_per_sample'):
                            info.bit_depth = audio.info.bits_per_sample
                        elif hasattr(audio.info, 'bits_per_raw_sample'):
                            info.bit_depth = audio.info.bits_per_raw_sample
                        tags = {}
                        if hasattr(audio, 'tags') and audio.tags:
                            tags = audio.tags
                        elif hasattr(audio, 'get'):
                            try:
                                tags = EasyID3(filepath)
                            except:
                                pass
                        if tags:
                            info.artist_raw = AudioReader._get_tag(tags, ['TPE1', 'artist', '©ART'])
                            info.title_raw = AudioReader._get_tag(tags, ['TIT2', 'title', '©nam'])
                            info.album = AudioReader._get_tag(tags, ['TALB', 'album', '©alb'])
                            info.track = AudioReader._get_tag(tags, ['TRCK', 'tracknumber', 'trck'])
                except Exception:
                    pass

            # Cover detection
            info.has_cover = AudioReader._has_cover(filepath)

            # Deep scan extras
            if deep:
                info.bpm = AudioReader._extract_bpm(filepath)
                info.key = AudioReader._extract_key(filepath)
                info.replaygain = AudioReader._extract_replaygain(filepath)
                info.fingerprint = AudioReader._get_fingerprint(filepath)

            # Clean and normalize
            info.artist_clean = AudioReader._clean_artist(info.artist_raw)
            info.title_clean = AudioReader._clean_title(info.title_raw)
            info.normalized_artist = AudioReader._normalize_text(info.artist_clean)
            info.normalized_title = AudioReader._normalize_text(info.title_clean)

            # Fallback to filename if needed
            if not info.artist_clean or not info.title_clean:
                artist_from_file, title_from_file = AudioReader._parse_filename(info.filename)
                if not info.artist_clean:
                    info.artist_clean = artist_from_file
                    info.normalized_artist = AudioReader._normalize_text(artist_from_file)
                if not info.title_clean:
                    info.title_clean = title_from_file
                    info.normalized_title = AudioReader._normalize_text(title_from_file)
                if not info.title_clean:
                    info.title_clean = os.path.splitext(info.filename)[0]
                    info.normalized_title = AudioReader._normalize_text(info.title_clean)

            if not info.artist_clean and info.album:
                info.artist_clean = info.album
                info.normalized_artist = AudioReader._normalize_text(info.album)

            info.tags_count = sum(1 for x in [info.artist_raw, info.title_raw, info.album, info.track] if x)
            info.quality_score = AudioReader._calculate_quality(info)
            return info
        except Exception:
            # Fallback: извлекаем только из имени файла
            try:
                info = AudioInfo(
                    path=filepath,
                    filename=os.path.basename(filepath),
                    size=os.path.getsize(filepath)
                )
                artist, title = AudioReader._parse_filename(info.filename)
                info.artist_clean = artist
                info.title_clean = title if title else os.path.splitext(info.filename)[0]
                info.normalized_artist = AudioReader._normalize_text(info.artist_clean)
                info.normalized_title = AudioReader._normalize_text(info.title_clean)
                info.quality_score = 0.0
                return info
            except:
                return None

    @staticmethod
    def _calculate_quality(info: AudioInfo) -> float:
        score = 0.0
        if info.bitrate > 0:
            score += min(info.bitrate / 320000, 1.0) * 0.5
        lossless_codecs = {'flac', 'pcm', 'aiff', 'alac', 'wav'}
        if info.codec.lower() in lossless_codecs:
            score += 0.2
        if info.sample_rate > 0:
            score += min(info.sample_rate / 192000, 1.0) * 0.1
        if info.has_cover:
            score += 0.1
        score += min(info.tags_count / 4, 1.0) * 0.1
        return min(score, 1.0)

    @staticmethod
    def _get_tag(tags, keys):
        for key in keys:
            val = tags.get(key)
            if val:
                if isinstance(val, list):
                    return str(val[0])
                return str(val)
        return ''

    @staticmethod
    def _has_cover(filepath: str) -> bool:
        ext = os.path.splitext(filepath)[1].lower()
        try:
            if ext == '.mp3':
                audio = ID3(filepath)
                return len(audio.getall('APIC')) > 0
            elif ext == '.flac':
                audio = FLAC(filepath)
                return len(audio.pictures) > 0
            elif ext in ['.m4a', '.aac']:
                audio = MP4(filepath)
                return 'covr' in audio
        except:
            pass
        return False

    @staticmethod
    def _clean_artist(text: str) -> str:
        if not text:
            return ''
        patterns = [
            (r'\s+feat\.?\s+', ' '),
            (r'\s+ft\.?\s+', ' '),
            (r'\s+featuring\s+', ' '),
            (r'\s+vs\.?\s+', ' '),
            (r'\s+&\s+', ' '),
            (r'\s+x\s+', ' '),
            (r'\s+present(s)?\s+', ' '),
            (r'\s+pres\.?\s+', ' '),
            (r'\s+with\s+', ' '),
        ]
        for pat, repl in patterns:
            text = re.sub(pat, repl, text, flags=re.IGNORECASE)
        return text.strip()

    @staticmethod
    def _clean_title(text: str) -> str:
        """
        Очищает название, НО НЕ УДАЛЯЕТ информацию о миксе (Extended, Back To Basics и т.п.)
        Удаляет только год в скобках, [hq], [hd], remaster и явные суффиксы после дефиса.
        """
        if not text:
            return ''
        patterns = [
            (r'\s*\([^)]*\d{4}[^)]*\)\s*', ''),        # (2023)
            (r'\s*\[[^\]]*hq[^\]]*\]\s*', ''),        # [hq]
            (r'\s*\[[^\]]*hd[^\]]*\]\s*', ''),        # [hd]
            (r'\s*\([^)]*remaster[^)]*\)\s*', ''),    # (remaster)
            (r'\s*-\s*[Rr]emix$', ''),                # - Remix в конце (оставляем, если в скобках)
            (r'\s*-\s*[Rr]emaster$', ''),             # - Remaster
            (r'\s*-\s*[Vv]ersion$', ''),              # - Version
            (r'\s*-\s*[Ee]dit$', ''),                 # - Edit
        ]
        for pat, repl in patterns:
            text = re.sub(pat, repl, text, flags=re.IGNORECASE)
        return text.strip()

    @staticmethod
    def _normalize_text(text: str) -> str:
        if not text:
            return ''
        text = text.lower()
        import unicodedata
        text = unicodedata.normalize('NFKC', text)
        text = re.sub(r'[^a-z0-9\s]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    @staticmethod
    def _parse_filename(filename: str) -> Tuple[str, str]:
        """
        Извлекает исполнителя и название из имени файла.
        НЕ УДАЛЯЕТ скобки с миксом – они остаются в названии.
        """
        name = os.path.splitext(filename)[0]
        # Удаляем номер трека в начале
        name = re.sub(r'^\s*\d+\s*[\.\-_\s]\s*', '', name)
        name = re.sub(r'_\d+$', '', name)          # суффикс _1, _2 и т.п.
        name = re.sub(r'\s+_copy$', '', name, flags=re.IGNORECASE)
        # Ищем разделитель " - "
        separators = [' - ', ' – ', ' — ', ' | ', ' _ ', ' . ']
        for sep in separators:
            if sep in name:
                parts = name.split(sep, 1)
                if len(parts) == 2:
                    artist = parts[0].strip()
                    title = parts[1].strip()
                    # НЕ удаляем скобки в конце – оставляем информацию о миксе
                    return artist, title
        # Если разделитель не найден, возвращаем всё как название
        return '', name.strip()

    @staticmethod
    def _extract_bpm(filepath: str) -> Optional[float]:
        try:
            audio = mutagen.File(filepath)
            if audio and hasattr(audio, 'tags') and audio.tags:
                bpm_tag = audio.tags.get('TBPM')
                if bpm_tag:
                    return float(bpm_tag[0])
                if hasattr(audio, 'get'):
                    bpm = audio.get('tmpo')
                    if bpm:
                        return float(bpm[0])
        except:
            pass
        return None

    @staticmethod
    def _extract_key(filepath: str) -> Optional[str]:
        return None

    @staticmethod
    def _extract_replaygain(filepath: str) -> Optional[float]:
        return None

    @staticmethod
    def _get_fingerprint(filepath: str) -> str:
        try:
            with open(filepath, 'rb') as f:
                data = f.read(65536)
                return hashlib.md5(data).hexdigest()[:16]
        except:
            return ''

# =============================================================================
# Similarity Scorer Module
# =============================================================================
class SimilarityScorer:
    @staticmethod
    def compare(a: AudioInfo, b: AudioInfo, mode: ScanMode) -> MatchScore:
        score = 0
        reasons = []

        artist_score = SimilarityScorer._compare_artist(a, b)
        score += artist_score
        if artist_score >= 30:
            reasons.append(f"Artist совпадает ({artist_score})")

        title_score = SimilarityScorer._compare_title(a, b)
        score += title_score
        if title_score >= 30:
            reasons.append(f"Title совпадает ({title_score})")

        dur_score = SimilarityScorer._compare_duration(a, b)
        score += dur_score
        if dur_score >= 10:
            reasons.append(f"Duration совпадает (±{abs(a.duration - b.duration):.1f} сек)")

        if mode == ScanMode.DEEP:
            album_score = SimilarityScorer._compare_album(a, b)
            score += album_score
            if album_score >= 5:
                reasons.append("Альбом совпадает")

        if mode in (ScanMode.SMART, ScanMode.DEEP) and a.bpm is not None and b.bpm is not None:
            bpm_score = SimilarityScorer._compare_bpm(a, b)
            score += bpm_score
            if bpm_score >= 5:
                reasons.append("BPM совпадает")

        if mode in (ScanMode.SMART, ScanMode.DEEP):
            cover_score = SimilarityScorer._compare_cover(a, b)
            score += cover_score
            if cover_score >= 3:
                reasons.append("Обложка совпадает")

        if mode == ScanMode.DEEP:
            codec_score = SimilarityScorer._compare_codec(a, b)
            score += codec_score
            if codec_score >= 2:
                reasons.append("Кодек совпадает")

        if mode == ScanMode.DEEP and a.fingerprint and b.fingerprint:
            if a.fingerprint == b.fingerprint:
                score += 15
                reasons.append("Fingerprint совпадает (+15)")

        final_score = min(100, score)
        is_dup = final_score >= 65
        return MatchScore(score=final_score, reasons=reasons, is_duplicate=is_dup)

    @staticmethod
    def _compare_artist(a: AudioInfo, b: AudioInfo) -> int:
        if a.normalized_artist == b.normalized_artist:
            return WEIGHTS['artist_exact']
        if a.normalized_artist and b.normalized_artist:
            if a.normalized_artist in b.normalized_artist or b.normalized_artist in a.normalized_artist:
                return WEIGHTS['artist_partial']
        return 0

    @staticmethod
    def _compare_title(a: AudioInfo, b: AudioInfo) -> int:
        if a.normalized_title == b.normalized_title:
            return WEIGHTS['title_exact']
        if a.normalized_title and b.normalized_title:
            if a.normalized_title in b.normalized_title or b.normalized_title in a.normalized_title:
                return WEIGHTS['title_partial']
        return 0

    @staticmethod
    def _compare_duration(a: AudioInfo, b: AudioInfo) -> int:
        diff = abs(a.duration - b.duration)
        if diff <= 2.0:
            return WEIGHTS['duration_exact']
        elif diff <= 5.0:
            return WEIGHTS['duration_close']
        elif diff <= 10.0:
            return WEIGHTS['duration_far']
        return 0

    @staticmethod
    def _compare_album(a: AudioInfo, b: AudioInfo) -> int:
        if a.album and b.album and a.album.lower() == b.album.lower():
            return WEIGHTS['album']
        return 0

    @staticmethod
    def _compare_bpm(a: AudioInfo, b: AudioInfo) -> int:
        if a.bpm and b.bpm and abs(a.bpm - b.bpm) <= 1.0:
            return WEIGHTS['bpm']
        return 0

    @staticmethod
    def _compare_cover(a: AudioInfo, b: AudioInfo) -> int:
        if a.has_cover == b.has_cover and a.has_cover:
            return WEIGHTS['cover']
        return 0

    @staticmethod
    def _compare_codec(a: AudioInfo, b: AudioInfo) -> int:
        if a.codec and b.codec and a.codec == b.codec:
            return WEIGHTS['codec']
        return 0

# =============================================================================
# Duplicate Detector Engine (Multi-stage)
# =============================================================================
class DuplicateDetector:
    def __init__(self, settings: Settings, locale: Locale, console: Console):
        self.settings = settings
        self.locale = locale
        self.console = console
        self.files: List[AudioInfo] = []
        self.groups: List[DuplicateGroup] = []
        self.scan_time = 0.0
        self.total_space_saved = 0

    def scan(self, folder: str, mode: ScanMode):
        start_time = time.time()
        paths = []
        if self.settings.recursive:
            for root, _, files in os.walk(folder):
                for f in files:
                    if f.lower().endswith(SUPPORTED_EXT):
                        full = os.path.join(root, f)
                        if self.settings.ignore_small_files and os.path.getsize(full) < 1024 * 1024 * self.settings.min_file_size_mb:
                            continue
                        paths.append(full)
        else:
            for f in os.listdir(folder):
                full = os.path.join(folder, f)
                if os.path.isfile(full):
                    if f.lower().endswith(SUPPORTED_EXT):
                        if self.settings.ignore_small_files and os.path.getsize(full) < 1024 * 1024 * self.settings.min_file_size_mb:
                            continue
                        paths.append(full)

        if not paths:
            self.console.print(f"[yellow]{self.locale.t('no_files')}[/yellow]")
            return

        self.console.print(f"[bold]{self.locale.t('scanning')}[/bold]")
        deep = (mode == ScanMode.DEEP)
        self.files = []
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=self.console,
            disable=not self.settings.show_progress
        ) as progress:
            task = progress.add_task(f"{self.locale.t('reading_files')} ({len(paths)})", total=len(paths))
            for path in paths:
                info = AudioReader.read(path, deep)
                if info:
                    self.files.append(info)
                progress.advance(task)

        self.console.print(f"[green]{self.locale.t('files_found')}: {len(self.files)}[/green]")
        self._cluster(mode)
        self.scan_time = time.time() - start_time

    def _cluster(self, mode: ScanMode):
        artist_groups = defaultdict(list)
        for info in self.files:
            if info.normalized_artist:
                artist_groups[info.normalized_artist].append(info)
            else:
                artist_groups[''].append(info)

        title_groups = defaultdict(list)
        for artist, files in artist_groups.items():
            for info in files:
                key = (artist, info.normalized_title)
                title_groups[key].append(info)

        self.groups = []
        used = set()
        total = len(self.files)
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=self.console,
            disable=not self.settings.show_progress
        ) as progress:
            task = progress.add_task(self.locale.t('clustering'), total=total)
            for (artist, title), candidates in title_groups.items():
                if len(candidates) < 2:
                    continue
                used_here = set()
                for i, file_a in enumerate(candidates):
                    if i in used_here:
                        continue
                    group_files = [file_a]
                    group_reasons = set()
                    for j, file_b in enumerate(candidates):
                        if j <= i or j in used_here:
                            continue
                        score = SimilarityScorer.compare(file_a, file_b, mode)
                        if score.is_duplicate:
                            group_files.append(file_b)
                            used_here.add(j)
                            group_reasons.update(score.reasons)
                    if len(group_files) > 1:
                        sorted_files = self._sort_by_quality(group_files)
                        best = sorted_files[0]
                        avg_score = sum(SimilarityScorer.compare(file_a, f, mode).score for f in group_files[1:]) // (len(group_files)-1) if len(group_files)>1 else 100
                        space_saved = sum(f.size for f in group_files[1:])
                        self.groups.append(DuplicateGroup(
                            files=group_files,
                            score=avg_score,
                            reasons=list(group_reasons),
                            best_file=best,
                            quality_rank=sorted_files,
                            space_saved=space_saved
                        ))
                        used_here.add(i)
                progress.advance(task, len(candidates))

        self.total_space_saved = sum(g.space_saved for g in self.groups)

    def _sort_by_quality(self, files: List[AudioInfo]) -> List[AudioInfo]:
        def key_func(f):
            return (f.quality_score, f.bitrate, 1 if f.has_cover else 0, f.tags_count, f.size)
        return sorted(files, key=key_func, reverse=True)

    def get_groups(self) -> List[DuplicateGroup]:
        return self.groups

    def export_report(self, folder: str, format: str = 'html') -> str:
        if not self.groups:
            return ''
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if format == 'html':
            filename = os.path.join(folder, f"duplicate_report_{timestamp}.html")
            self._export_html(filename)
        elif format == 'json':
            filename = os.path.join(folder, f"duplicate_report_{timestamp}.json")
            self._export_json(filename)
        elif format == 'csv':
            filename = os.path.join(folder, f"duplicate_report_{timestamp}.csv")
            self._export_csv(filename)
        else:
            filename = ''
        return filename

    def _export_html(self, filename: str):
        html = f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>Duplicate Report</title>
<style>
body {{ font-family: Arial; margin: 20px; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
th {{ background-color: #f2f2f2; }}
tr:nth-child(even) {{ background-color: #f9f9f9; }}
.highlight {{ background-color: #ffffcc; }}
.stats {{ margin-bottom: 20px; }}
.stats span {{ font-weight: bold; }}
</style>
</head>
<body>
<h1>Duplicate Audio Report</h1>
<div class="stats">
<p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
<p>Total groups: <span>{len(self.groups)}</span></p>
<p>Total duplicates: <span>{sum(len(g.files)-1 for g in self.groups)}</span></p>
<p>Space saved: <span>{self._format_size(self.total_space_saved)}</span></p>
<p>Scan duration: <span>{self.scan_time:.1f}s</span></p>
</div>
"""
        for idx, group in enumerate(self.groups, 1):
            html += f"<h2>Group #{idx} (Score: {group.score}%, Space saved: {self._format_size(group.space_saved)})</h2>"
            html += "<table><tr><th>#</th><th>File</th><th>Artist</th><th>Title</th><th>Codec</th><th>Bitrate</th><th>Cover</th><th>Quality</th><th>Size</th></tr>"
            for i, f in enumerate(group.files, 1):
                cover = "✓" if f.has_cover else "✗"
                cls = 'class="highlight"' if f == group.best_file else ''
                html += f"<tr {cls}><td>{i}</td><td>{f.filename}</td><td>{f.artist_clean}</td><td>{f.title_clean}</td><td>{f.codec}</td><td>{f.bitrate//1000 if f.bitrate else '?'} kbps</td><td>{cover}</td><td>{f.quality_score:.2f}</td><td>{self._format_size(f.size)}</td></tr>"
            html += "</table>"
            if group.reasons:
                html += f"<p><strong>Reasons:</strong> {', '.join(group.reasons)}</p>"
        html += "</body></html>"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)

    def _export_json(self, filename: str):
        data = {
            'scan_time': self.scan_time,
            'total_groups': len(self.groups),
            'total_duplicates': sum(len(g.files)-1 for g in self.groups),
            'space_saved': self.total_space_saved,
            'groups': []
        }
        for group in self.groups:
            data['groups'].append({
                'score': group.score,
                'reasons': group.reasons,
                'space_saved': group.space_saved,
                'files': [{
                    'filename': f.filename,
                    'artist': f.artist_clean,
                    'title': f.title_clean,
                    'codec': f.codec,
                    'bitrate': f.bitrate,
                    'has_cover': f.has_cover,
                    'quality_score': f.quality_score,
                    'size': f.size,
                    'is_best': f == group.best_file
                } for f in group.files]
            })
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _export_csv(self, filename: str):
        import csv
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Group', 'Score', 'File', 'Artist', 'Title', 'Codec', 'Bitrate', 'Cover', 'Quality', 'Size', 'IsBest'])
            for gi, group in enumerate(self.groups, 1):
                for fi, file in enumerate(group.files):
                    writer.writerow([
                        gi,
                        group.score,
                        file.filename,
                        file.artist_clean,
                        file.title_clean,
                        file.codec,
                        file.bitrate,
                        'Yes' if file.has_cover else 'No',
                        f"{file.quality_score:.2f}",
                        file.size,
                        'Yes' if file == group.best_file else 'No'
                    ])

    @staticmethod
    def _format_size(size_bytes):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

# =============================================================================
# Application
# =============================================================================
class Application:
    _root = None

    def __init__(self):
        self.settings = Settings()
        self.locale = Locale(self.settings.language)
        self.console = Console() if RICH_AVAILABLE else None
        self.folder = self.settings.last_folder if self.settings.last_folder else None
        self.detector = None
        self.groups = []
        self._setup_signal_handler()

    def _setup_signal_handler(self):
        try:
            signal.signal(signal.SIGINT, self._signal_handler)
        except:
            pass

    def _signal_handler(self, signum, frame):
        print("\n\n[yellow]Operation cancelled by user.[/yellow]")
        sys.exit(0)

    def _clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def _prompt_choice(self, prompt, choices, default=None):
        if self.console:
            return Prompt.ask(prompt, choices=choices, default=default)
        else:
            while True:
                print(f"{prompt} ({'/'.join(choices)})", end=' ')
                ans = input().strip()
                if ans in choices:
                    return ans
                print("Invalid choice")

    def _confirm(self, prompt, default=True):
        if self.settings.auto_confirm:
            return default
        if self.console:
            return Confirm.ask(prompt, default=default)
        else:
            ans = input(f"{prompt} (Y/n): ").strip().lower()
            return ans in ('', 'y', 'yes')

    def _select_folder_gui(self):
        if TKINTER_AVAILABLE:
            try:
                if Application._root is None:
                    Application._root = tk.Tk()
                    Application._root.withdraw()
                    Application._root.attributes('-topmost', True)
                else:
                    Application._root.deiconify()
                    Application._root.lift()
                    Application._root.focus_force()
                Application._root.update()
                folder = filedialog.askdirectory(parent=Application._root, title=self.locale.t('select_folder'))
                Application._root.withdraw()
                return folder
            except Exception as e:
                if self.console:
                    self.console.print(f"[yellow]GUI folder selection failed: {e}. Using manual input.[/yellow]")
                return None
        return None

    def _get_folder(self):
        folder = self._select_folder_gui()
        if folder:
            return folder
        if self.console:
            self.console.print(f"\n{self.locale.t('enter_path')}:")
            self.console.print(f"({self.locale.t('cancel')}: leave empty)")
        else:
            print(f"\n{self.locale.t('enter_path')}:")
            print(f"({self.locale.t('cancel')}: leave empty)")
        path = input("> ").strip()
        if not path:
            return None
        path = os.path.expanduser(path)
        if os.path.isdir(path):
            return path
        else:
            if self.console:
                self.console.print(f"[red]{self.locale.t('folder_not_found')}[/red]")
            else:
                print(f"{self.locale.t('folder_not_found')}")
            return None

    def _format_duration(self, seconds):
        if seconds < 60:
            return f"{seconds:.0f}s"
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        if mins < 60:
            return f"{mins}m {secs}s"
        hours = mins // 60
        mins = mins % 60
        return f"{hours}h {mins}m {secs}s"

    def _format_size(self, size_bytes):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

    def _press_enter(self):
        if self.console:
            self.console.print(f"\n[dim]{self.locale.t('press_enter')}[/dim]")
        else:
            print(f"\n{self.locale.t('press_enter')}")
        input()

    # ===== Улучшенный вывод групп =====
    def _display_groups(self, groups, max_groups=10):
        """Красивый вывод групп дубликатов в консоль."""
        if not groups:
            return

        if self.console and RICH_AVAILABLE:
            from rich.table import Table
            from rich import box

            for idx, group in enumerate(groups[:max_groups], 1):
                title = (f"Group #{idx} (Score: {group.score}%, "
                         f"Space saved: {self._format_size(group.space_saved)})")
                table = Table(title=title, box=box.ROUNDED,
                              show_header=True, header_style="bold cyan")
                table.add_column("#", style="dim", width=4)
                table.add_column("File", style="white", no_wrap=False)
                table.add_column("Artist", style="green")
                table.add_column("Title", style="yellow")
                table.add_column("Bitrate", justify="right")
                table.add_column("Cover", justify="center")
                table.add_column("Quality", justify="right")
                table.add_column("Size", justify="right")
                table.add_column("Best", justify="center")

                for i, f in enumerate(group.files, 1):
                    best_marker = "★" if f == group.best_file else ""
                    cover = "✓" if f.has_cover else "✗"
                    quality = f"{f.quality_score:.2f}"
                    bitrate = f"{f.bitrate//1000 if f.bitrate else '?'} kbps"
                    size = self._format_size(f.size)
                    style = "bold green" if f == group.best_file else ""
                    table.add_row(
                        str(i),
                        f.filename,
                        f.artist_clean,
                        f.title_clean,
                        bitrate,
                        cover,
                        quality,
                        size,
                        best_marker,
                        style=style
                    )

                self.console.print(table)
                if group.reasons:
                    reasons_str = ', '.join(group.reasons)
                    self.console.print(f"[dim]Reasons: {reasons_str}[/dim]")
                self.console.print("")

        else:
            # Текстовый вывод без rich
            for idx, group in enumerate(groups[:max_groups], 1):
                print(f"\nGroup #{idx} (Score: {group.score}%, Space saved: {self._format_size(group.space_saved)})")
                print(f"Best file: {group.best_file.filename if group.best_file else 'N/A'}")
                for i, f in enumerate(group.files, 1):
                    marker = "★" if f == group.best_file else " "
                    cover = "✓" if f.has_cover else "✗"
                    bitrate = f"{f.bitrate//1000 if f.bitrate else '?'} kbps"
                    print(f"  {marker} {i}. {f.filename} | {f.artist_clean} - {f.title_clean} | {bitrate} | cover: {cover} | quality: {f.quality_score:.2f}")
                if group.reasons:
                    print(f"  Reasons: {', '.join(group.reasons)}")

    # ===== Основное действие сканирования =====
    def scan_action(self):
        if not self.folder:
            if self.console:
                self.console.print(f"\n[bold]{self.locale.t('select_folder')}[/bold]")
                self.console.print("[dim]Opening folder selection dialog...[/dim]")
            else:
                print(f"\n{self.locale.t('select_folder')}")
                print("Opening folder selection dialog...")
            folder = self._get_folder()
            if not folder:
                if self.console:
                    self.console.print("[yellow]Scan cancelled.[/yellow]")
                self._press_enter()
                return
            self.folder = folder
            self.settings.last_folder = folder
            self.settings.save()
            if self.console:
                self.console.print(f"[green]{self.locale.t('folder_set')}: {self.folder}[/green]")
            else:
                print(f"{self.locale.t('folder_set')}: {self.folder}")

        mode = ScanMode(self.settings.scan_mode)
        self.detector = DuplicateDetector(self.settings, self.locale, self.console)
        self.detector.scan(self.folder, mode)
        self.groups = self.detector.get_groups()
        if not self.groups:
            if self.console:
                self.console.print("[green]" + self.locale.t('no_duplicates_found') + "[/green]")
            else:
                print(self.locale.t('no_duplicates_found'))
            self._press_enter()
            return

        total_dups = sum(len(g.files)-1 for g in self.groups)
        if self.console:
            self.console.print(f"\n[bold]{self.locale.t('duplicates_found')}: {len(self.groups)}[/bold]")
            self.console.print(f"{self.locale.t('duplicates_total')}: {total_dups}")
            self.console.print(f"{self.locale.t('space_saved')}: {self._format_size(self.detector.total_space_saved)}\n")
        else:
            print(f"\n{self.locale.t('duplicates_found')}: {len(self.groups)}")
            print(f"{self.locale.t('duplicates_total')}: {total_dups}")
            print(f"{self.locale.t('space_saved')}: {self._format_size(self.detector.total_space_saved)}\n")

        # Отображаем группы с помощью нового метода
        self._display_groups(self.groups, max_groups=10)
        if len(self.groups) > 10:
            if self.console:
                self.console.print(f"[dim]... and {len(self.groups)-10} more groups[/dim]")
            else:
                print(f"... and {len(self.groups)-10} more groups")

        if self.settings.export_report:
            report_file = self.detector.export_report(self.folder, self.settings.report_format)
            if report_file:
                if self.console:
                    self.console.print(f"[green]{self.locale.t('report_exported')}: {report_file}[/green]")
                else:
                    print(f"{self.locale.t('report_exported')}: {report_file}")

        if self._confirm(self.locale.t('confirm_delete'), default=False):
            self._run_deletion()
        else:
            if self.console:
                self.console.print("[yellow]" + self.locale.t('deletion_cancelled') + "[/yellow]")
        self._press_enter()

    def _run_deletion(self):
        log_file = os.path.join(self.folder, f"duplicate_detector_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f"Log - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Folder: {self.folder}\n")
            f.write(f"Scan mode: {self.settings.scan_mode}\n")
            f.write(f"Keep strategy: {self.settings.keep_strategy}\n")
            f.write("-"*50+"\n")

        deleted = 0
        kept = 0
        errors = 0
        start = time.time()

        for group in self.groups:
            if self.settings.keep_strategy == 'auto':
                keep_idx = 0
            elif self.settings.keep_strategy == 'first':
                keep_idx = 0
            else:  # manual
                if self.console:
                    for i, f in enumerate(group.files, 1):
                        self.console.print(f"{i}. {f.filename} | {f.artist_clean} - {f.title_clean} | {f.bitrate//1000 if f.bitrate else '?'} kbps | cover: {'✓' if f.has_cover else '✗'} | quality: {f.quality_score:.2f}")
                else:
                    for i, f in enumerate(group.files, 1):
                        print(f"{i}. {f.filename} | {f.artist_clean} - {f.title_clean} | {f.bitrate//1000 if f.bitrate else '?'} kbps")
                choice = self._prompt_choice(self.locale.t('choose_keep').format(count=len(group.files)), [str(i) for i in range(1, len(group.files)+1)] + ['0'])
                if choice == '0':
                    continue
                keep_idx = int(choice) - 1

            for i, info in enumerate(group.files):
                if i == keep_idx:
                    kept += 1
                    continue
                if self.settings.dry_run:
                    if self.console:
                        self.console.print(f"[cyan]DRY-RUN: Would delete {info.filename}[/cyan]")
                    else:
                        print(f"DRY-RUN: Would delete {info.filename}")
                    with open(log_file, 'a', encoding='utf-8') as f:
                        f.write(f"[DRY-RUN] {info.path}\n")
                    deleted += 1
                else:
                    try:
                        os.remove(info.path)
                        with open(log_file, 'a', encoding='utf-8') as f:
                            f.write(f"[DELETED] {info.path}\n")
                        deleted += 1
                    except Exception as e:
                        with open(log_file, 'a', encoding='utf-8') as f:
                            f.write(f"[ERROR] {info.path}: {e}\n")
                        errors += 1

        elapsed = time.time() - start
        if self.console:
            self.console.print(f"\n[bold green]{self.locale.t('deletion_complete')}[/bold green]")
            self.console.print(f"{self.locale.t('stats_files_kept')}: {kept}")
            self.console.print(f"{self.locale.t('stats_files_deleted')}: {deleted}")
            if errors:
                self.console.print(f"[red]{self.locale.t('stats_errors')}: {errors}[/red]")
            self.console.print(f"{self.locale.t('stats_time')}: {elapsed:.1f}s")
            self.console.print(f"{self.locale.t('log_file')}: {log_file}")
        else:
            print(f"\n{self.locale.t('deletion_complete')}")
            print(f"{self.locale.t('stats_files_kept')}: {kept}")
            print(f"{self.locale.t('stats_files_deleted')}: {deleted}")
            if errors:
                print(f"{self.locale.t('stats_errors')}: {errors}")
            print(f"{self.locale.t('stats_time')}: {elapsed:.1f}s")
            print(f"{self.locale.t('log_file')}: {log_file}")

    def toggle_dryrun(self):
        self.settings.dry_run = not self.settings.dry_run
        self.settings.save()
        if self.console:
            self.console.print(f"[bold]Dry-run mode: {'ON' if self.settings.dry_run else 'OFF'}[/bold]")
        else:
            print(f"Dry-run mode: {'ON' if self.settings.dry_run else 'OFF'}")
        self._press_enter()

    def toggle_mode(self):
        modes = ['fast', 'smart', 'deep']
        current = self.settings.scan_mode
        idx = (modes.index(current) + 1) % len(modes)
        self.settings.scan_mode = modes[idx]
        self.settings.save()
        mode_names = {'fast': self.locale.t('mode_fast'), 'smart': self.locale.t('mode_smart'), 'deep': self.locale.t('mode_deep')}
        if self.console:
            self.console.print(f"[bold]{self.locale.t('scan_mode')}: {mode_names[self.settings.scan_mode]}[/bold]")
        else:
            print(f"{self.locale.t('scan_mode')}: {mode_names[self.settings.scan_mode]}")
        self._press_enter()

    def change_folder(self):
        folder = self._get_folder()
        if folder:
            self.folder = folder
            self.settings.last_folder = folder
            self.settings.save()
            if self.console:
                self.console.print(f"[green]{self.locale.t('folder_set')}: {self.folder}[/green]")
            else:
                print(f"{self.locale.t('folder_set')}: {self.folder}")
        self._press_enter()

    def settings_menu(self):
        while True:
            self._clear()
            if self.console:
                self.console.print(f"\n[bold]{self.locale.t('settings_title')}[/bold]")
            else:
                print(f"\n{self.locale.t('settings_title')}")
            print("1. " + self.locale.t('setting_language') + f": {self.settings.language.upper()}")
            print("2. " + self.locale.t('setting_recursive') + f": {self.settings.recursive}")
            print("3. " + self.locale.t('setting_dry_run') + f": {self.settings.dry_run}")
            print("4. " + self.locale.t('setting_auto_confirm') + f": {self.settings.auto_confirm}")
            print("5. " + self.locale.t('setting_keep_strategy') + f": {self.settings.keep_strategy}")
            print("6. " + self.locale.t('setting_scan_mode') + f": {self.settings.scan_mode}")
            print("7. " + self.locale.t('setting_show_progress') + f": {self.settings.show_progress}")
            print("8. " + self.locale.t('setting_ignore_small') + f": {self.settings.ignore_small_files}")
            print("9. " + self.locale.t('setting_export_report') + f": {self.settings.export_report}")
            print("a. " + self.locale.t('setting_report_format') + f": {self.settings.report_format}")
            print("0. " + self.locale.t('back'))

            choice = self._prompt_choice(self.locale.t('enter_choice'), ['0','1','2','3','4','5','6','7','8','9','a'])
            if choice == '0':
                self.settings.save()
                return
            elif choice == '1':
                self.settings.language = 'ru' if self.settings.language == 'en' else 'en'
                self.locale.lang = self.settings.language
                self.settings.save()
            elif choice == '2':
                self.settings.recursive = not self.settings.recursive
                self.settings.save()
            elif choice == '3':
                self.settings.dry_run = not self.settings.dry_run
                self.settings.save()
            elif choice == '4':
                self.settings.auto_confirm = not self.settings.auto_confirm
                self.settings.save()
            elif choice == '5':
                strategies = ['auto', 'first', 'manual']
                idx = (strategies.index(self.settings.keep_strategy) + 1) % len(strategies)
                self.settings.keep_strategy = strategies[idx]
                self.settings.save()
                if self.console:
                    self.console.print(f"[green]Keep strategy: {self.settings.keep_strategy}[/green]")
                else:
                    print(f"Keep strategy: {self.settings.keep_strategy}")
                self._press_enter()
            elif choice == '6':
                modes = ['fast', 'smart', 'deep']
                idx = (modes.index(self.settings.scan_mode) + 1) % len(modes)
                self.settings.scan_mode = modes[idx]
                self.settings.save()
                if self.console:
                    self.console.print(f"[green]Scan mode: {self.settings.scan_mode}[/green]")
                else:
                    print(f"Scan mode: {self.settings.scan_mode}")
                self._press_enter()
            elif choice == '7':
                self.settings.show_progress = not self.settings.show_progress
                self.settings.save()
            elif choice == '8':
                self.settings.ignore_small_files = not self.settings.ignore_small_files
                self.settings.save()
            elif choice == '9':
                self.settings.export_report = not self.settings.export_report
                self.settings.save()
            elif choice == 'a':
                formats = ['html', 'json', 'csv']
                idx = (formats.index(self.settings.report_format) + 1) % len(formats)
                self.settings.report_format = formats[idx]
                self.settings.save()
                if self.console:
                    self.console.print(f"[green]Report format: {self.settings.report_format}[/green]")
                else:
                    print(f"Report format: {self.settings.report_format}")
                self._press_enter()

    def about(self):
        self._clear()
        if self.console:
            self.console.print(Panel(
                f"[bold]{self.locale.t('app_title')}[/bold]\n"
                f"{self.locale.t('about_version')}\n"
                f"{self.locale.t('about_desc')}\n\n"
                f"[bold]{self.locale.t('about_features')}:[/bold]\n"
                f"• {self.locale.t('mode_fast')}\n"
                f"• {self.locale.t('mode_smart')}\n"
                f"• {self.locale.t('mode_deep')}\n"
                f"• Weighted scoring system with explanations\n"
                f"• Automatic best file selection\n"
                f"• Export reports (HTML, JSON, CSV)\n"
                f"• Supports MP3, FLAC, M4A, AAC, OGG, OPUS, WAV, AIFF, WMA, APE\n"
                f"• Dry-run, auto-confirm\n"
                f"• Russian/English interface\n\n"
                f"[bold]{self.locale.t('about_tech')}:[/bold]\n"
                f"• Python 3.6+, mutagen, rich, ffprobe",
                title="About",
                border_style="blue"
            ))
        else:
            print(f"\n{self.locale.t('about_title')}")
            print(self.locale.t('about_version'))
            print(self.locale.t('about_desc'))
        self._press_enter()

    def main_menu(self):
        while True:
            self._clear()
            folder_display = self.folder if self.folder else "[dim]Not selected[/dim]"
            dry_status = "[bold red]ON[/bold red]" if self.settings.dry_run else "[bold green]OFF[/bold green]"
            mode_names = {'fast': self.locale.t('mode_fast'), 'smart': self.locale.t('mode_smart'), 'deep': self.locale.t('mode_deep')}
            strategy_names = {'auto': self.locale.t('strategy_auto'), 'first': self.locale.t('strategy_first'), 'manual': self.locale.t('strategy_manual')}

            if self.console:
                header = (
                    f"[dim]{self.locale.t('current_folder')}:[/dim] [bold cyan]{folder_display}[/bold cyan]\n"
                    f"[dim]Dry-Run:[/dim] {dry_status}\n"
                    f"[dim]{self.locale.t('scan_mode')}:[/dim] [bold yellow]{mode_names[self.settings.scan_mode]}[/bold yellow]\n"
                    f"[dim]{self.locale.t('keep_strategy')}:[/dim] [bold yellow]{strategy_names[self.settings.keep_strategy]}[/bold yellow]"
                )
                self.console.print(Panel(header, title=f"[bold magenta]{self.locale.t('app_title')}[/bold magenta]", expand=False, box=box.ROUNDED))

                menu_table = Table(box=box.SIMPLE, show_header=False)
                menu_table.add_column("Key", style="bold yellow", justify="right")
                menu_table.add_column("Action", style="white")
                menu_table.add_row("1", self.locale.t('menu_scan'))
                menu_table.add_row("")
                menu_table.add_row("2", self.locale.t('menu_toggle_dryrun'))
                menu_table.add_row("3", self.locale.t('menu_change_folder'))
                menu_table.add_row("4", self.locale.t('menu_toggle_mode'))
                menu_table.add_row("")
                menu_table.add_row("5", self.locale.t('menu_settings'))
                menu_table.add_row("6", self.locale.t('menu_about'))
                menu_table.add_row("")
                menu_table.add_row("0", f"[dim]{self.locale.t('menu_exit')}[/dim]")
                self.console.print(menu_table)
            else:
                print(f"\n{self.locale.t('app_title')}")
                print(f"{self.locale.t('current_folder')}: {self.folder if self.folder else 'Not selected'}")
                print(f"Dry-Run: {'ON' if self.settings.dry_run else 'OFF'}")
                print(f"{self.locale.t('scan_mode')}: {mode_names[self.settings.scan_mode]}")
                print(f"{self.locale.t('keep_strategy')}: {strategy_names[self.settings.keep_strategy]}")
                print("\n1. " + self.locale.t('menu_scan'))
                print("2. " + self.locale.t('menu_toggle_dryrun'))
                print("3. " + self.locale.t('menu_change_folder'))
                print("4. "+ self.locale.t('menu_toggle_mode'))
                print("5. " + self.locale.t('menu_settings'))
                print("6. " + self.locale.t('menu_about'))
                print("0. " + self.locale.t('menu_exit'))

            choice = self._prompt_choice(self.locale.t('enter_choice'), ['0','1','2','3','4','5','6'])
            if choice == "0":
                if self.console:
                    self.console.print(f"[green]{self.locale.t('goodbye')}[/green]")
                else:
                    print(self.locale.t('goodbye'))
                if Application._root:
                    try:
                        Application._root.destroy()
                    except:
                        pass
                sys.exit(0)
            elif choice == "1":
                self.scan_action()
            elif choice == "2":
                self.toggle_dryrun()
            elif choice == "3":
                self.change_folder()
            elif choice == "4":
                self.toggle_mode()
            elif choice == "5":
                self.settings_menu()
            elif choice == "6":
                self.about()

# =============================================================================
# Entry Point
# =============================================================================
def main():
    app = Application()
    args = sys.argv[1:]
    if args:
        first = os.path.abspath(args[0])
        if os.path.isdir(first):
            app.folder = first
            app.settings.last_folder = first
            app.settings.save()
            if app.console:
                app.console.print(f"\n[bold green]📁 {app.locale.t('drag_drop_detected')}:[/bold green] {first}")
            else:
                print(f"\nDrag & Drop detected: {first}")
            if app._confirm(app.locale.t('scan_this_folder'), default=True):
                app.scan_action()
                return
    app.main_menu()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[yellow]Aborted.[/yellow]")
    except Exception as e:
        print(f"[red]FATAL ERROR:[/red] {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")