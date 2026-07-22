#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Audio Converter PRO v3.2 – Final (full redraw on each action)
Author: DJ Denicore
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
        'program_name': 'Audio Converter PRO',
        'main_title': 'MAIN MENU',
        'menu_start': 'Start conversion',
        'menu_settings': 'Settings',
        'menu_ffmpeg': 'FFmpeg info',
        'menu_about': 'About',
        'menu_exit': 'Exit',
        'settings_title': 'SETTINGS',
        'setting_language': 'Language',
        'setting_delete_original': 'Delete original files after conversion',
        'setting_recursive': 'Scan subfolders recursively',
        'setting_preserve_structure': 'Preserve folder structure in output',
        'setting_dry_run': 'Dry-run (no actual conversion)',
        'setting_auto_confirm': 'Auto-confirm all prompts',
        'setting_output_format': 'Default output format',
        'setting_show_progress': 'Show progress bar',
        'setting_preserve_cover': 'Preserve cover art (if present)',
        'setting_force_reencode': 'Force re-encode even if same format',
        'back': 'Back',
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
        'about_version': 'Version 3.2',
        'about_desc': 'Professional audio file converter powered by FFmpeg.',
        'about_features': 'Features',
        'about_tech': 'Technologies',
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
        'bit_depth_16': '16-bit integer',
        'bit_depth_24': '24-bit integer',
        'bit_depth_32': '32-bit integer',
        'bit_depth_32float': '32-bit float',
        'bit_depth_64float': '64-bit float',
        'flac_compression_fastest': 'Fastest',
        'flac_compression_standard': 'Standard',
        'flac_compression_best': 'Best compression',
        'bitrate_low': 'Low',
        'bitrate_medium': 'Medium',
        'bitrate_standard': 'Standard',
        'bitrate_high': 'High',
        'bitrate_very_high': 'Very High',
        'bitrate_max': 'Maximum',
        'mp3_quality_best': 'Best quality',
        'mp3_quality_worst': 'Worst quality',
        'ogg_quality_worst': 'Worst',
        'ogg_quality_best': 'Best',
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
        'setting_preserve_cover': 'Сохранять обложку (если есть)',
        'setting_force_reencode': 'Принудительное перекодирование (даже если формат совпадает)',
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
        'about_version': 'Версия 3.2',
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
    CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".audio_converter_config.json")

    def __init__(self):
        self.language = 'en'
        self.delete_original = False
        self.recursive = True
        self.preserve_structure = False
        self.dry_run = False
        self.auto_confirm = False
        self.output_format = 'flac'
        self.bitrate = '192k'
        self.sample_rate = 44100
        self.channels = 2
        self.show_progress = True
        self.preserve_cover = True
        self.force_reencode = True
        self.load()

    def load(self):
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
        try:
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.__dict__, f, indent=2, ensure_ascii=False)
        except Exception:
            pass


# =============================================================================
# Localization Helper
# =============================================================================

class Locale:
    def __init__(self, lang='en'):
        self.lang = lang

    def t(self, key):
        return TRANSLATIONS.get(self.lang, TRANSLATIONS['en']).get(key, key)


# =============================================================================
# Main Converter Class
# =============================================================================

