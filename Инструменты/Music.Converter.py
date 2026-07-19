#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Audio Converter PRO v3.0
Professional audio converter with drag&drop, rich UI, settings, dry-run and more.
"""

import os
import sys
import re
import json
import time
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path

# =============================================================================
# Clear screen function
# =============================================================================
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# =============================================================================
# Optional GUI folder picker (tkinter)
# =============================================================================
try:
    import tkinter as tk
    from tkinter import filedialog
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False

# =============================================================================
# Rich library for beautiful console output
# =============================================================================
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm
    from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    # Fallback to simple prints if rich not installed
    def rprint(*args, **kwargs):
        print(*args)

# =============================================================================
# Configuration / Constants
# =============================================================================

SUPPORTED_INPUT_EXTENSIONS = [
    '.mp3', '.wav', '.flac', '.m4a', '.aac', '.ogg', '.opus',
    '.wma', '.aiff', '.aif', '.ape', '.wv', '.tta', '.mka',
    '.ra', '.rm', '.voc', '.au', '.snd', '.pcm', '.raw',
    '.mp4', '.m4v', '.mov', '.avi', '.mkv', '.webm', '.flv',
    '.wmv', '.3gp', '.3g2', '.mpeg', '.mpg', '.vob', '.ts',
    '.mts', '.m2ts', '.divx', '.xvid'
]

AUDIO_FORMATS = {
    '1': {
        'key': 'wav',
        'ext': '.wav',
        'codec': 'pcm_s16le',
        'name_key': 'format_wav',
        'desc_key': 'format_wav_desc',
        'lossless': True,
        'sample_formats': {
            '1': {'key': 's16', 'name_key': 'bit_depth_16', 'default': True},
            '2': {'key': 's24', 'name_key': 'bit_depth_24'},
            '3': {'key': 's32', 'name_key': 'bit_depth_32'},
            '4': {'key': 'flt', 'name_key': 'bit_depth_32float'},
            '5': {'key': 'dbl', 'name_key': 'bit_depth_64float'},
        }
    },
    '2': {
        'key': 'flac',
        'ext': '.flac',
        'codec': 'flac',
        'name_key': 'format_flac',
        'desc_key': 'format_flac_desc',
        'lossless': True,
        'compression_levels': {
            '1': {'level': 0, 'name_key': 'flac_compression_fastest'},
            '2': {'level': 1, 'name_key': 'flac_compression_fastest'},
            '3': {'level': 2, 'name_key': 'flac_compression_fastest'},
            '4': {'level': 3, 'name_key': 'flac_compression_fastest'},
            '5': {'level': 4, 'name_key': 'flac_compression_standard'},
            '6': {'level': 5, 'name_key': 'flac_compression_standard', 'default': True},
            '7': {'level': 6, 'name_key': 'flac_compression_best'},
            '8': {'level': 7, 'name_key': 'flac_compression_best'},
            '9': {'level': 8, 'name_key': 'flac_compression_best'},
        }
    },
    '3': {
        'key': 'mp3',
        'ext': '.mp3',
        'codec': 'libmp3lame',
        'name_key': 'format_mp3',
        'desc_key': 'format_mp3_desc',
        'lossless': False,
        'bitrates': {
            '1': {'bitrate': '96k', 'name_key': 'bitrate_low'},
            '2': {'bitrate': '128k', 'name_key': 'bitrate_medium'},
            '3': {'bitrate': '160k', 'name_key': 'bitrate_standard'},
            '4': {'bitrate': '192k', 'name_key': 'bitrate_high', 'default': True},
            '5': {'bitrate': '256k', 'name_key': 'bitrate_very_high'},
            '6': {'bitrate': '320k', 'name_key': 'bitrate_max'},
        },
        'qualities': {
            '1': {'quality': 0, 'name_key': 'mp3_quality_best'},
            '2': {'quality': 1, 'name_key': 'mp3_quality_best'},
            '3': {'quality': 2, 'name_key': 'mp3_quality_best', 'default': True},
            '4': {'quality': 3, 'name_key': 'mp3_quality_best'},
            '5': {'quality': 4, 'name_key': 'mp3_quality_best'},
            '6': {'quality': 5, 'name_key': 'mp3_quality_worst'},
            '7': {'quality': 6, 'name_key': 'mp3_quality_worst'},
            '8': {'quality': 7, 'name_key': 'mp3_quality_worst'},
            '9': {'quality': 8, 'name_key': 'mp3_quality_worst'},
            '10': {'quality': 9, 'name_key': 'mp3_quality_worst'},
        }
    },
    '4': {
        'key': 'aac',
        'ext': '.m4a',
        'codec': 'aac',
        'name_key': 'format_aac',
        'desc_key': 'format_aac_desc',
        'lossless': False,
        'bitrates': {
            '1': {'bitrate': '96k', 'name_key': 'bitrate_low'},
            '2': {'bitrate': '128k', 'name_key': 'bitrate_medium'},
            '3': {'bitrate': '160k', 'name_key': 'bitrate_standard'},
            '4': {'bitrate': '192k', 'name_key': 'bitrate_high'},
            '5': {'bitrate': '256k', 'name_key': 'bitrate_very_high', 'default': True},
            '6': {'bitrate': '320k', 'name_key': 'bitrate_max'},
        }
    },
    '5': {
        'key': 'opus',
        'ext': '.opus',
        'codec': 'libopus',
        'name_key': 'format_opus',
        'desc_key': 'format_opus_desc',
        'lossless': False,
        'bitrates': {
            '1': {'bitrate': '64k', 'name_key': 'bitrate_low'},
            '2': {'bitrate': '96k', 'name_key': 'bitrate_medium'},
            '3': {'bitrate': '128k', 'name_key': 'bitrate_standard', 'default': True},
            '4': {'bitrate': '160k', 'name_key': 'bitrate_high'},
            '5': {'bitrate': '192k', 'name_key': 'bitrate_very_high'},
            '6': {'bitrate': '256k', 'name_key': 'bitrate_max'},
        }
    },
    '6': {
        'key': 'ogg',
        'ext': '.ogg',
        'codec': 'libvorbis',
        'name_key': 'format_ogg',
        'desc_key': 'format_ogg_desc',
        'lossless': False,
        'qualities': {
            '1': {'quality': -1, 'name_key': 'ogg_quality_worst'},
            '2': {'quality': 0, 'name_key': 'ogg_quality_worst'},
            '3': {'quality': 1, 'name_key': 'ogg_quality_worst'},
            '4': {'quality': 2, 'name_key': 'ogg_quality_worst'},
            '5': {'quality': 3, 'name_key': 'ogg_quality_worst', 'default': True},
            '6': {'quality': 4, 'name_key': 'ogg_quality_best'},
            '7': {'quality': 5, 'name_key': 'ogg_quality_best'},
            '8': {'quality': 6, 'name_key': 'ogg_quality_best'},
            '9': {'quality': 7, 'name_key': 'ogg_quality_best'},
            '10': {'quality': 8, 'name_key': 'ogg_quality_best'},
            '11': {'quality': 9, 'name_key': 'ogg_quality_best'},
            '12': {'quality': 10, 'name_key': 'ogg_quality_best'},
        }
    },
    '7': {
        'key': 'm4a',
        'ext': '.m4a',
        'codec': 'aac',
        'name_key': 'format_m4a',
        'desc_key': 'format_m4a_desc',
        'lossless': False,
        'bitrates': {
            '1': {'bitrate': '96k', 'name_key': 'bitrate_low'},
            '2': {'bitrate': '128k', 'name_key': 'bitrate_medium'},
            '3': {'bitrate': '160k', 'name_key': 'bitrate_standard'},
            '4': {'bitrate': '192k', 'name_key': 'bitrate_high'},
            '5': {'bitrate': '256k', 'name_key': 'bitrate_very_high', 'default': True},
            '6': {'bitrate': '320k', 'name_key': 'bitrate_max'},
        }
    },
    '8': {
        'key': 'alac',
        'ext': '.m4a',
        'codec': 'alac',
        'name_key': 'format_alac',
        'desc_key': 'format_alac_desc',
        'lossless': True,
    }
}

SAMPLE_RATES = {
    '1': {'rate': 8000, 'name_key': 'sample_rate_8k'},
    '2': {'rate': 11025, 'name_key': 'sample_rate_11k'},
    '3': {'rate': 16000, 'name_key': 'sample_rate_16k'},
    '4': {'rate': 22050, 'name_key': 'sample_rate_22k'},
    '5': {'rate': 32000, 'name_key': 'sample_rate_32k'},
    '6': {'rate': 44100, 'name_key': 'sample_rate_44k', 'default': True},
    '7': {'rate': 48000, 'name_key': 'sample_rate_48k'},
    '8': {'rate': 88200, 'name_key': 'sample_rate_88k'},
    '9': {'rate': 96000, 'name_key': 'sample_rate_96k'},
    '10': {'rate': 176400, 'name_key': 'sample_rate_176k'},
    '11': {'rate': 192000, 'name_key': 'sample_rate_192k'},
}

CHANNELS = {
    '1': {'channels': 1, 'name_key': 'channels_mono'},
    '2': {'channels': 2, 'name_key': 'channels_stereo', 'default': True},
    '3': {'channels': 4, 'name_key': 'channels_quad'},
    '4': {'channels': 6, 'name_key': 'channels_51'},
    '5': {'channels': 8, 'name_key': 'channels_71'},
}

DEFAULT_SETTINGS = {
    'wav': {
        'sample_fmt': 's16',
        'sample_rate': 44100,
        'channels': 2,
    },
    'flac': {
        'compression_level': 5,
        'sample_rate': 44100,
        'channels': 2,
    },
    'mp3': {
        'bitrate': '192k',
        'quality': 2,
        'sample_rate': 44100,
        'channels': 2,
    },
    'aac': {
        'bitrate': '256k',
        'sample_rate': 44100,
        'channels': 2,
    },
    'opus': {
        'bitrate': '128k',
        'sample_rate': 48000,
        'channels': 2,
    },
    'ogg': {
        'quality': 3,
        'sample_rate': 44100,
        'channels': 2,
    },
    'm4a': {
        'bitrate': '256k',
        'sample_rate': 44100,
        'channels': 2,
    },
    'alac': {
        'sample_rate': 44100,
        'channels': 2,
    }
}

# =============================================================================
# Localization (EN/RU)
# =============================================================================

TRANSLATIONS = {
    'en': {
        # Main menu
        'program_name': 'Audio Converter PRO',
        'main_title': 'MAIN MENU',
        'menu_start': 'Start conversion',
        'menu_settings': 'Settings',
        'menu_ffmpeg': 'FFmpeg info',
        'menu_about': 'About',
        'menu_exit': 'Exit',
        # Settings
        'settings_title': 'SETTINGS',
        'setting_language': 'Language',
        'setting_delete_original': 'Delete original files after conversion',
        'setting_recursive': 'Scan subfolders recursively',
        'setting_preserve_structure': 'Preserve folder structure in output',
        'setting_dry_run': 'Dry-run (no actual conversion)',
        'setting_auto_confirm': 'Auto-confirm all prompts',
        'setting_output_format': 'Default output format',
        'setting_show_progress': 'Show progress bar',
        'back': 'Back',
        # Conversion
        'select_folder': 'Select source folder',
        'enter_path': 'Enter path (or drag folder)',
        'folder_not_found': 'Folder not found',
        'no_files': 'No supported audio files found',
        'files_found': 'Files found',
        'file_list_title': 'Found files (first 10)',
        'select_format': 'Select output format',
        'format_desc': 'Description',
        'select_settings': 'Configure additional settings',
        'bit_depth': 'Bit depth',
        'compression': 'Compression level',
        'quality': 'Quality',
        'original': 'Original (keep)',
        'default': 'Default',
        'output_folder': 'Select output folder',
        'confirm_start': 'Start conversion?',
        'converting': 'Converting...',
        'conversion_complete': 'Conversion complete!',
        'stats_total': 'Total files',
        'stats_success': 'Successful',
        'stats_failed': 'Failed',
        'stats_skipped': 'Skipped',
        'stats_time': 'Time elapsed',
        'stats_avg': 'Avg per file',
        'log_file': 'Log file',
        'dry_run_mode': 'DRY-RUN MODE - no files will be changed',
        'cancel': 'Cancel',
        # About
        'about_version': 'Version 3.0',
        'about_desc': 'Professional audio file converter powered by FFmpeg.',
        'about_features': 'Features',
        'about_tech': 'Technologies',
        # Misc
        'yes': 'Yes',
        'no': 'No',
        'enter_choice': 'Enter your choice',
        'press_enter': 'Press Enter to continue...',
        'error_ffmpeg': 'FFmpeg not found. Please install FFmpeg.',
        'error_conversion': 'Conversion error',
        'success': 'Success',
        'info': 'Info',
        'warning': 'Warning',
        'error': 'Error',
        # Format names (used in menus)
        'format_wav': 'WAV',
        'format_wav_desc': 'Uncompressed PCM',
        'format_flac': 'FLAC',
        'format_flac_desc': 'Free Lossless Audio Codec',
        'format_mp3': 'MP3',
        'format_mp3_desc': 'MPEG Layer 3',
        'format_aac': 'AAC',
        'format_aac_desc': 'Advanced Audio Coding',
        'format_opus': 'Opus',
        'format_opus_desc': 'Opus Interactive Audio',
        'format_ogg': 'OGG',
        'format_ogg_desc': 'Ogg Vorbis',
        'format_m4a': 'M4A',
        'format_m4a_desc': 'MPEG-4 Audio',
        'format_alac': 'ALAC',
        'format_alac_desc': 'Apple Lossless',
        # Bit depth names
        'bit_depth_16': '16-bit integer',
        'bit_depth_24': '24-bit integer',
        'bit_depth_32': '32-bit integer',
        'bit_depth_32float': '32-bit float',
        'bit_depth_64float': '64-bit float',
        # Compression
        'flac_compression_fastest': 'Fastest',
        'flac_compression_standard': 'Standard',
        'flac_compression_best': 'Best compression',
        # Bitrates
        'bitrate_low': 'Low',
        'bitrate_medium': 'Medium',
        'bitrate_standard': 'Standard',
        'bitrate_high': 'High',
        'bitrate_very_high': 'Very High',
        'bitrate_max': 'Maximum',
        # MP3 quality
        'mp3_quality_best': 'Best quality',
        'mp3_quality_worst': 'Worst quality',
        # OGG quality
        'ogg_quality_worst': 'Worst',
        'ogg_quality_best': 'Best',
        # Sample rates
        'sample_rate_8k': '8 kHz',
        'sample_rate_11k': '11.025 kHz',
        'sample_rate_16k': '16 kHz',
        'sample_rate_22k': '22.05 kHz',
        'sample_rate_32k': '32 kHz',
        'sample_rate_44k': '44.1 kHz (CD)',
        'sample_rate_48k': '48 kHz (DVD)',
        'sample_rate_88k': '88.2 kHz',
        'sample_rate_96k': '96 kHz',
        'sample_rate_176k': '176.4 kHz',
        'sample_rate_192k': '192 kHz',
        # Channels
        'channels_mono': 'Mono',
        'channels_stereo': 'Stereo',
        'channels_quad': 'Quad',
        'channels_51': '5.1 Surround',
        'channels_71': '7.1 Surround',
    },
    'ru': {
        'program_name': 'Audio Converter PRO',
        'main_title': 'ГЛАВНОЕ МЕНЮ',
        'menu_start': 'Начать конвертацию',
        'menu_settings': 'Настройки',
        'menu_ffmpeg': 'Информация о FFmpeg',
        'menu_about': 'О программе',
        'menu_exit': 'Выход',
        'settings_title': 'НАСТРОЙКИ',
        'setting_language': 'Язык',
        'setting_delete_original': 'Удалять оригиналы после конвертации',
        'setting_recursive': 'Сканировать подпапки рекурсивно',
        'setting_preserve_structure': 'Сохранять структуру папок в выходных',
        'setting_dry_run': 'Пробный запуск (без реальной конвертации)',
        'setting_auto_confirm': 'Автоподтверждение всех запросов',
        'setting_output_format': 'Формат по умолчанию',
        'setting_show_progress': 'Показывать прогресс-бар',
        'back': 'Назад',
        'select_folder': 'Выберите исходную папку',
        'enter_path': 'Введите путь (или перетащите папку)',
        'folder_not_found': 'Папка не найдена',
        'no_files': 'Не найдено поддерживаемых аудиофайлов',
        'files_found': 'Найдено файлов',
        'file_list_title': 'Найденные файлы (первые 10)',
        'select_format': 'Выберите выходной формат',
        'format_desc': 'Описание',
        'select_settings': 'Настройка дополнительных параметров',
        'bit_depth': 'Битность',
        'compression': 'Степень сжатия',
        'quality': 'Качество',
        'original': 'Оригинал (сохранить)',
        'default': 'По умолчанию',
        'output_folder': 'Выберите выходную папку',
        'confirm_start': 'Начать конвертацию?',
        'converting': 'Конвертация...',
        'conversion_complete': 'Конвертация завершена!',
        'stats_total': 'Всего файлов',
        'stats_success': 'Успешно',
        'stats_failed': 'Ошибок',
        'stats_skipped': 'Пропущено',
        'stats_time': 'Затрачено времени',
        'stats_avg': 'Среднее на файл',
        'log_file': 'Лог-файл',
        'dry_run_mode': 'РЕЖИМ ПРОБНОГО ЗАПУСКА - изменения не будут записаны',
        'cancel': 'Отмена',
        'about_version': 'Версия 3.0',
        'about_desc': 'Профессиональный конвертер аудиофайлов на базе FFmpeg.',
        'about_features': 'Возможности',
        'about_tech': 'Технологии',
        'yes': 'Да',
        'no': 'Нет',
        'enter_choice': 'Выберите вариант',
        'press_enter': 'Нажмите Enter для продолжения...',
        'error_ffmpeg': 'FFmpeg не найден. Установите FFmpeg.',
        'error_conversion': 'Ошибка конвертации',
        'success': 'Успешно',
        'info': 'Информация',
        'warning': 'Предупреждение',
        'error': 'Ошибка',
        'format_wav': 'WAV',
        'format_wav_desc': 'Несжатый PCM',
        'format_flac': 'FLAC',
        'format_flac_desc': 'Free Lossless Audio Codec',
        'format_mp3': 'MP3',
        'format_mp3_desc': 'MPEG Layer 3',
        'format_aac': 'AAC',
        'format_aac_desc': 'Advanced Audio Coding',
        'format_opus': 'Opus',
        'format_opus_desc': 'Opus Interactive Audio',
        'format_ogg': 'OGG',
        'format_ogg_desc': 'Ogg Vorbis',
        'format_m4a': 'M4A',
        'format_m4a_desc': 'MPEG-4 Audio',
        'format_alac': 'ALAC',
        'format_alac_desc': 'Apple Lossless',
        'bit_depth_16': '16-бит целочисленный',
        'bit_depth_24': '24-бит целочисленный',
        'bit_depth_32': '32-бит целочисленный',
        'bit_depth_32float': '32-бит с плавающей точкой',
        'bit_depth_64float': '64-бит с плавающей точкой',
        'flac_compression_fastest': 'Быстрее всего',
        'flac_compression_standard': 'Стандарт',
        'flac_compression_best': 'Лучшее сжатие',
        'bitrate_low': 'Низкое',
        'bitrate_medium': 'Среднее',
        'bitrate_standard': 'Стандартное',
        'bitrate_high': 'Высокое',
        'bitrate_very_high': 'Очень высокое',
        'bitrate_max': 'Максимальное',
        'mp3_quality_best': 'Лучшее качество',
        'mp3_quality_worst': 'Худшее качество',
        'ogg_quality_worst': 'Худшее',
        'ogg_quality_best': 'Лучшее',
        'sample_rate_8k': '8 кГц',
        'sample_rate_11k': '11.025 кГц',
        'sample_rate_16k': '16 кГц',
        'sample_rate_22k': '22.05 кГц',
        'sample_rate_32k': '32 кГц',
        'sample_rate_44k': '44.1 кГц (CD)',
        'sample_rate_48k': '48 кГц (DVD)',
        'sample_rate_88k': '88.2 кГц',
        'sample_rate_96k': '96 кГц',
        'sample_rate_176k': '176.4 кГц',
        'sample_rate_192k': '192 кГц',
        'channels_mono': 'Моно',
        'channels_stereo': 'Стерео',
        'channels_quad': 'Квадро',
        'channels_51': '5.1 Surround',
        'channels_71': '7.1 Surround',
    }
}

# =============================================================================
# Settings Manager
# =============================================================================

class Settings:
    """Global settings manager with persistence."""

    CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".audio_converter_config.json")

    def __init__(self):
        self.language = 'en'
        self.delete_original = False
        self.recursive = True
        self.preserve_structure = False
        self.dry_run = False
        self.auto_confirm = False
        self.output_format = 'mp3'        # default format key
        self.bitrate = '192k'             # default bitrate string
        self.sample_rate = 44100          # default sample rate
        self.channels = 2                 # default channels
        self.show_progress = True         # show progress bar
        self.load()

    def load(self):
        """Load settings from JSON file."""
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for key, value in data.items():
                        if hasattr(self, key):
                            setattr(self, key, value)
            except Exception:
                pass

    def save(self):
        """Save settings to JSON file."""
        try:
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.__dict__, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def get(self, key, default=None):
        return getattr(self, key, default)

    def set(self, key, value):
        setattr(self, key, value)
        self.save()


# =============================================================================
# Localization Helper
# =============================================================================

class Locale:
    def __init__(self, lang='en'):
        self.lang = lang

    def t(self, key):
        """Get translation string by key."""
        return TRANSLATIONS.get(self.lang, TRANSLATIONS['en']).get(key, key)


# =============================================================================
# Main Converter Class
# =============================================================================

class AudioConverter:
    def __init__(self):
        self.settings = Settings()
        self.locale = Locale(self.settings.language)
        self.console = Console() if RICH_AVAILABLE else None

        # Conversion statistics
        self.total_files = 0
        self.converted_files = 0
        self.failed_files = 0
        self.skipped_files = 0
        self.start_time = 0
        self.source_folder = ""

        # Check FFmpeg availability
        self.ffmpeg_available = self._check_ffmpeg()

    def _check_ffmpeg(self) -> bool:
        """Check if ffmpeg is in PATH."""
        try:
            result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, check=False)
            return result.returncode == 0
        except FileNotFoundError:
            return False

    def _print(self, message, style=None):
        if self.console:
            self.console.print(message, style=style)
        else:
            print(message)

    def _print_table(self, title, columns, rows):
        if self.console:
            table = Table(title=title)
            for col in columns:
                table.add_column(col)
            for row in rows:
                table.add_row(*[str(cell) for cell in row])
            self.console.print(table)
        else:
            print(f"\n{title}")
            for row in rows:
                print("  ".join(str(cell) for cell in row))

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
        """Open folder picker dialog using tkinter."""
        if TKINTER_AVAILABLE:
            root = tk.Tk()
            root.withdraw()
            folder = filedialog.askdirectory(title=self.locale.t('select_folder'))
            root.destroy()
            return folder
        return None

    def _get_folder(self):
        """Get folder path from user (GUI or manual)."""
        # Try GUI first
        folder = self._select_folder_gui()
        if folder:
            return folder

        # Manual input
        print(f"\n{self.locale.t('enter_path')}:")
        print(f"({self.locale.t('cancel')}: leave empty)")
        path = input("> ").strip()
        if not path:
            return None
        path = os.path.expanduser(path)
        if os.path.isdir(path):
            return path
        else:
            self._print(self.locale.t('folder_not_found'), style="red")
            return None

    def _scan_directory(self, folder: str, recursive: bool) -> List[str]:
        """Scan folder for supported audio files."""
        files = []
        if not os.path.isdir(folder):
            return files
        if recursive:
            for root, _, filenames in os.walk(folder):
                for f in filenames:
                    ext = os.path.splitext(f)[1].lower()
                    if ext in SUPPORTED_INPUT_EXTENSIONS:
                        files.append(os.path.join(root, f))
        else:
            try:
                for item in os.listdir(folder):
                    full = os.path.join(folder, item)
                    if os.path.isfile(full):
                        ext = os.path.splitext(item)[1].lower()
                        if ext in SUPPORTED_INPUT_EXTENSIONS:
                            files.append(full)
            except PermissionError:
                pass
        return files

    def _get_file_info(self, filepath: str) -> Dict[str, Any]:
        """Get basic audio info using ffprobe."""
        info = {
            'format': 'unknown',
            'duration': 0,
            'sample_rate': 0,
            'channels': 0,
            'codec': 'unknown',
            'bit_rate': 0,
            'size': os.path.getsize(filepath),
            'filename': os.path.basename(filepath)
        }
        try:
            # Use ffprobe if available
            cmd = [
                'ffprobe', '-v', 'quiet',
                '-print_format', 'json',
                '-show_streams', '-show_format',
                filepath
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            if result.returncode == 0:
                data = json.loads(result.stdout)
                # Find audio stream
                audio_stream = None
                for stream in data.get('streams', []):
                    if stream.get('codec_type') == 'audio':
                        audio_stream = stream
                        break
                if audio_stream:
                    info['format'] = audio_stream.get('codec_name', 'unknown')
                    info['sample_rate'] = int(audio_stream.get('sample_rate', 0))
                    info['channels'] = int(audio_stream.get('channels', 0))
                    info['codec'] = audio_stream.get('codec_name', 'unknown')
                    info['bit_rate'] = int(audio_stream.get('bit_rate', 0))
                    info['duration'] = float(audio_stream.get('duration', data.get('format', {}).get('duration', 0)))
                elif data.get('format'):
                    info['format'] = data['format'].get('format_name', 'unknown')
                    info['duration'] = float(data['format'].get('duration', 0))
        except Exception:
            pass
        return info

    def _format_file_size(self, size_bytes: int) -> str:
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

    def _format_duration(self, seconds: float) -> str:
        if seconds < 60:
            return f"{seconds:.0f}s"
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        if mins < 60:
            return f"{mins}m {secs}s"
        hours = mins // 60
        mins = mins % 60
        return f"{hours}h {mins}m {secs}s"

    def _get_output_path(self, input_path: str, output_dir: str, target_format: str) -> str:
        """Generate output file path, handling name collisions."""
        # Find extension
        ext = None
        for fmt in AUDIO_FORMATS.values():
            if fmt['key'] == target_format:
                ext = fmt['ext']
                break
        if not ext:
            ext = '.wav'

        base = os.path.splitext(os.path.basename(input_path))[0]
        # Sanitize filename
        safe = re.sub(r'[<>:"/\\|?*]', '_', base)
        safe = re.sub(r'\s+', ' ', safe).strip()

        # If preserving structure, build subpath
        if self.settings.preserve_structure and self.source_folder:
            rel = os.path.relpath(os.path.dirname(input_path), self.source_folder)
            if rel == '.':
                out_dir = output_dir
            else:
                out_dir = os.path.join(output_dir, rel)
        else:
            out_dir = output_dir

        os.makedirs(out_dir, exist_ok=True)

        counter = 1
        out_path = os.path.join(out_dir, safe + ext)
        while os.path.exists(out_path):
            out_path = os.path.join(out_dir, f"{safe}_{counter}{ext}")
            counter += 1
        return out_path

    def _convert_single_file(self, input_path: str, output_path: str, target_format: str,
                             settings: Dict[str, Any]) -> Tuple[bool, str]:
        """Convert one file using ffmpeg."""
        try:
            # Find codec
            codec = None
            for fmt in AUDIO_FORMATS.values():
                if fmt['key'] == target_format:
                    codec = fmt['codec']
                    break
            if not codec:
                return False, "Unknown format"

            # Build ffmpeg command
            cmd = ['ffmpeg', '-y', '-i', input_path, '-map_metadata', '0']

            # Audio codec
            cmd.extend(['-c:a', codec])

            # Additional settings
            if 'sample_fmt' in settings:
                cmd.extend(['-sample_fmt', settings['sample_fmt']])
            if 'sample_rate' in settings and settings['sample_rate']:
                cmd.extend(['-ar', str(settings['sample_rate'])])
            if 'channels' in settings and settings['channels']:
                cmd.extend(['-ac', str(settings['channels'])])
            if 'bitrate' in settings:
                cmd.extend(['-b:a', settings['bitrate']])
            if 'quality' in settings:
                if target_format == 'mp3':
                    cmd.extend(['-q:a', str(settings['quality'])])
                elif target_format == 'ogg':
                    cmd.extend(['-q:a', str(settings['quality'])])
            if 'compression_level' in settings:
                cmd.extend(['-compression_level', str(settings['compression_level'])])

            cmd.append(output_path)

            # Run conversion
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            if result.returncode != 0:
                error_msg = result.stderr[:200] if result.stderr else "Unknown error"
                return False, f"FFmpeg error: {error_msg}"

            # Check output
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                return True, "Success"
            else:
                return False, "Output file missing or empty"

        except Exception as e:
            return False, str(e)

    def _print_progress(self, current: int, total: int, filename: str = ""):
        """Print simple text progress bar (fallback when rich not available)."""
        if not self.settings.show_progress:
            return
        percent = (current / total) * 100
        bar_length = 40
        filled = int(bar_length * current // total)
        bar = '█' * filled + '░' * (bar_length - filled)
        # Truncate filename to fit
        max_name_len = 30
        if len(filename) > max_name_len:
            filename = filename[:max_name_len-3] + '...'
        sys.stdout.write(f'\r[{bar}] {percent:>5.1f}% ({current}/{total}) {filename}')
        sys.stdout.flush()

    def _run_conversion(self, files: List[str], target_format: str,
                        settings: Dict[str, Any], output_dir: str):
        """Run conversion on all files."""
        self.total_files = len(files)
        self.converted_files = 0
        self.failed_files = 0
        self.skipped_files = 0
        self.start_time = time.time()

        # Create log file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(output_dir, f"conversion_log_{timestamp}.txt")
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f"Conversion log - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Format: {target_format}\n")
            f.write(f"Settings: {json.dumps(settings, indent=2)}\n")
            f.write(f"Files: {self.total_files}\n")
            f.write("-" * 50 + "\n")

        # Show dry-run warning
        if self.settings.dry_run:
            self._print(self.locale.t('dry_run_mode'), style="bold yellow")

        # Initialize progress
        if self.settings.show_progress:
            if RICH_AVAILABLE and self.console:
                # Use rich progress bar
                progress = Progress(
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(),
                    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                    TimeElapsedColumn(),
                    console=self.console
                )
                task = progress.add_task(self.locale.t('converting'), total=len(files))
                progress.start()
                use_rich_progress = True
            else:
                # Use simple text progress
                progress = None
                use_rich_progress = False
                print(f"\n{self.locale.t('converting')}...")
                self._print_progress(0, len(files), "")
        else:
            progress = None
            use_rich_progress = False
            print(f"\n{self.locale.t('converting')}...")

        for i, input_path in enumerate(files, 1):
            filename = os.path.basename(input_path)

            if use_rich_progress:
                progress.update(task, description=f"{i}/{len(files)} {filename[:30]}")
            elif self.settings.show_progress:
                self._print_progress(i, len(files), filename)

            # Generate output path
            output_path = self._get_output_path(input_path, output_dir, target_format)

            # Skip if same extension and not deleting original (to avoid overwrite)
            input_ext = os.path.splitext(input_path)[1].lower()
            target_ext = None
            for fmt in AUDIO_FORMATS.values():
                if fmt['key'] == target_format:
                    target_ext = fmt['ext']
                    break
            if target_ext and input_ext == target_ext and not self.settings.delete_original:
                self.skipped_files += 1
                with open(log_file, 'a', encoding='utf-8') as f:
                    f.write(f"[SKIPPED] {filename} - already in target format\n")
                if use_rich_progress:
                    progress.advance(task)
                continue

            # Perform conversion (or dry-run)
            if self.settings.dry_run:
                # Simulate success
                self.converted_files += 1
                with open(log_file, 'a', encoding='utf-8') as f:
                    f.write(f"[DRY-RUN] {filename} -> {os.path.basename(output_path)}\n")
            else:
                success, msg = self._convert_single_file(input_path, output_path, target_format, settings)
                if success:
                    self.converted_files += 1
                    with open(log_file, 'a', encoding='utf-8') as f:
                        f.write(f"[SUCCESS] {filename} -> {os.path.basename(output_path)}\n")
                    if self.settings.delete_original and input_path != output_path:
                        try:
                            os.remove(input_path)
                            with open(log_file, 'a', encoding='utf-8') as f:
                                f.write(f"  Original deleted\n")
                        except Exception as e:
                            self._print(f"Warning: could not delete original {filename}: {e}", style="yellow")
                else:
                    self.failed_files += 1
                    with open(log_file, 'a', encoding='utf-8') as f:
                        f.write(f"[ERROR] {filename}: {msg}\n")
                    self._print(f"Error converting {filename}: {msg}", style="red")

            if use_rich_progress:
                progress.advance(task)

        # Final newline after simple progress
        if self.settings.show_progress and not use_rich_progress and not RICH_AVAILABLE:
            print()  # newline after progress bar

        if use_rich_progress:
            progress.stop()

        # Statistics
        elapsed = time.time() - self.start_time
        self._print_statistics(elapsed, log_file)

    def _print_statistics(self, elapsed: float, log_file: str):
        """Show conversion statistics."""
        if self.console:
            table = Table(title=self.locale.t('conversion_complete'))
            table.add_column(self.locale.t('stats_total'), justify="right")
            table.add_column(self.locale.t('stats_success'), justify="right")
            table.add_column(self.locale.t('stats_failed'), justify="right")
            table.add_column(self.locale.t('stats_skipped'), justify="right")
            table.add_column(self.locale.t('stats_time'), justify="right")
            table.add_row(
                str(self.total_files),
                str(self.converted_files),
                str(self.failed_files),
                str(self.skipped_files),
                f"{elapsed:.1f}s"
            )
            self.console.print(table)
            self.console.print(f"{self.locale.t('log_file')}: {log_file}")
        else:
            print(f"\n{self.locale.t('conversion_complete')}")
            print(f"{self.locale.t('stats_total')}: {self.total_files}")
            print(f"{self.locale.t('stats_success')}: {self.converted_files}")
            print(f"{self.locale.t('stats_failed')}: {self.failed_files}")
            print(f"{self.locale.t('stats_skipped')}: {self.skipped_files}")
            print(f"{self.locale.t('stats_time')}: {elapsed:.1f}s")
            print(f"{self.locale.t('log_file')}: {log_file}")

    # ========================================================================
    # Conversion Workflow
    # ========================================================================

    def run_conversion_workflow(self, folder=None, files=None):
        """
        Main conversion process.
        If folder is provided, skip folder selection.
        If files is provided, convert only those files (ignoring folder scan).
        """
        # Check FFmpeg
        if not self.ffmpeg_available:
            self._print(self.locale.t('error_ffmpeg'), style="red")
            return

        # Step 1: Select source folder (if not provided)
        if folder is None:
            self._print(f"\n[bold]{self.locale.t('select_folder')}[/bold]")
            folder = self._get_folder()
            if not folder:
                return
        else:
            # If folder provided, we still need to ensure it exists
            if not os.path.isdir(folder):
                self._print(self.locale.t('folder_not_found'), style="red")
                return
            self._print(f"\n[bold]Using folder:[/bold] {folder}")
        
        self.source_folder = folder  # store for path preservation

        # Step 2: Get list of files
        if files is None:
            files = self._scan_directory(folder, self.settings.recursive)
        else:
            # Filter only existing files
            files = [f for f in files if os.path.isfile(f)]
            if not files:
                self._print(self.locale.t('no_files'), style="red")
                return

        if not files:
            self._print(self.locale.t('no_files'), style="red")
            return

        self._print(f"\n{self.locale.t('files_found')}: {len(files)}")
        # Show first 10 files
        rows = []
        for f in files[:10]:
            info = self._get_file_info(f)
            size = self._format_file_size(info['size'])
            dur = self._format_duration(info['duration'])
            rows.append((os.path.basename(f), info['codec'].upper(), size, dur))
        if self.console:
            table = Table(title=self.locale.t('file_list_title'))
            table.add_column("File")
            table.add_column("Codec")
            table.add_column("Size")
            table.add_column("Duration")
            for row in rows:
                table.add_row(*row)
            self.console.print(table)
        else:
            print(f"\n{self.locale.t('file_list_title')}:")
            for row in rows:
                print(f"  {row[0]}  {row[1]}  {row[2]}  {row[3]}")
        if len(files) > 10:
            self._print(f"... and {len(files)-10} more")

        # Step 3: Select output format
        self._print(f"\n[bold]{self.locale.t('select_format')}[/bold]")
        for key, fmt in AUDIO_FORMATS.items():
            name = self.locale.t(fmt['name_key'])
            desc = self.locale.t(fmt['desc_key'])
            default_marker = " (default)" if fmt['key'] == self.settings.output_format else ""
            print(f"  {key}. {name} - {desc}{default_marker}")
        print(f"  0. {self.locale.t('cancel')}")
        choice = self._prompt_choice(self.locale.t('enter_choice'), 
                                     [str(i) for i in range(0, len(AUDIO_FORMATS)+1)])
        if choice == "0":
            return
        format_info = AUDIO_FORMATS[choice]
        target_format = format_info['key']

        # Step 4: Configure settings for this format
        self._print(f"\n[bold]{self.locale.t('select_settings')}[/bold]")
        conv_settings = {}
        # Determine lossless/lossy
        is_lossless = format_info.get('lossless', False)

        if is_lossless:
            # Bit depth (sample format)
            if 'sample_formats' in format_info:
                print(f"\n{self.locale.t('bit_depth')}:")
                for sk, sf in format_info['sample_formats'].items():
                    name = self.locale.t(sf['name_key'])
                    default = sf.get('default', False)
                    marker = " (default)" if default else ""
                    print(f"  {sk}. {name}{marker}")
                print(f"  0. {self.locale.t('original')}")
                choice = self._prompt_choice(self.locale.t('enter_choice'),
                                             [str(i) for i in range(0, len(format_info['sample_formats'])+1)])
                if choice != "0":
                    conv_settings['sample_fmt'] = format_info['sample_formats'][choice]['key']
            # Compression level (FLAC)
            if 'compression_levels' in format_info:
                print(f"\n{self.locale.t('compression')}:")
                for ck, cl in format_info['compression_levels'].items():
                    name = self.locale.t(cl['name_key'])
                    default = cl.get('default', False)
                    marker = " (default)" if default else ""
                    print(f"  {ck}. {name} (level {cl['level']}){marker}")
                print(f"  0. {self.locale.t('default')}")
                choice = self._prompt_choice(self.locale.t('enter_choice'),
                                             [str(i) for i in range(0, len(format_info['compression_levels'])+1)])
                if choice != "0":
                    conv_settings['compression_level'] = format_info['compression_levels'][choice]['level']
        else:
            # Bitrate
            if 'bitrates' in format_info:
                print(f"\n{self.locale.t('bitrate')}:")
                for bk, br in format_info['bitrates'].items():
                    name = self.locale.t(br['name_key'])
                    default = br.get('default', False)
                    marker = " (default)" if default else ""
                    print(f"  {bk}. {br['bitrate']} ({name}){marker}")
                print(f"  0. {self.locale.t('default')}")
                choice = self._prompt_choice(self.locale.t('enter_choice'),
                                             [str(i) for i in range(0, len(format_info['bitrates'])+1)])
                if choice != "0":
                    conv_settings['bitrate'] = format_info['bitrates'][choice]['bitrate']
            # Quality (MP3, OGG)
            if 'qualities' in format_info:
                print(f"\n{self.locale.t('quality')}:")
                for qk, qv in format_info['qualities'].items():
                    name = self.locale.t(qv['name_key'])
                    default = qv.get('default', False)
                    marker = " (default)" if default else ""
                    print(f"  {qk}. {name} (level {qv['quality']}){marker}")
                print(f"  0. {self.locale.t('default')}")
                choice = self._prompt_choice(self.locale.t('enter_choice'),
                                             [str(i) for i in range(0, len(format_info['qualities'])+1)])
                if choice != "0":
                    conv_settings['quality'] = format_info['qualities'][choice]['quality']

        # Sample rate
        print(f"\n{self.locale.t('setting_sample_rate')}:")
        for srk, sr in SAMPLE_RATES.items():
            name = self.locale.t(sr['name_key'])
            default = sr.get('default', False)
            marker = " (default)" if default else ""
            print(f"  {srk}. {sr['rate']} Hz - {name}{marker}")
        print(f"  0. {self.locale.t('original')}")
        choice = self._prompt_choice(self.locale.t('enter_choice'),
                                     [str(i) for i in range(0, len(SAMPLE_RATES)+1)])
        if choice != "0":
            conv_settings['sample_rate'] = SAMPLE_RATES[choice]['rate']

        # Channels
        print(f"\n{self.locale.t('setting_channels')}:")
        for chk, ch in CHANNELS.items():
            name = self.locale.t(ch['name_key'])
            default = ch.get('default', False)
            marker = " (default)" if default else ""
            print(f"  {chk}. {ch['channels']} channels - {name}{marker}")
        print(f"  0. {self.locale.t('original')}")
        choice = self._prompt_choice(self.locale.t('enter_choice'),
                                     [str(i) for i in range(0, len(CHANNELS)+1)])
        if choice != "0":
            conv_settings['channels'] = CHANNELS[choice]['channels']

        # Step 5: Output folder
        self._print(f"\n[bold]{self.locale.t('output_folder')}[/bold]")
        default_output = os.path.join(folder, f"converted_{target_format.upper()}")
        print(f"{self.locale.t('default')}: {default_output}")
        print(f"{self.locale.t('enter_path')} (leave empty for default):")
        out_path = input("> ").strip()
        if not out_path:
            out_path = default_output
        out_path = os.path.expanduser(out_path)
        try:
            os.makedirs(out_path, exist_ok=True)
        except Exception as e:
            self._print(f"Error creating output folder: {e}", style="red")
            return

        # Step 6: Confirm
        if not self.settings.auto_confirm:
            print(f"\n[bold]Summary:[/bold]")
            print(f"  Source: {folder}")
            print(f"  Output: {out_path}")
            print(f"  Format: {target_format.upper()}")
            print(f"  Files: {len(files)}")
            if self.settings.dry_run:
                print(f"  [yellow]{self.locale.t('dry_run_mode')}[/yellow]")
            if not self._confirm(self.locale.t('confirm_start'), default=True):
                return

        # Step 7: Run conversion
        self._run_conversion(files, target_format, conv_settings, out_path)

        # Post-conversion options
        self._post_conversion_menu()

    def _post_conversion_menu(self):
        """Menu after conversion."""
        while True:
            clear_screen()
            print("\n" + "─" * 40)
            print(f"1. {self.locale.t('menu_start')}")
            print(f"2. {self.locale.t('back')}")
            print(f"0. {self.locale.t('menu_exit')}")
            choice = self._prompt_choice(self.locale.t('enter_choice'), ['0','1','2'])
            if choice == "0":
                sys.exit(0)
            elif choice == "1":
                self.run_conversion_workflow()
                return
            else:
                return

    # ========================================================================
    # Settings Menu
    # ========================================================================

    def settings_menu(self):
        """Show settings menu."""
        while True:
            clear_screen()
            if self.console:
                self.console.print(f"[bold]{self.locale.t('settings_title')}[/bold]")
            else:
                print(f"\n{self.locale.t('settings_title')}")

            # Простой список настроек без иконок, но с цветными номерами
            print("1. " + self.locale.t('setting_language') + f": {self.settings.language.upper()}")
            print("2. " + self.locale.t('setting_delete_original') + f": {self.settings.delete_original}")
            print("3. " + self.locale.t('setting_recursive') + f": {self.settings.recursive}")
            print("4. " + self.locale.t('setting_preserve_structure') + f": {self.settings.preserve_structure}")
            print("5. " + self.locale.t('setting_dry_run') + f": {self.settings.dry_run}")
            print("6. " + self.locale.t('setting_auto_confirm') + f": {self.settings.auto_confirm}")
            print("7. " + self.locale.t('setting_output_format') + f": {self.settings.output_format}")
            print("8. " + self.locale.t('setting_show_progress') + f": {self.settings.show_progress}")
            print("0. " + self.locale.t('back'))

            choice = self._prompt_choice(self.locale.t('enter_choice'), 
                                         [str(i) for i in range(0, 9)])
            if choice == "0":
                self.settings.save()
                return
            elif choice == "1":
                new_lang = "ru" if self.settings.language == "en" else "en"
                self.settings.language = new_lang
                self.locale.lang = new_lang
                self.settings.save()
            elif choice == "2":
                self.settings.delete_original = not self.settings.delete_original
                self.settings.save()
            elif choice == "3":
                self.settings.recursive = not self.settings.recursive
                self.settings.save()
            elif choice == "4":
                self.settings.preserve_structure = not self.settings.preserve_structure
                self.settings.save()
            elif choice == "5":
                self.settings.dry_run = not self.settings.dry_run
                self.settings.save()
            elif choice == "6":
                self.settings.auto_confirm = not self.settings.auto_confirm
                self.settings.save()
            elif choice == "7":
                print(f"\n{self.locale.t('setting_output_format')}:")
                for key, fmt in AUDIO_FORMATS.items():
                    name = self.locale.t(fmt['name_key'])
                    print(f"  {key}. {name}")
                fmt_choice = self._prompt_choice(self.locale.t('enter_choice'),
                                                 [str(i) for i in range(1, len(AUDIO_FORMATS)+1)])
                self.settings.output_format = AUDIO_FORMATS[fmt_choice]['key']
                self.settings.save()
            elif choice == "8":
                self.settings.show_progress = not self.settings.show_progress
                self.settings.save()

    # ========================================================================
    # About / FFmpeg Info
    # ========================================================================

    def show_about(self):
        clear_screen()
        if self.console:
            self.console.print(Panel(f"[bold]{self.locale.t('program_name')}[/bold]\n"
                                     f"{self.locale.t('about_version')}\n"
                                     f"{self.locale.t('about_desc')}\n\n"
                                     f"[bold]{self.locale.t('about_features')}:[/bold]\n"
                                     f"• {len(AUDIO_FORMATS)} output formats\n"
                                     f"• {len(SUPPORTED_INPUT_EXTENSIONS)} input formats\n"
                                     f"• Batch conversion, recursive scan\n"
                                     f"• Bit depth, sample rate, channel settings\n"
                                     f"• Dry-run mode, auto-confirm\n"
                                     f"• Russian/English interface\n"
                                     f"• Drag & drop support\n"
                                     f"• Progress bar (rich or fallback)\n\n"
                                     f"[bold]{self.locale.t('about_tech')}:[/bold]\n"
                                     f"• Python 3.6+, FFmpeg\n"
                                     f"• rich, tkinter (optional)",
                                     title=self.locale.t('about_title')))
        else:
            print(f"\n{self.locale.t('program_name')} {self.locale.t('about_version')}")
            print(self.locale.t('about_desc'))
            print(f"{self.locale.t('about_features')}: ...")
        input(f"\n{self.locale.t('press_enter')}")

    def show_ffmpeg_info(self):
        clear_screen()
        print(f"\n{self.locale.t('menu_ffmpeg')}:")
        if self.ffmpeg_available:
            try:
                result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, check=False)
                if result.returncode == 0:
                    lines = result.stdout.split('\n')[:5]
                    for line in lines:
                        print(line)
                else:
                    self._print(self.locale.t('error_ffmpeg'), style="red")
            except Exception:
                self._print(self.locale.t('error_ffmpeg'), style="red")
        else:
            self._print(self.locale.t('error_ffmpeg'), style="red")
        input(f"\n{self.locale.t('press_enter')}")

    # ========================================================================
    # Main Menu
    # ========================================================================

    def main_menu(self):
        """Main program loop."""
        while True:
            clear_screen()
            # Build header with current folder and dry-run status
            folder_info = self.source_folder if self.source_folder else "[dim]Not selected[/dim]"
            dry_run_status = "[bold red]ON[/bold red]" if self.settings.dry_run else "[bold green]OFF[/bold green]"
            header = (
                f"[dim]Folder:[/dim] [bold cyan]{folder_info}[/bold cyan]\n"
                f"[dim]Dry-Run:[/dim] {dry_run_status}"
            )
            if self.console:
                self.console.print(Panel(header, title=f"[bold magenta]{self.locale.t('program_name')}[/bold magenta]", expand=False, box=box.ROUNDED))
            else:
                print(f"\n{self.locale.t('program_name')}")
                print(f"Folder: {folder_info}")
                print(f"Dry-Run: {dry_run_status}")

            # Стильное меню без иконок, но с цветами
            if self.console:
                menu_table = Table(box=box.SIMPLE, show_header=False)
                menu_table.add_column("Key", style="bold yellow", justify="right")
                menu_table.add_column("Action", style="white")
                
                # Группировка с разделителями (пустые строки)
                menu_table.add_row("1", self.locale.t('menu_start'))
                menu_table.add_row("")
                menu_table.add_row("2", self.locale.t('menu_settings'))
                menu_table.add_row("3", self.locale.t('menu_ffmpeg'))
                menu_table.add_row("4", self.locale.t('menu_about'))
                menu_table.add_row("")
                menu_table.add_row("0", f"[dim]{self.locale.t('menu_exit')}[/dim]")
                
                self.console.print(menu_table)
            else:
                print("\n1. " + self.locale.t('menu_start'))
                print("2. " + self.locale.t('menu_settings'))
                print("3. " + self.locale.t('menu_ffmpeg'))
                print("4. " + self.locale.t('menu_about'))
                print("0. " + self.locale.t('menu_exit'))

            choice = self._prompt_choice(self.locale.t('enter_choice'), ['0','1','2','3','4'])
            if choice == "0":
                self._print("Goodbye!", style="green")
                break
            elif choice == "1":
                self.run_conversion_workflow()
            elif choice == "2":
                self.settings_menu()
            elif choice == "3":
                self.show_ffmpeg_info()
            elif choice == "4":
                self.show_about()


# =============================================================================
# Entry Point
# =============================================================================

def main():
    try:
        converter = AudioConverter()
        # Parse command line arguments (drag & drop)
        args = sys.argv[1:]
        if args:
            # First argument is path (can be folder or file)
            first_path = os.path.abspath(args[0])
            if os.path.isdir(first_path):
                folder = first_path
                files = None  # will scan folder later
            elif os.path.isfile(first_path):
                folder = os.path.dirname(first_path)
                files = [first_path]
            else:
                folder = None
                files = None

            if folder:
                converter.source_folder = folder
                # Ask user if they want to start conversion with this folder
                print(f"\n[bold]Detected drag & drop:[/bold] {folder}")
                if converter._confirm("Start conversion with this folder?", default=True):
                    converter.run_conversion_workflow(folder=folder, files=files)
                    return

        # No args or user cancelled – show main menu
        converter.main_menu()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except Exception as e:
        print(f"\nCritical error: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