class AudioConverter:
    def __init__(self):
        self.settings = Settings()
        self.locale = Locale(self.settings.language)
        self.console = Console() if RICH_AVAILABLE else None

        self.total_files = 0
        self.converted_files = 0
        self.failed_files = 0
        self.skipped_files = 0
        self.start_time = 0
        self.source_folder = ""

        self.ffmpeg_available = self._check_ffmpeg()

    # ====================================================================
    # Очистка экрана – максимально надёжная
    # ====================================================================
    def clear_screen(self):
        # Сначала пробуем rich (если доступен)
        if self.console and RICH_AVAILABLE:
            self.console.clear()
        else:
            # fallback – системная команда
            if os.name == 'nt':
                os.system('cls')
            else:
                os.system('clear')
        # Дополнительно сбрасываем буфер прокрутки (ANSI)
        sys.stdout.write('\033[3J')
        sys.stdout.flush()

    def _check_ffmpeg(self) -> bool:
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
            root = tk.Tk()
            root.withdraw()
            folder = filedialog.askdirectory(title=self.locale.t('select_folder'))
            root.destroy()
            return folder
        return None

    def _get_folder(self):
        folder = self._select_folder_gui()
        if folder:
            return folder
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
            cmd = [
                'ffprobe', '-v', 'quiet',
                '-print_format', 'json',
                '-show_streams', '-show_format',
                filepath
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            if result.returncode == 0:
                data = json.loads(result.stdout)
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
        ext = None
        for fmt in AUDIO_FORMATS.values():
            if fmt['key'] == target_format:
                ext = fmt['ext']
                break
        if not ext:
            ext = '.wav'

        base = os.path.splitext(os.path.basename(input_path))[0]
        safe = re.sub(r'[<>:"/\\|?*]', '_', base)
        safe = re.sub(r'\s+', ' ', safe).strip()

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
        try:
            codec = None
            for fmt in AUDIO_FORMATS.values():
                if fmt['key'] == target_format:
                    codec = fmt['codec']
                    break
            if not codec:
                return False, "Unknown format"

            cmd = ['ffmpeg', '-y', '-i', input_path, '-map_metadata', '0']

            cmd.extend(['-map', '0:a'])

            if self.settings.preserve_cover:
                cmd.extend(['-map', '0:v?'])
                cmd.extend(['-map', '0:t?'])
                cmd.extend(['-c:v', 'copy'])

            cmd.extend(['-c:a', codec])

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

            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            if result.returncode != 0:
                error_msg = result.stderr[:200] if result.stderr else "Unknown error"
                return False, f"FFmpeg error: {error_msg}"

            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                return True, "Success"
            else:
                return False, "Output file missing or empty"

        except Exception as e:
            return False, str(e)

    def _print_progress(self, current: int, total: int, filename: str = ""):
        if not self.settings.show_progress:
            return
        percent = (current / total) * 100
        bar_length = 40
        filled = int(bar_length * current // total)
        bar = '█' * filled + '░' * (bar_length - filled)
        max_name_len = 30
        if len(filename) > max_name_len:
            filename = filename[:max_name_len-3] + '...'
        sys.stdout.write(f'\r[{bar}] {percent:>5.1f}% ({current}/{total}) {filename}')
        sys.stdout.flush()

    def _run_conversion(self, files: List[str], target_format: str,
                        settings: Dict[str, Any], output_dir: str):
        self.total_files = len(files)
        self.converted_files = 0
        self.failed_files = 0
        self.skipped_files = 0
        self.start_time = time.time()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(output_dir, f"conversion_log_{timestamp}.txt")
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f"Conversion log - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Format: {target_format}\n")
            f.write(f"Settings: {json.dumps(settings, indent=2)}\n")
            f.write(f"Files: {self.total_files}\n")
            f.write("-" * 50 + "\n")

        if self.settings.dry_run:
            self._print(self.locale.t('dry_run_mode'), style="bold yellow")

        if self.settings.show_progress:
            if RICH_AVAILABLE and self.console:
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

            output_path = self._get_output_path(input_path, output_dir, target_format)

            input_ext = os.path.splitext(input_path)[1].lower()
            target_ext = None
            for fmt in AUDIO_FORMATS.values():
                if fmt['key'] == target_format:
                    target_ext = fmt['ext']
                    break
            if target_ext and input_ext == target_ext and not self.settings.delete_original and not self.settings.force_reencode:
                self.skipped_files += 1
                with open(log_file, 'a', encoding='utf-8') as f:
                    f.write(f"[SKIPPED] {filename} - already in target format (force_reencode disabled)\n")
                if use_rich_progress:
                    progress.advance(task)
                continue

            if self.settings.dry_run:
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

        if self.settings.show_progress and not use_rich_progress and not RICH_AVAILABLE:
            print()

        if use_rich_progress:
            progress.stop()

        elapsed = time.time() - self.start_time
        self._print_statistics(elapsed, log_file)

    def _print_statistics(self, elapsed: float, log_file: str):
        if self.console:
            from rich.table import Table
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
        self.clear_screen()
        if not self.ffmpeg_available:
            self._print(self.locale.t('error_ffmpeg'), style="red")
            return

        if folder is None:
            self._print(f"\n[bold]{self.locale.t('select_folder')}[/bold]")
            folder = self._get_folder()
            if not folder:
                return
        else:
            if not os.path.isdir(folder):
                self._print(self.locale.t('folder_not_found'), style="red")
                return
            self._print(f"\n[bold]Using folder:[/bold] {folder}")

        self.source_folder = folder

        if files is None:
            files = self._scan_directory(folder, self.settings.recursive)
        else:
            files = [f for f in files if os.path.isfile(f)]
            if not files:
                self._print(self.locale.t('no_files'), style="red")
                return

        if not files:
            self._print(self.locale.t('no_files'), style="red")
            return

        # ===== Показываем список файлов только по запросу =====
        self._print(f"\n{self.locale.t('files_found')}: [bold]{len(files)}[/bold]")
        if self.console and RICH_AVAILABLE:
            if Confirm.ask("Show first 10 files?", default=False):
                rows = []
                for f in files[:10]:
                    info = self._get_file_info(f)
                    size = self._format_file_size(info['size'])
                    dur = self._format_duration(info['duration'])
                    rows.append((os.path.basename(f), info['codec'].upper(), size, dur))
                table = Table(title=self.locale.t('file_list_title'))
                table.add_column("File")
                table.add_column("Codec")
                table.add_column("Size")
                table.add_column("Duration")
                for row in rows:
                    table.add_row(*row)
                self.console.print(table)
                if len(files) > 10:
                    self._print(f"... and {len(files)-10} more")
        else:
            print(f"\n{self.locale.t('file_list_title')}:")
            for f in files[:10]:
                print(f"  {os.path.basename(f)}")
            if len(files) > 10:
                print(f"... and {len(files)-10} more")
        # ===== Конец блока =====

        # Select output format (color-coded)
        self._print(f"\n[bold]{self.locale.t('select_format')}[/bold]")
        for key, fmt in AUDIO_FORMATS.items():
            name = self.locale.t(fmt['name_key'])
            desc = self.locale.t(fmt['desc_key'])
            default_marker = " [green](default)[/green]" if fmt['key'] == self.settings.output_format else ""
            self._print(f"[yellow][ {key} ][/yellow] [cyan]{name}[/cyan] - {desc}{default_marker}")
        self._print("[yellow][ 0 ][/yellow] " + self.locale.t('cancel'))
        choice = self._prompt_choice(self.locale.t('enter_choice'),
                                     [str(i) for i in range(0, len(AUDIO_FORMATS)+1)])
        if choice == "0":
            return
        format_info = AUDIO_FORMATS[choice]
        target_format = format_info['key']

        # Configure settings (color-coded)
        self._print(f"\n[bold]{self.locale.t('select_settings')}[/bold]")
        conv_settings = {}
        is_lossless = format_info.get('lossless', False)

        if is_lossless:
            if 'sample_formats' in format_info:
                self._print(f"\n[cyan]{self.locale.t('bit_depth')}:[/cyan]")
                for sk, sf in format_info['sample_formats'].items():
                    name = self.locale.t(sf['name_key'])
                    default = sf.get('default', False)
                    marker = " [green](default)[/green]" if default else ""
                    self._print(f"[yellow][ {sk} ][/yellow] {name}{marker}")
                self._print("[yellow][ 0 ][/yellow] " + self.locale.t('original'))
                choice = self._prompt_choice(self.locale.t('enter_choice'),
                                             [str(i) for i in range(0, len(format_info['sample_formats'])+1)])
                if choice != "0":
                    conv_settings['sample_fmt'] = format_info['sample_formats'][choice]['key']
            if 'compression_levels' in format_info:
                self._print(f"\n[cyan]{self.locale.t('compression')}:[/cyan]")
                for ck, cl in format_info['compression_levels'].items():
                    name = self.locale.t(cl['name_key'])
                    default = cl.get('default', False)
                    marker = " [green](default)[/green]" if default else ""
                    self._print(f"[yellow][ {ck} ][/yellow] {name} (level {cl['level']}){marker}")
                self._print("[yellow][ 0 ][/yellow] " + self.locale.t('default'))
                choice = self._prompt_choice(self.locale.t('enter_choice'),
                                             [str(i) for i in range(0, len(format_info['compression_levels'])+1)])
                if choice != "0":
                    conv_settings['compression_level'] = format_info['compression_levels'][choice]['level']
        else:
            if 'bitrates' in format_info:
                self._print(f"\n[cyan]{self.locale.t('bitrate')}:[/cyan]")
                for bk, br in format_info['bitrates'].items():
                    name = self.locale.t(br['name_key'])
                    default = br.get('default', False)
                    marker = " [green](default)[/green]" if default else ""
                    self._print(f"[yellow][ {bk} ][/yellow] [magenta]{br['bitrate']}[/magenta] ({name}){marker}")
                self._print("[yellow][ 0 ][/yellow] " + self.locale.t('default'))
                choice = self._prompt_choice(self.locale.t('enter_choice'),
                                             [str(i) for i in range(0, len(format_info['bitrates'])+1)])
                if choice != "0":
                    conv_settings['bitrate'] = format_info['bitrates'][choice]['bitrate']
            if 'qualities' in format_info:
                self._print(f"\n[cyan]{self.locale.t('quality')}:[/cyan]")
                for qk, qv in format_info['qualities'].items():
                    name = self.locale.t(qv['name_key'])
                    default = qv.get('default', False)
                    marker = " [green](default)[/green]" if default else ""
                    self._print(f"[yellow][ {qk} ][/yellow] {name} (level {qv['quality']}){marker}")
                self._print("[yellow][ 0 ][/yellow] " + self.locale.t('default'))
                choice = self._prompt_choice(self.locale.t('enter_choice'),
                                             [str(i) for i in range(0, len(format_info['qualities'])+1)])
                if choice != "0":
                    conv_settings['quality'] = format_info['qualities'][choice]['quality']

        # Sample rate (color-coded)
        self._print(f"\n[cyan]{self.locale.t('setting_sample_rate')}:[/cyan]")
        for srk, sr in SAMPLE_RATES.items():
            name = self.locale.t(sr['name_key'])
            default = sr.get('default', False)
            marker = " [green](default)[/green]" if default else ""
            self._print(f"[yellow][ {srk} ][/yellow] [magenta]{sr['rate']} Hz[/magenta] - {name}{marker}")
        self._print("[yellow][ 0 ][/yellow] " + self.locale.t('original'))
        choice = self._prompt_choice(self.locale.t('enter_choice'),
                                     [str(i) for i in range(0, len(SAMPLE_RATES)+1)])
        if choice != "0":
            conv_settings['sample_rate'] = SAMPLE_RATES[choice]['rate']

        # Channels (color-coded)
        self._print(f"\n[cyan]{self.locale.t('setting_channels')}:[/cyan]")
        for chk, ch in CHANNELS.items():
            name = self.locale.t(ch['name_key'])
            default = ch.get('default', False)
            marker = " [green](default)[/green]" if default else ""
            self._print(f"[yellow][ {chk} ][/yellow] [magenta]{ch['channels']} channels[/magenta] - {name}{marker}")
        self._print("[yellow][ 0 ][/yellow] " + self.locale.t('original'))
        choice = self._prompt_choice(self.locale.t('enter_choice'),
                                     [str(i) for i in range(0, len(CHANNELS)+1)])
        if choice != "0":
            conv_settings['channels'] = CHANNELS[choice]['channels']

        # Output folder
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

        # Confirm (color-coded summary)
        if not self.settings.auto_confirm:
            print(f"\n[bold]Summary:[/bold]")
            print(f"  [cyan]Source:[/cyan] {folder}")
            print(f"  [green]Output:[/green] {out_path}")
            print(f"  [yellow]Format:[/yellow] {target_format.upper()}")
            print(f"  [white]Files:[/white] {len(files)}")
            cover_status = "[green]Yes[/green]" if self.settings.preserve_cover else "[red]No[/red]"
            force_status = "[green]Yes[/green]" if self.settings.force_reencode else "[red]No[/red]"
            print(f"  [cyan]Preserve cover:[/cyan] {cover_status}")
            print(f"  [cyan]Force re-encode:[/cyan] {force_status}")
            if self.settings.dry_run:
                self._print(f"  [yellow]{self.locale.t('dry_run_mode')}[/yellow]")
            if not self._confirm(self.locale.t('confirm_start'), default=True):
                return

        self._run_conversion(files, target_format, conv_settings, out_path)
        self._post_conversion_menu()

    def _post_conversion_menu(self):
        while True:
            self.clear_screen()
            print("\n" + "─" * 40)
            self._print("[green][ 1 ][/green] " + self.locale.t('menu_start'))
            self._print("[blue][ 2 ][/blue] " + self.locale.t('back'))
            self._print("[red][ 0 ][/red] " + self.locale.t('menu_exit'))
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
        while True:
            self.clear_screen()
            if self.console:
                self.console.print(f"[bold blue]{self.locale.t('settings_title')}[/bold blue]")
            else:
                print(f"\n{self.locale.t('settings_title')}")

            # Все пункты в стиле [ 1 ] с цветными значениями
            self._print(f"[yellow][ 1 ][/yellow] {self.locale.t('setting_language')}: [bold cyan]{self.settings.language.upper()}[/bold cyan]")
            self._print(f"[yellow][ 2 ][/yellow] {self.locale.t('setting_delete_original')}: [bold cyan]{self.settings.delete_original}[/bold cyan]")
            self._print(f"[yellow][ 3 ][/yellow] {self.locale.t('setting_recursive')}: [bold cyan]{self.settings.recursive}[/bold cyan]")
            self._print(f"[yellow][ 4 ][/yellow] {self.locale.t('setting_preserve_structure')}: [bold cyan]{self.settings.preserve_structure}[/bold cyan]")
            self._print(f"[yellow][ 5 ][/yellow] {self.locale.t('setting_dry_run')}: [bold cyan]{self.settings.dry_run}[/bold cyan]")
            self._print(f"[yellow][ 6 ][/yellow] {self.locale.t('setting_auto_confirm')}: [bold cyan]{self.settings.auto_confirm}[/bold cyan]")
            self._print(f"[yellow][ 7 ][/yellow] {self.locale.t('setting_output_format')}: [bold cyan]{self.settings.output_format}[/bold cyan]")
            self._print(f"[yellow][ 8 ][/yellow] {self.locale.t('setting_show_progress')}: [bold cyan]{self.settings.show_progress}[/bold cyan]")
            self._print(f"[yellow][ 9 ][/yellow] {self.locale.t('setting_preserve_cover')}: [bold cyan]{self.settings.preserve_cover}[/bold cyan]")
            self._print(f"[yellow][ a ][/yellow] {self.locale.t('setting_force_reencode')}: [bold cyan]{self.settings.force_reencode}[/bold cyan]")
            self._print(f"[red][ 0 ][/red] {self.locale.t('back')}")

            choice = self._prompt_choice(self.locale.t('enter_choice'),
                                         ['0','1','2','3','4','5','6','7','8','9','a'])
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
                self._print(f"\n[cyan]{self.locale.t('setting_output_format')}:[/cyan]")
                for key, fmt in AUDIO_FORMATS.items():
                    name = self.locale.t(fmt['name_key'])
                    self._print(f"[yellow][ {key} ][/yellow] {name}")
                fmt_choice = self._prompt_choice(self.locale.t('enter_choice'),
                                                 [str(i) for i in range(1, len(AUDIO_FORMATS)+1)])
                self.settings.output_format = AUDIO_FORMATS[fmt_choice]['key']
                self.settings.save()
            elif choice == "8":
                self.settings.show_progress = not self.settings.show_progress
                self.settings.save()
            elif choice == "9":
                self.settings.preserve_cover = not self.settings.preserve_cover
                self.settings.save()
            elif choice == "a":
                self.settings.force_reencode = not self.settings.force_reencode
                self.settings.save()

    # ========================================================================
    # About / FFmpeg Info
    # ========================================================================

    def show_about(self):
        self.clear_screen()
        if self.console:
            self.console.print(Panel(
                f"[bold magenta]{self.locale.t('program_name')}[/bold magenta]\n"
                f"[cyan]{self.locale.t('about_version')}[/cyan]\n"
                f"{self.locale.t('about_desc')}\n\n"
                f"[bold green]{self.locale.t('about_features')}:[/bold green]\n"
                f"• {len(AUDIO_FORMATS)} output formats\n"
                f"• {len(SUPPORTED_INPUT_EXTENSIONS)} input formats\n"
                f"• Batch conversion, recursive scan\n"
                f"• Bit depth, sample rate, channel settings\n"
                f"• Dry-run mode, auto-confirm\n"
                f"• Russian/English interface\n"
                f"• Drag & drop support\n"
                f"• Progress bar (rich or fallback)\n"
                f"• Preserve cover art (toggle in settings)\n"
                f"• Force re-encode even if same format\n\n"
                f"[bold blue]{self.locale.t('about_tech')}:[/bold blue]\n"
                f"• Python 3.6+, FFmpeg\n"
                f"• rich, tkinter (optional)",
                title=self.locale.t('about_title')
            ))
        else:
            print(f"\n{self.locale.t('program_name')} {self.locale.t('about_version')}")
            print(self.locale.t('about_desc'))
        input(f"\n{self.locale.t('press_enter')}")

    def show_ffmpeg_info(self):
        self.clear_screen()
        self._print(f"\n[bold cyan]{self.locale.t('menu_ffmpeg')}:[/bold cyan]")
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
        while True:
            self.clear_screen()
            folder_info = self.source_folder if self.source_folder else "[dim]Not selected[/dim]"
            dry_run_status = "[bold red]ON[/bold red]" if self.settings.dry_run else "[bold green]OFF[/bold green]"
            cover_status = "[bold green]ON[/bold green]" if self.settings.preserve_cover else "[dim]OFF[/dim]"
            force_status = "[bold green]ON[/bold green]" if self.settings.force_reencode else "[dim]OFF[/dim]"
            header = (
                f"[dim]Folder:[/dim] [bold cyan]{folder_info}[/bold cyan]\n"
                f"[dim]Dry-Run:[/dim] {dry_run_status}\n"
                f"[dim]Preserve Cover:[/dim] {cover_status}\n"
                f"[dim]Force Re-encode:[/dim] {force_status}"
            )
            if self.console:
                self.console.print(Panel(header, title=f"[bold magenta]{self.locale.t('program_name')}[/bold magenta]", expand=False, box=box.ROUNDED))
            else:
                print(f"\n{self.locale.t('program_name')}")
                print(f"Folder: {folder_info}")
                print(f"Dry-Run: {dry_run_status}")
                print(f"Preserve Cover: {self.settings.preserve_cover}")
                print(f"Force Re-encode: {self.settings.force_reencode}")

            # Главное меню с цветами
            if self.console:
                menu_table = Table(box=box.SIMPLE, show_header=False)
                menu_table.add_column("Key", style="bold yellow", justify="right", width=6)
                menu_table.add_column("Action", style="white")
                menu_table.add_row("[ 1 ]", "[bold green]Start conversion[/bold green]")
                menu_table.add_row("", "")
                menu_table.add_row("[ 2 ]", "[bold blue]Settings[/bold blue]")
                menu_table.add_row("[ 3 ]", "[bold yellow]FFmpeg info[/bold yellow]")
                menu_table.add_row("[ 4 ]", "[bold cyan]About[/bold cyan]")
                menu_table.add_row("", "")
                menu_table.add_row("[ 0 ]", "[bold red]Exit[/bold red]")
                self.console.print(menu_table)
            else:
                print("\n[ 1 ] " + self.locale.t('menu_start'))
                print("")
                print("[ 2 ] " + self.locale.t('menu_settings'))
                print("[ 3 ] " + self.locale.t('menu_ffmpeg'))
                print("[ 4 ] " + self.locale.t('menu_about'))
                print("")
                print("[ 0 ] " + self.locale.t('menu_exit'))

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
        args = sys.argv[1:]
        if args:
            first_path = os.path.abspath(args[0])
            if os.path.isdir(first_path):
                folder = first_path
                files = None
            elif os.path.isfile(first_path):
                folder = os.path.dirname(first_path)
                files = [first_path]
            else:
                folder = None
                files = None

            if folder:
                converter.source_folder = folder
                print(f"\n[bold]Detected drag & drop:[/bold] {folder}")
                if converter._confirm("Start conversion with this folder?", default=True):
                    converter.run_conversion_workflow(folder=folder, files=files)
                    return

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