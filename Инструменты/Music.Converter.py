#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Audio Converter PRO v2.3 - Multi-language
Professional audio file converter with Russian and English support
"""

import os
import sys
import time
import re
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import subprocess

# Попытка импортировать ffmpeg-python
try:
    import ffmpeg
    FFMPEG_AVAILABLE = True
except ImportError:
    FFMPEG_AVAILABLE = False

# ============================================================================
# LOCALIZATION / ЛОКАЛИЗАЦИЯ
# ============================================================================

class Locale:
    """Class for managing localization"""
    
    # Translation dictionaries
    TRANSLATIONS = {
        'en': {
            # Common phrases
            'program_name': 'Audio Converter PRO',
            'welcome': 'Welcome',
            'exit': 'Exit',
            'back': 'Back',
            'cancel': 'Cancel',
            'continue': 'Continue',
            'yes': 'Yes',
            'no': 'No',
            'default': 'Default',
            'original': 'Original',
            'auto': 'Auto',
            'custom': 'Custom',
            
            # Colors
            'color_header': '\033[95m',
            'color_blue': '\033[94m',
            'color_cyan': '\033[96m',
            'color_green': '\033[92m',
            'color_yellow': '\033[93m',
            'color_red': '\033[91m',
            'color_end': '\033[0m',
            'color_bold': '\033[1m',
            
            # Menu
            'menu_main_title': 'MAIN MENU',
            'menu_start_conversion': 'Start conversion',
            'menu_about': 'About',
            'menu_ffmpeg_info': 'FFmpeg information',
            'menu_language': 'Language / Язык',
            'menu_exit': 'Exit',
            
            'menu_post_title': 'POST-CONVERSION ACTIONS',
            'menu_open_folder': 'Open results folder',
            'menu_show_log': 'Show log file',
            'menu_new_conversion': 'Start new conversion',
            'menu_return_main': 'Return to main menu',
            
            # Steps
            'step_select_folder': 'SELECT SOURCE FOLDER',
            'step_recursive_scan': 'RECURSIVE SCANNING',
            'step_find_files': 'FINDING AUDIO FILES',
            'step_select_format': 'SELECT CONVERSION FORMAT',
            'step_settings': 'SETTINGS CONFIGURATION',
            'step_output_folder': 'SELECT OUTPUT FOLDER',
            'step_additional_options': 'ADDITIONAL OPTIONS',
            'step_confirmation': 'CONFIRM SETTINGS',
            'step_conversion': 'CONVERTING FILES',
            
            # Messages
            'msg_scanning': 'Scanning...',
            'msg_files_found': 'Files found',
            'msg_converting': 'Converting...',
            'msg_completed': 'CONVERSION COMPLETED',
            'msg_success': 'Success',
            'msg_error': 'Error',
            'msg_warning': 'Warning',
            'msg_info': 'Info',
            'msg_processing': 'Processing',
            'msg_complete': 'Complete',
            'msg_cancelled': 'Cancelled',
            
            # Settings
            'settings_sample_rate': 'Sample rate',
            'settings_channels': 'Channels',
            'settings_bit_depth': 'Bit depth',
            'settings_bitrate': 'Bitrate',
            'settings_quality': 'Quality',
            'settings_compression': 'Compression',
            
            # Options
            'option_keep_original': 'Keep originals',
            'option_delete_original': 'Delete originals after conversion',
            'option_recursive_scan': 'Scan subfolders',
            
            # Formats
            'format_wav': 'WAV',
            'format_wav_desc': 'Waveform Audio (uncompressed)',
            'format_flac': 'FLAC',
            'format_flac_desc': 'Free Lossless Audio Codec',
            'format_mp3': 'MP3',
            'format_mp3_desc': 'MPEG Layer 3 Audio',
            'format_aac': 'AAC',
            'format_aac_desc': 'Advanced Audio Coding',
            'format_opus': 'Opus',
            'format_opus_desc': 'Opus Interactive Audio Codec',
            'format_ogg': 'OGG',
            'format_ogg_desc': 'Ogg Vorbis Audio',
            'format_m4a': 'M4A',
            'format_m4a_desc': 'MPEG-4 Audio',
            'format_alac': 'ALAC',
            'format_alac_desc': 'Apple Lossless Audio Codec',
            
            # Bit depth
            'bit_depth_16': '16-bit integer',
            'bit_depth_24': '24-bit integer',
            'bit_depth_32': '32-bit integer',
            'bit_depth_32float': '32-bit float',
            'bit_depth_64float': '64-bit float',
            
            # Sample rates
            'sample_rate_8k': '8 kHz - Telephone quality',
            'sample_rate_11k': '11.025 kHz',
            'sample_rate_16k': '16 kHz - VoIP',
            'sample_rate_22k': '22.05 kHz - Radio',
            'sample_rate_32k': '32 kHz - Digital radio',
            'sample_rate_44k': '44.1 kHz - CD quality',
            'sample_rate_48k': '48 kHz - DVD/Video',
            'sample_rate_88k': '88.2 kHz - Hi-Res',
            'sample_rate_96k': '96 kHz - Hi-Res',
            'sample_rate_176k': '176.4 kHz - Studio',
            'sample_rate_192k': '192 kHz - Studio',
            
            # Channels
            'channels_mono': 'Mono',
            'channels_stereo': 'Stereo',
            'channels_quad': 'Quad',
            'channels_51': '5.1 Surround',
            'channels_71': '7.1 Surround',
            
            # Bitrates
            'bitrate_low': 'Low quality',
            'bitrate_medium': 'Medium quality',
            'bitrate_standard': 'Standard quality',
            'bitrate_high': 'High quality',
            'bitrate_very_high': 'Very high quality',
            'bitrate_max': 'Maximum quality',
            
            # MP3 quality
            'mp3_quality_best': 'Best quality',
            'mp3_quality_worst': 'Worst quality',
            
            # OGG quality
            'ogg_quality_worst': 'Worst quality',
            'ogg_quality_best': 'Best quality',
            
            # FLAC compression
            'flac_compression_fastest': 'Fastest',
            'flac_compression_best': 'Best compression',
            'flac_compression_standard': 'Standard',
            
            # Confirmation
            'confirm_start': 'Start conversion?',
            'confirm_delete': 'Delete original files?',
            'confirm_recursive': 'Scan subfolders?',
            
            # Input
            'input_folder': 'Enter path to audio files folder',
            'input_output_folder': 'Enter path for output folder',
            'input_choice': 'Select option',
            'input_enter': 'Press Enter',
            
            # About
            'about_title': 'ABOUT',
            'about_version': 'Audio Converter PRO v2.3',
            'about_description': 'Professional audio file converter',
            'about_features': 'Features',
            'about_tech': 'Technologies used',
            'about_copyright': 'Copyright',
            
            # Errors
            'error_no_files': 'No audio files found',
            'error_no_folder': 'Folder does not exist',
            'error_ffmpeg': 'FFmpeg not found',
            'error_conversion': 'Conversion error',
            'error_permission': 'No permission',
            'error_invalid': 'Invalid input',
            
            # Success
            'success_converted': 'Conversion completed successfully',
            'success_folder_created': 'Folder created',
            'success_file_converted': 'File converted',
            
            # Statistics
            'stats_total': 'Total files',
            'stats_converted': 'Successful',
            'stats_failed': 'Failed',
            'stats_skipped': 'Skipped',
            'stats_time': 'Time spent',
            'stats_avg_time': 'Average time per file',
            'stats_success_rate': 'Success rate',
            
            # Log
            'log_file': 'Log file',
            'log_created': 'Log created',
            
            # Other
            'other_language': 'Language',
            'other_select_language': 'Select language',
            'other_loading': 'Loading...',
            'other_please_wait': 'Please wait',
        },
        'ru': {
            # Общие фразы
            'program_name': 'Audio Converter PRO',
            'welcome': 'Добро пожаловать',
            'exit': 'Выход',
            'back': 'Назад',
            'cancel': 'Отмена',
            'continue': 'Продолжить',
            'yes': 'Да',
            'no': 'Нет',
            'default': 'По умолчанию',
            'original': 'Оригинал',
            'auto': 'Авто',
            'custom': 'Свой',
            
            # Цвета
            'color_header': '\033[95m',
            'color_blue': '\033[94m',
            'color_cyan': '\033[96m',
            'color_green': '\033[92m',
            'color_yellow': '\033[93m',
            'color_red': '\033[91m',
            'color_end': '\033[0m',
            'color_bold': '\033[1m',
            
            # Меню
            'menu_main_title': 'ГЛАВНОЕ МЕНЮ',
            'menu_start_conversion': 'Начать конвертацию',
            'menu_about': 'О программе',
            'menu_ffmpeg_info': 'Информация о FFmpeg',
            'menu_language': 'Язык / Language',
            'menu_exit': 'Выход',
            
            'menu_post_title': 'ДЕЙСТВИЯ ПОСЛЕ КОНВЕРТАЦИИ',
            'menu_open_folder': 'Открыть папку с результатами',
            'menu_show_log': 'Показать лог-файл',
            'menu_new_conversion': 'Начать новую конвертацию',
            'menu_return_main': 'Вернуться в главное меню',
            
            # Шаги
            'step_select_folder': 'ВЫБОР ИСХОДНОЙ ПАПКИ',
            'step_recursive_scan': 'РЕКУРСИВНОЕ СКАНИРОВАНИЕ',
            'step_find_files': 'ПОИСК АУДИОФАЙЛОВ',
            'step_select_format': 'ВЫБОР ФОРМАТА КОНВЕРТАЦИИ',
            'step_settings': 'НАСТРОЙКА ПАРАМЕТРОВ',
            'step_output_folder': 'ВЫБОР ВЫХОДНОЙ ПАПКИ',
            'step_additional_options': 'ДОПОЛНИТЕЛЬНЫЕ ОПЦИИ',
            'step_confirmation': 'ПОДТВЕРЖДЕНИЕ НАСТРОЕК',
            'step_conversion': 'КОНВЕРТАЦИЯ ФАЙЛОВ',
            
            # Сообщения
            'msg_scanning': 'Сканирование...',
            'msg_files_found': 'Найдено файлов',
            'msg_converting': 'Конвертация...',
            'msg_completed': 'КОНВЕРТАЦИЯ ЗАВЕРШЕНА',
            'msg_success': 'Успешно',
            'msg_error': 'Ошибка',
            'msg_warning': 'Внимание',
            'msg_info': 'Информация',
            'msg_processing': 'Обработка',
            'msg_complete': 'Завершено',
            'msg_cancelled': 'Отменено',
            
            # Настройки
            'settings_sample_rate': 'Частота дискретизации',
            'settings_channels': 'Количество каналов',
            'settings_bit_depth': 'Битность',
            'settings_bitrate': 'Битрейт',
            'settings_quality': 'Качество',
            'settings_compression': 'Сжатие',
            
            # Опции
            'option_keep_original': 'Сохранить оригиналы',
            'option_delete_original': 'Удалить оригиналы после конвертации',
            'option_recursive_scan': 'Сканировать подпапки',
            
            # Форматы
            'format_wav': 'WAV',
            'format_wav_desc': 'Waveform Audio (без сжатия)',
            'format_flac': 'FLAC',
            'format_flac_desc': 'Free Lossless Audio Codec',
            'format_mp3': 'MP3',
            'format_mp3_desc': 'MPEG Layer 3 Audio',
            'format_aac': 'AAC',
            'format_aac_desc': 'Advanced Audio Coding',
            'format_opus': 'Opus',
            'format_opus_desc': 'Opus Interactive Audio Codec',
            'format_ogg': 'OGG',
            'format_ogg_desc': 'Ogg Vorbis Audio',
            'format_m4a': 'M4A',
            'format_m4a_desc': 'MPEG-4 Audio',
            'format_alac': 'ALAC',
            'format_alac_desc': 'Apple Lossless Audio Codec',
            
            # Битность
            'bit_depth_16': '16-bit целочисленный',
            'bit_depth_24': '24-bit целочисленный',
            'bit_depth_32': '32-bit целочисленный',
            'bit_depth_32float': '32-bit с плавающей точкой',
            'bit_depth_64float': '64-bit с плавающей точкой',
            
            # Частоты
            'sample_rate_8k': '8 kHz - Телефонное качество',
            'sample_rate_11k': '11.025 kHz',
            'sample_rate_16k': '16 kHz - VoIP',
            'sample_rate_22k': '22.05 kHz - Радио',
            'sample_rate_32k': '32 kHz - Цифровое радио',
            'sample_rate_44k': '44.1 kHz - CD качество',
            'sample_rate_48k': '48 kHz - DVD/Видео',
            'sample_rate_88k': '88.2 kHz - Hi-Res',
            'sample_rate_96k': '96 kHz - Hi-Res',
            'sample_rate_176k': '176.4 kHz - Studio',
            'sample_rate_192k': '192 kHz - Studio',
            
            # Каналы
            'channels_mono': 'Моно',
            'channels_stereo': 'Стерео',
            'channels_quad': 'Квадро',
            'channels_51': '5.1 Surround',
            'channels_71': '7.1 Surround',
            
            # Битрейты
            'bitrate_low': 'Низкое качество',
            'bitrate_medium': 'Среднее качество',
            'bitrate_standard': 'Стандартное качество',
            'bitrate_high': 'Высокое качество',
            'bitrate_very_high': 'Очень высокое качество',
            'bitrate_max': 'Максимальное качество',
            
            # Качество MP3
            'mp3_quality_best': 'Лучшее качество',
            'mp3_quality_worst': 'Худшее качество',
            
            # Качество OGG
            'ogg_quality_worst': 'Худшее качество',
            'ogg_quality_best': 'Лучшее качество',
            
            # Сжатие FLAC
            'flac_compression_fastest': 'Быстрее всего',
            'flac_compression_best': 'Лучшее сжатие',
            'flac_compression_standard': 'Стандарт',
            
            # Подтверждение
            'confirm_start': 'Начать конвертацию?',
            'confirm_delete': 'Удалить оригинальные файлы?',
            'confirm_recursive': 'Сканировать подпапки?',
            
            # Ввод
            'input_folder': 'Введите путь к папке с аудиофайлами',
            'input_output_folder': 'Введите путь для выходной папки',
            'input_choice': 'Выберите вариант',
            'input_enter': 'Нажмите Enter',
            
            # О программе
            'about_title': 'О ПРОГРАММЕ',
            'about_version': 'Audio Converter PRO v2.3',
            'about_description': 'Профессиональный конвертер аудиофайлов',
            'about_features': 'Возможности',
            'about_tech': 'Используемые технологии',
            'about_copyright': 'Авторские права',
            
            # Ошибки
            'error_no_files': 'Аудиофайлы не найдены',
            'error_no_folder': 'Папка не существует',
            'error_ffmpeg': 'FFmpeg не найден',
            'error_conversion': 'Ошибка конвертации',
            'error_permission': 'Нет доступа',
            'error_invalid': 'Неверный ввод',
            
            # Успех
            'success_converted': 'Конвертация завершена успешно',
            'success_folder_created': 'Папка создана',
            'success_file_converted': 'Файл сконвертирован',
            
            # Статистика
            'stats_total': 'Всего файлов',
            'stats_converted': 'Успешно',
            'stats_failed': 'Не удалось',
            'stats_skipped': 'Пропущено',
            'stats_time': 'Затрачено времени',
            'stats_avg_time': 'Среднее время на файл',
            'stats_success_rate': 'Успешность',
            
            # Лог
            'log_file': 'Лог-файл',
            'log_created': 'Лог создан',
            
            # Другое
            'other_language': 'Язык',
            'other_select_language': 'Выберите язык',
            'other_loading': 'Загрузка...',
            'other_please_wait': 'Пожалуйста, подождите',
        }
    }
    
    def __init__(self, language='en'):
        """Initialize localization"""
        self.language = language if language in self.TRANSLATIONS else 'en'
    
    def t(self, key: str) -> str:
        """Get translation by key"""
        return self.TRANSLATIONS.get(self.language, {}).get(key, key)
    
    def get_color(self, color_name: str) -> str:
        """Get color code"""
        color_key = f'color_{color_name}'
        return self.t(color_key) if color_key in self.TRANSLATIONS[self.language] else ''
    
    def format_menu_item(self, number: str, text: str, is_default: bool = False) -> str:
        """Format menu item"""
        default_marker = f" [{self.t('default')}]" if is_default else ""
        color = self.get_color('cyan')
        end_color = self.get_color('end')
        return f"{color}{number}.{end_color} {text}{default_marker}"
    
    def format_option(self, number: str, name: str, description: str = "", is_default: bool = False) -> str:
        """Format option"""
        default_marker = f" [{self.t('default')}]" if is_default else ""
        if description:
            return f"{number}. {name} - {description}{default_marker}"
        return f"{number}. {name}{default_marker}"

# ============================================================================
# CONFIGURATION / КОНФИГУРАЦИЯ
# ============================================================================

class Config:
    """Configuration class"""
    
    # Default settings
    DEFAULT_SETTINGS = {
        'wav': {
            'sample_fmt': 's16',  # 16-bit default
            'sample_rate': 44100,  # CD quality
            'channels': 2,  # Stereo
        },
        'flac': {
            'compression_level': 5,  # Standard compression
            'sample_rate': 44100,
            'channels': 2,
        },
        'mp3': {
            'bitrate': '192k',  # High quality
            'quality': 2,  # LAME quality
            'sample_rate': 44100,
            'channels': 2,
        },
        'aac': {
            'bitrate': '256k',  # High quality
            'sample_rate': 44100,
            'channels': 2,
        },
        'opus': {
            'bitrate': '128k',  # Good quality
            'sample_rate': 48000,  # Opus prefers 48kHz
            'channels': 2,
        },
        'ogg': {
            'quality': 3,  # Standard quality
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
    
    # Audio formats
    AUDIO_FORMATS = {
        '1': {
            'key': 'wav',
            'ext': '.wav',
            'codec': 'pcm_s16le',
            'name_key': 'format_wav',
            'desc_key': 'format_wav_desc',
            'lossless': True,
            'sample_formats': {
                '1': {'key': 's16', 'name_key': 'bit_depth_16', 'is_default': True},
                '2': {'key': 's24', 'name_key': 'bit_depth_24', 'is_default': False},
                '3': {'key': 's32', 'name_key': 'bit_depth_32', 'is_default': False},
                '4': {'key': 'flt', 'name_key': 'bit_depth_32float', 'is_default': False},
                '5': {'key': 'dbl', 'name_key': 'bit_depth_64float', 'is_default': False},
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
                '1': {'level': 0, 'name_key': 'flac_compression_fastest', 'is_default': False},
                '2': {'level': 1, 'name_key': 'flac_compression_fastest', 'is_default': False},
                '3': {'level': 2, 'name_key': 'flac_compression_fastest', 'is_default': False},
                '4': {'level': 3, 'name_key': 'flac_compression_fastest', 'is_default': False},
                '5': {'level': 4, 'name_key': 'flac_compression_standard', 'is_default': False},
                '6': {'level': 5, 'name_key': 'flac_compression_standard', 'is_default': True},
                '7': {'level': 6, 'name_key': 'flac_compression_best', 'is_default': False},
                '8': {'level': 7, 'name_key': 'flac_compression_best', 'is_default': False},
                '9': {'level': 8, 'name_key': 'flac_compression_best', 'is_default': False},
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
                '1': {'bitrate': '96k', 'name_key': 'bitrate_low', 'is_default': False},
                '2': {'bitrate': '128k', 'name_key': 'bitrate_medium', 'is_default': False},
                '3': {'bitrate': '160k', 'name_key': 'bitrate_standard', 'is_default': False},
                '4': {'bitrate': '192k', 'name_key': 'bitrate_high', 'is_default': True},
                '5': {'bitrate': '256k', 'name_key': 'bitrate_very_high', 'is_default': False},
                '6': {'bitrate': '320k', 'name_key': 'bitrate_max', 'is_default': False},
            },
            'qualities': {
                '1': {'quality': 0, 'name_key': 'mp3_quality_best', 'is_default': False},
                '2': {'quality': 1, 'name_key': 'mp3_quality_best', 'is_default': False},
                '3': {'quality': 2, 'name_key': 'mp3_quality_best', 'is_default': True},
                '4': {'quality': 3, 'name_key': 'mp3_quality_best', 'is_default': False},
                '5': {'quality': 4, 'name_key': 'mp3_quality_best', 'is_default': False},
                '6': {'quality': 5, 'name_key': 'mp3_quality_worst', 'is_default': False},
                '7': {'quality': 6, 'name_key': 'mp3_quality_worst', 'is_default': False},
                '8': {'quality': 7, 'name_key': 'mp3_quality_worst', 'is_default': False},
                '9': {'quality': 8, 'name_key': 'mp3_quality_worst', 'is_default': False},
                '10': {'quality': 9, 'name_key': 'mp3_quality_worst', 'is_default': False},
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
                '1': {'bitrate': '96k', 'name_key': 'bitrate_low', 'is_default': False},
                '2': {'bitrate': '128k', 'name_key': 'bitrate_medium', 'is_default': False},
                '3': {'bitrate': '160k', 'name_key': 'bitrate_standard', 'is_default': False},
                '4': {'bitrate': '192k', 'name_key': 'bitrate_high', 'is_default': False},
                '5': {'bitrate': '256k', 'name_key': 'bitrate_very_high', 'is_default': True},
                '6': {'bitrate': '320k', 'name_key': 'bitrate_max', 'is_default': False},
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
                '1': {'bitrate': '64k', 'name_key': 'bitrate_low', 'is_default': False},
                '2': {'bitrate': '96k', 'name_key': 'bitrate_medium', 'is_default': False},
                '3': {'bitrate': '128k', 'name_key': 'bitrate_standard', 'is_default': True},
                '4': {'bitrate': '160k', 'name_key': 'bitrate_high', 'is_default': False},
                '5': {'bitrate': '192k', 'name_key': 'bitrate_very_high', 'is_default': False},
                '6': {'bitrate': '256k', 'name_key': 'bitrate_max', 'is_default': False},
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
                '1': {'quality': -1, 'name_key': 'ogg_quality_worst', 'is_default': False},
                '2': {'quality': 0, 'name_key': 'ogg_quality_worst', 'is_default': False},
                '3': {'quality': 1, 'name_key': 'ogg_quality_worst', 'is_default': False},
                '4': {'quality': 2, 'name_key': 'ogg_quality_worst', 'is_default': False},
                '5': {'quality': 3, 'name_key': 'ogg_quality_worst', 'is_default': True},
                '6': {'quality': 4, 'name_key': 'ogg_quality_best', 'is_default': False},
                '7': {'quality': 5, 'name_key': 'ogg_quality_best', 'is_default': False},
                '8': {'quality': 6, 'name_key': 'ogg_quality_best', 'is_default': False},
                '9': {'quality': 7, 'name_key': 'ogg_quality_best', 'is_default': False},
                '10': {'quality': 8, 'name_key': 'ogg_quality_best', 'is_default': False},
                '11': {'quality': 9, 'name_key': 'ogg_quality_best', 'is_default': False},
                '12': {'quality': 10, 'name_key': 'ogg_quality_best', 'is_default': False},
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
                '1': {'bitrate': '96k', 'name_key': 'bitrate_low', 'is_default': False},
                '2': {'bitrate': '128k', 'name_key': 'bitrate_medium', 'is_default': False},
                '3': {'bitrate': '160k', 'name_key': 'bitrate_standard', 'is_default': False},
                '4': {'bitrate': '192k', 'name_key': 'bitrate_high', 'is_default': False},
                '5': {'bitrate': '256k', 'name_key': 'bitrate_very_high', 'is_default': True},
                '6': {'bitrate': '320k', 'name_key': 'bitrate_max', 'is_default': False},
            }
        },
        '8': {
            'key': 'alac',
            'ext': '.m4a',
            'codec': 'alac',
            'name_key': 'format_alac',
            'desc_key': 'format_alac_desc',
            'lossless': True
        }
    }
    
    # Sample rates
    SAMPLE_RATES = {
        '1': {'rate': 8000, 'name_key': 'sample_rate_8k', 'is_default': False},
        '2': {'rate': 11025, 'name_key': 'sample_rate_11k', 'is_default': False},
        '3': {'rate': 16000, 'name_key': 'sample_rate_16k', 'is_default': False},
        '4': {'rate': 22050, 'name_key': 'sample_rate_22k', 'is_default': False},
        '5': {'rate': 32000, 'name_key': 'sample_rate_32k', 'is_default': False},
        '6': {'rate': 44100, 'name_key': 'sample_rate_44k', 'is_default': True},
        '7': {'rate': 48000, 'name_key': 'sample_rate_48k', 'is_default': False},
        '8': {'rate': 88200, 'name_key': 'sample_rate_88k', 'is_default': False},
        '9': {'rate': 96000, 'name_key': 'sample_rate_96k', 'is_default': False},
        '10': {'rate': 176400, 'name_key': 'sample_rate_176k', 'is_default': False},
        '11': {'rate': 192000, 'name_key': 'sample_rate_192k', 'is_default': False},
    }
    
    # Channels
    CHANNELS = {
        '1': {'channels': 1, 'name_key': 'channels_mono', 'is_default': False},
        '2': {'channels': 2, 'name_key': 'channels_stereo', 'is_default': True},
        '3': {'channels': 4, 'name_key': 'channels_quad', 'is_default': False},
        '4': {'channels': 6, 'name_key': 'channels_51', 'is_default': False},
        '5': {'channels': 8, 'name_key': 'channels_71', 'is_default': False},
    }
    
    # Supported input formats
    SUPPORTED_INPUT_EXTENSIONS = [
        '.mp3', '.wav', '.flac', '.m4a', '.aac', '.ogg', '.opus',
        '.wma', '.aiff', '.aif', '.ape', '.wv', '.tta', '.mka',
        '.ra', '.rm', '.voc', '.au', '.snd', '.pcm', '.raw',
        '.mp4', '.m4v', '.mov', '.avi', '.mkv', '.webm', '.flv',
        '.wmv', '.3gp', '.3g2', '.mpeg', '.mpg', '.vob', '.ts',
        '.mts', '.m2ts', '.divx', '.xvid'
    ]
    
    @classmethod
    def get_default_setting(cls, format_key: str, setting: str):
        """Get default setting for format"""
        return cls.DEFAULT_SETTINGS.get(format_key, {}).get(setting)

# ============================================================================
# MAIN PROGRAM CLASS / ОСНОВНОЙ КЛАСС ПРОГРАММЫ
# ============================================================================

class AudioConverter:
    """Main audio converter class"""
    
    def __init__(self, language='en'):
        """Initialize converter"""
        self.locale = Locale(language)
        self.config = Config()
        self.total_files = 0
        self.converted_files = 0
        self.failed_files = 0
        self.skipped_files = 0
        self.start_time = 0
        self.current_step = 1
        self.total_steps = 9
    
    def clear_screen(self):
        """Clear console screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_banner(self):
        """Print program banner"""
        header_color = self.locale.get_color('header')
        cyan_color = self.locale.get_color('cyan')
        end_color = self.locale.get_color('end')
        
        banner = f"""
{cyan_color}{'='*70}
   █████╗ ██╗   ██╗███████╗██╗   ██╗ ██████╗ ██████╗ 
  ██╔══██╗██║   ██║██╔════╝██║   ██║██╔═══██╗██╔══██╗
  ███████║██║   ██║█████╗  ██║   ██║██║   ██║██████╔╝
  ██╔══██║██║   ██║██╔══╝  ╚██╗ ██╔╝██║   ██║██╔══██╗
  ██║  ██║╚██████╔╝███████╗ ╚████╔╝ ╚██████╔╝██║  ██║
  ╚═╝  ╚═╝ ╚═════╝ ╚══════╝  ╚═══╝   ╚═════╝ ╚═╝  ╚═╝
{'='*70}
            {header_color}{self.locale.t('program_name')} v2.3{cyan_color}
{'='*70}{end_color}
"""
        print(banner)
    
    def print_step(self, step_num: int, title_key: str):
        """Print step header"""
        header_color = self.locale.get_color('header')
        cyan_color = self.locale.get_color('cyan')
        end_color = self.locale.get_color('end')
        
        title = self.locale.t(title_key)
        print(f"\n{header_color}[STEP {step_num}/{self.total_steps}] {title}{end_color}")
        print(f"{cyan_color}{'─' * 60}{end_color}")
    
    def print_success(self, message: str):
        """Print success message"""
        green_color = self.locale.get_color('green')
        end_color = self.locale.get_color('end')
        print(f"{green_color}✓ {message}{end_color}")
    
    def print_error(self, message: str):
        """Print error message"""
        red_color = self.locale.get_color('red')
        end_color = self.locale.get_color('end')
        print(f"{red_color}✗ {message}{end_color}")
    
    def print_warning(self, message: str):
        """Print warning message"""
        yellow_color = self.locale.get_color('yellow')
        end_color = self.locale.get_color('end')
        print(f"{yellow_color}⚠ {message}{end_color}")
    
    def print_info(self, message: str):
        """Print info message"""
        cyan_color = self.locale.get_color('cyan')
        end_color = self.locale.get_color('end')
        print(f"{cyan_color}ℹ {message}{end_color}")
    
    def check_ffmpeg(self) -> bool:
        """Check if FFmpeg is available in system"""
        try:
            result = subprocess.run(
                ["ffmpeg", "-version"], 
                capture_output=True, 
                text=True, 
                check=False
            )
            
            if result.returncode == 0:
                self.print_success("FFmpeg found in system")
                return True
            else:
                self.print_error("FFmpeg not found or not working")
                return False
                
        except FileNotFoundError:
            self.print_error(self.locale.t('error_ffmpeg'))
            self.print_info("Windows: https://ffmpeg.org/download.html#build-windows")
            self.print_info("macOS: brew install ffmpeg")
            self.print_info("Ubuntu/Debian: sudo apt install ffmpeg")
            return False
    
    def get_menu_choice(self, prompt: str, min_choice: int, max_choice: int, allow_zero: bool = False) -> str:
        """Get menu choice from user"""
        while True:
            try:
                choice = input(f"\n{prompt} ").strip()
                
                if allow_zero and choice == "0":
                    return "0"
                
                if not choice:
                    self.print_error(self.locale.t('error_invalid'))
                    continue
                
                choice_num = int(choice)
                if min_choice <= choice_num <= max_choice:
                    return str(choice_num)
                else:
                    self.print_error(f"Enter a number from {min_choice} to {max_choice}")
            except ValueError:
                self.print_error("Please enter a number")
    
    def get_yes_no(self, prompt_key: str, default_yes: bool = False) -> bool:
        """Get yes/no answer from user"""
        prompt = self.locale.t(prompt_key)
        default_text = f" [{self.locale.t('yes') if default_yes else self.locale.t('no')}]"
        
        print(f"\n{prompt}{default_text}")
        print(f"1. {self.locale.t('yes')}")
        print(f"2. {self.locale.t('no')}")
        print(f"0. {self.locale.t('cancel')}")
        
        while True:
            choice = input(f"{self.locale.t('input_choice')}: ").strip()
            
            if choice == "":
                return default_yes
            
            if choice == "0":
                raise KeyboardInterrupt("Operation cancelled")
            
            if choice == "1":
                return True
            elif choice == "2":
                return False
            else:
                self.print_error(self.locale.t('error_invalid'))
    
    def scan_directory(self, directory: str, recursive: bool = False) -> List[str]:
        """Scan directory for audio files"""
        audio_files = []
        
        if not os.path.exists(directory):
            self.print_error(f"{self.locale.t('error_no_folder')}: {directory}")
            return []
        
        if not os.path.isdir(directory):
            self.print_error(f"Not a folder: {directory}")
            return []
        
        self.print_info(self.locale.t('msg_scanning'))
        
        if recursive:
            # Recursive scanning
            for root, dirs, files in os.walk(directory):
                for file in files:
                    file_ext = os.path.splitext(file)[1].lower()
                    if file_ext in self.config.SUPPORTED_INPUT_EXTENSIONS:
                        full_path = os.path.join(root, file)
                        audio_files.append(full_path)
        else:
            # Scan only current directory
            try:
                items = os.listdir(directory)
                for item in items:
                    full_path = os.path.join(directory, item)
                    if os.path.isfile(full_path):
                        file_ext = os.path.splitext(item)[1].lower()
                        if file_ext in self.config.SUPPORTED_INPUT_EXTENSIONS:
                            audio_files.append(full_path)
            except PermissionError:
                self.print_error(f"{self.locale.t('error_permission')}: {directory}")
                return []
        
        return audio_files
    
    def get_audio_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get audio file information"""
        try:
            if FFMPEG_AVAILABLE:
                # Use ffmpeg-python to get information
                probe = ffmpeg.probe(file_path)
                
                # Find audio stream
                audio_stream = None
                for stream in probe.get('streams', []):
                    if stream.get('codec_type') == 'audio':
                        audio_stream = stream
                        break
                
                if audio_stream:
                    info = {
                        'format': probe.get('format', {}).get('format_name', 'unknown'),
                        'duration': float(audio_stream.get('duration', probe.get('format', {}).get('duration', 0))),
                        'sample_rate': int(audio_stream.get('sample_rate', 0)),
                        'channels': int(audio_stream.get('channels', 0)),
                        'codec': audio_stream.get('codec_name', 'unknown'),
                        'bit_rate': int(audio_stream.get('bit_rate', 0)),
                        'size': int(probe.get('format', {}).get('size', 0)),
                        'filename': os.path.basename(file_path)
                    }
                    return info
            else:
                # Basic information without ffprobe
                try:
                    size = os.path.getsize(file_path)
                    info = {
                        'format': os.path.splitext(file_path)[1][1:].lower(),
                        'duration': 0,
                        'sample_rate': 44100,
                        'channels': 2,
                        'codec': 'unknown',
                        'bit_rate': 0,
                        'size': size,
                        'filename': os.path.basename(file_path)
                    }
                    return info
                except:
                    pass
        except Exception as e:
            self.print_warning(f"Failed to get file info {os.path.basename(file_path)}: {str(e)}")
        
        return None
    
    def format_file_size(self, size_bytes: int) -> str:
        """Format file size to readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.2f} {size_names[i]}"
    
    def format_duration(self, seconds: float) -> str:
        """Format duration to readable format"""
        if seconds == 0:
            return "0:00"
        
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes}:{secs:02d}"
    
    def display_files_info(self, files: List[str]):
        """Display information about found files"""
        if not files:
            self.print_error(self.locale.t('error_no_files'))
            return
        
        print(f"\n{self.locale.t('msg_files_found')}: {len(files)}")
        
        # Format statistics
        format_stats = {}
        total_size = 0
        total_duration = 0
        
        for file_path in files:
            info = self.get_audio_info(file_path)
            if info:
                ext = os.path.splitext(file_path)[1].lower()
                format_stats[ext] = format_stats.get(ext, 0) + 1
                total_size += info['size']
                total_duration += info['duration']
        
        # Show statistics
        if format_stats:
            print(f"\nFormat statistics:")
            for ext, count in format_stats.items():
                print(f"  {ext}: {count} files")
        
        print(f"\nGeneral information:")
        print(f"  Total size: {self.format_file_size(total_size)}")
        print(f"  Total duration: {self.format_duration(total_duration)}")
        
        # Show first few files
        print(f"\nFirst 5 files:")
        for i, file_path in enumerate(files[:5]):
            info = self.get_audio_info(file_path)
            if info:
                filename = info['filename']
                if len(filename) > 40:
                    filename = filename[:37] + "..."
                
                print(f"  {i+1}. {filename}")
                print(f"     Format: {info['format']}, "
                      f"Size: {self.format_file_size(info['size'])}, "
                      f"Duration: {self.format_duration(info['duration'])}")
        
        if len(files) > 5:
            print(f"  ... and {len(files) - 5} more files")
    
    def select_output_format(self) -> Optional[str]:
        """Select format for conversion"""
        print(f"\n{self.locale.t('step_select_format')}:")
        
        # Show available formats
        for key, fmt in self.config.AUDIO_FORMATS.items():
            name = self.locale.t(fmt['name_key'])
            desc = self.locale.t(fmt['desc_key'])
            print(self.locale.format_menu_item(key, f"{name} - {desc}"))
        
        print(f"\n0. {self.locale.t('cancel')}")
        
        choice = self.get_menu_choice(f"{self.locale.t('input_choice')} (0-{len(self.config.AUDIO_FORMATS)}):", 
                                     0, len(self.config.AUDIO_FORMATS), allow_zero=True)
        
        if choice == "0":
            self.print_info(self.locale.t('msg_cancelled'))
            return None
        
        selected_format = self.config.AUDIO_FORMATS[choice]
        format_name = self.locale.t(selected_format['name_key'])
        self.print_success(f"Selected format: {format_name}")
        return selected_format['key']
    
    def get_sample_format(self, target_format_key: str) -> Optional[str]:
        """Select bit depth for lossless formats"""
        # Find format information
        format_info = None
        for fmt in self.config.AUDIO_FORMATS.values():
            if fmt['key'] == target_format_key:
                format_info = fmt
                break
        
        if not format_info or 'sample_formats' not in format_info:
            return None
        
        format_name = self.locale.t(format_info['name_key'])
        print(f"\n{self.locale.t('settings_bit_depth')} for {format_name}:")
        
        # Show available bit depth options
        for key, sf in format_info['sample_formats'].items():
            name = self.locale.t(sf['name_key'])
            print(self.locale.format_option(key, name, is_default=sf.get('is_default', False)))
        
        print(f"\n0. {self.locale.t('original')}")
        
        choice = self.get_menu_choice(f"{self.locale.t('input_choice')} (0-{len(format_info['sample_formats'])}):",
                                     0, len(format_info['sample_formats']), allow_zero=True)
        
        if choice == "0":
            return None  # Keep original
        
        selected = format_info['sample_formats'][choice]
        return selected['key']
    
    def get_compression_level(self, target_format_key: str) -> Optional[int]:
        """Select compression level for lossless formats"""
        # Find format information
        format_info = None
        for fmt in self.config.AUDIO_FORMATS.values():
            if fmt['key'] == target_format_key:
                format_info = fmt
                break
        
        if not format_info or 'compression_levels' not in format_info:
            return None
        
        format_name = self.locale.t(format_info['name_key'])
        print(f"\n{self.locale.t('settings_compression')} for {format_name}:")
        
        # Show available compression levels
        for key, cl in format_info['compression_levels'].items():
            name = self.locale.t(cl['name_key'])
            print(self.locale.format_option(key, f"Level {cl['level']}", name, is_default=cl.get('is_default', False)))
        
        default_level = self.config.get_default_setting(target_format_key, 'compression_level')
        print(f"\n0. {self.locale.t('default')} (Level {default_level})")
        
        choice = self.get_menu_choice(f"{self.locale.t('input_choice')} (0-{len(format_info['compression_levels'])}):",
                                     0, len(format_info['compression_levels']), allow_zero=True)
        
        if choice == "0":
            return default_level
        
        selected = format_info['compression_levels'][choice]
        return selected['level']
    
    def get_bitrate(self, target_format_key: str) -> Optional[str]:
        """Select bitrate for lossy formats"""
        # Find format information
        format_info = None
        for fmt in self.config.AUDIO_FORMATS.values():
            if fmt['key'] == target_format_key:
                format_info = fmt
                break
        
        if not format_info or 'bitrates' not in format_info:
            return None
        
        format_name = self.locale.t(format_info['name_key'])
        print(f"\n{self.locale.t('settings_bitrate')} for {format_name}:")
        
        # Show available bitrates
        for key, br in format_info['bitrates'].items():
            name = self.locale.t(br['name_key'])
            print(self.locale.format_option(key, br['bitrate'], name, is_default=br.get('is_default', False)))
        
        default_bitrate = self.config.get_default_setting(target_format_key, 'bitrate')
        print(f"\n0. {self.locale.t('default')} ({default_bitrate})")
        
        choice = self.get_menu_choice(f"{self.locale.t('input_choice')} (0-{len(format_info['bitrates'])}):",
                                     0, len(format_info['bitrates']), allow_zero=True)
        
        if choice == "0":
            return default_bitrate
        
        selected = format_info['bitrates'][choice]
        return selected['bitrate']
    
    def get_quality(self, target_format_key: str) -> Optional[int]:
        """Select quality for some formats"""
        # Find format information
        format_info = None
        for fmt in self.config.AUDIO_FORMATS.values():
            if fmt['key'] == target_format_key:
                format_info = fmt
                break
        
        if not format_info or 'qualities' not in format_info:
            return None
        
        format_name = self.locale.t(format_info['name_key'])
        print(f"\n{self.locale.t('settings_quality')} for {format_name}:")
        
        # Show available quality levels
        for key, q in format_info['qualities'].items():
            name = self.locale.t(q['name_key'])
            print(self.locale.format_option(key, f"Level {q['quality']}", name, is_default=q.get('is_default', False)))
        
        default_quality = self.config.get_default_setting(target_format_key, 'quality')
        print(f"\n0. {self.locale.t('default')} (Level {default_quality})")
        
        choice = self.get_menu_choice(f"{self.locale.t('input_choice')} (0-{len(format_info['qualities'])}):",
                                     0, len(format_info['qualities']), allow_zero=True)
        
        if choice == "0":
            return default_quality
        
        selected = format_info['qualities'][choice]
        return selected['quality']
    
    def get_sample_rate(self) -> Optional[int]:
        """Select sample rate"""
        print(f"\n{self.locale.t('settings_sample_rate')}:")
        
        # Show available sample rates
        for key, sr in self.config.SAMPLE_RATES.items():
            name = self.locale.t(sr['name_key'])
            print(self.locale.format_option(key, f"{sr['rate']} Hz", name, is_default=sr.get('is_default', False)))
        
        print(f"\n0. {self.locale.t('original')}")
        
        choice = self.get_menu_choice(f"{self.locale.t('input_choice')} (0-{len(self.config.SAMPLE_RATES)}):",
                                     0, len(self.config.SAMPLE_RATES), allow_zero=True)
        
        if choice == "0":
            return None  # Keep original
        
        selected = self.config.SAMPLE_RATES[choice]
        return selected['rate']
    
    def get_channels(self) -> Optional[int]:
        """Select number of channels"""
        print(f"\n{self.locale.t('settings_channels')}:")
        
        # Show available channel options
        for key, ch in self.config.CHANNELS.items():
            name = self.locale.t(ch['name_key'])
            print(self.locale.format_option(key, f"{ch['channels']} channels", 
                  name, is_default=ch.get('is_default', False)))
        
        print(f"\n0. {self.locale.t('original')}")
        
        choice = self.get_menu_choice(f"{self.locale.t('input_choice')} (0-{len(self.config.CHANNELS)}):",
                                     0, len(self.config.CHANNELS), allow_zero=True)
        
        if choice == "0":
            return None  # Keep original
        
        selected = self.config.CHANNELS[choice]
        return selected['channels']
    
    def get_conversion_settings(self, target_format: str) -> Dict[str, Any]:
        """Get conversion settings for selected format"""
        settings = {}
        
        # Determine format type
        format_info = None
        for fmt in self.config.AUDIO_FORMATS.values():
            if fmt['key'] == target_format:
                format_info = fmt
                break
        
        if not format_info:
            return settings
        
        format_type = "lossless" if format_info.get('lossless', False) else "lossy"
        
        if format_type == "lossless":
            # Bit depth for lossless formats
            sample_fmt = self.get_sample_format(target_format)
            if sample_fmt:
                settings['sample_fmt'] = sample_fmt
            else:
                # Use default if not selected
                default_sample_fmt = self.config.get_default_setting(target_format, 'sample_fmt')
                if default_sample_fmt:
                    settings['sample_fmt'] = default_sample_fmt
            
            # Compression level for lossless formats
            compression_level = self.get_compression_level(target_format)
            if compression_level is not None:
                settings['compression_level'] = compression_level
        
        else:  # lossy formats
            # Bitrate for lossy formats
            bitrate = self.get_bitrate(target_format)
            if bitrate:
                settings['bitrate'] = bitrate
            
            # Quality for some formats
            quality = self.get_quality(target_format)
            if quality is not None:
                settings['quality'] = quality
        
        # Sample rate
        sample_rate = self.get_sample_rate()
        if sample_rate:
            settings['sample_rate'] = sample_rate
        else:
            # Use default if not selected
            default_sample_rate = self.config.get_default_setting(target_format, 'sample_rate')
            if default_sample_rate:
                settings['sample_rate'] = default_sample_rate
        
        # Channels
        channels = self.get_channels()
        if channels:
            settings['channels'] = channels
        else:
            # Use default if not selected
            default_channels = self.config.get_default_setting(target_format, 'channels')
            if default_channels:
                settings['channels'] = default_channels
        
        return settings
    
    def safe_filename(self, filename: str) -> str:
        """Create safe filename"""
        # Remove unsafe characters
        safe = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Remove extra spaces
        safe = re.sub(r'\s+', ' ', safe).strip()
        return safe
    
    def get_output_path(self, input_path: str, output_dir: str, target_format: str) -> str:
        """Generate output file path"""
        # Find correct extension for format
        target_ext = None
        for fmt in self.config.AUDIO_FORMATS.values():
            if fmt['key'] == target_format:
                target_ext = fmt['ext']
                break
        
        if not target_ext:
            target_ext = ".wav"  # fallback
        
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        safe_name = self.safe_filename(base_name)
        
        # Add counter if file already exists
        counter = 1
        original_name = safe_name
        output_path = os.path.join(output_dir, safe_name + target_ext)
        
        while os.path.exists(output_path):
            safe_name = f"{original_name}_{counter}"
            output_path = os.path.join(output_dir, safe_name + target_ext)
            counter += 1
        
        return output_path
    
    def convert_file(self, input_path: str, output_path: str, 
                    target_format: str, settings: Dict[str, Any]) -> Tuple[bool, str]:
        """Convert single file"""
        try:
            # Create directory for output file if needed
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Find codec for format
            codec = None
            for fmt in self.config.AUDIO_FORMATS.values():
                if fmt['key'] == target_format:
                    codec = fmt['codec']
                    break
            
            if not codec:
                return False, "Unknown format"
            
            if FFMPEG_AVAILABLE:
                # Use ffmpeg-python
                input_stream = ffmpeg.input(input_path)
                
                # Basic parameters
                output_args = {
                    'c:a': codec,
                    'map_metadata': '0'
                }
                
                # Add custom settings
                if 'sample_fmt' in settings:
                    output_args['sample_fmt'] = settings['sample_fmt']
                
                if 'sample_rate' in settings:
                    output_args['ar'] = str(settings['sample_rate'])
                
                if 'channels' in settings:
                    output_args['ac'] = str(settings['channels'])
                
                if 'bitrate' in settings:
                    output_args['b:a'] = settings['bitrate']
                
                if 'quality' in settings:
                    if target_format == 'mp3':
                        output_args['q:a'] = str(settings['quality'])
                    elif target_format == 'ogg':
                        output_args['q:a'] = str(settings['quality'])
                
                if 'compression_level' in settings:
                    output_args['compression_level'] = str(settings['compression_level'])
                
                # Create output stream
                output_stream = ffmpeg.output(
                    input_stream,
                    output_path,
                    **output_args
                )
                
                # Run conversion
                ffmpeg.run(
                    output_stream,
                    overwrite_output=True,
                    capture_stdout=True,
                    capture_stderr=True
                )
            else:
                # Use system ffmpeg via subprocess
                cmd = ['ffmpeg', '-y', '-i', input_path]
                
                # Basic parameters
                cmd.extend(['-c:a', codec])
                cmd.extend(['-map_metadata', '0'])
                
                # Add custom settings
                if 'sample_fmt' in settings:
                    cmd.extend(['-sample_fmt', settings['sample_fmt']])
                
                if 'sample_rate' in settings:
                    cmd.extend(['-ar', str(settings['sample_rate'])])
                
                if 'channels' in settings:
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
                
                # Run process
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    check=False
                )
                
                if result.returncode != 0:
                    error_msg = result.stderr[:200] if result.stderr else "Unknown error"
                    return False, f"FFmpeg error: {error_msg}"
            
            # Check result
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                return True, "Success"
            else:
                return False, "Output file not created or empty"
                
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def run_conversion(self, files: List[str], target_format: str, 
                      settings: Dict[str, Any], output_dir: str,
                      delete_original: bool = False):
        """Run conversion process for all files"""
        self.total_files = len(files)
        self.converted_files = 0
        self.failed_files = 0
        self.skipped_files = 0
        self.start_time = time.time()
        
        print(f"\n{self.locale.t('msg_converting')}")
        cyan_color = self.locale.get_color('cyan')
        end_color = self.locale.get_color('end')
        print(f"{cyan_color}{'='*60}{end_color}")
        
        # Find format name
        format_name = target_format.upper()
        for fmt in self.config.AUDIO_FORMATS.values():
            if fmt['key'] == target_format:
                format_name = self.locale.t(fmt['name_key'])
                break
        
        print(f"Format: {format_name}")
        print(f"Files: {self.total_files}")
        print(f"Output folder: {output_dir}")
        print(f"{cyan_color}{'='*60}{end_color}\n")
        
        # Create log file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(output_dir, f"conversion_log_{timestamp}.txt")
        
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f"Conversion log - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Format: {target_format}\n")
            f.write(f"Settings: {json.dumps(settings, indent=2)}\n")
            f.write(f"Files: {self.total_files}\n")
            f.write("-" * 50 + "\n")
        
        # Process files
        for i, input_path in enumerate(files, 1):
            try:
                # Generate output path
                output_path = self.get_output_path(input_path, output_dir, target_format)
                
                # Get file information
                file_info = self.get_audio_info(input_path)
                filename = os.path.basename(input_path)
                
                header_color = self.locale.get_color('header')
                end_color = self.locale.get_color('end')
                print(f"\n{header_color}[{i}/{self.total_files}] {filename}{end_color}")
                
                if file_info:
                    print(f"  Format: {file_info['codec'].upper()}, "
                          f"Size: {self.format_file_size(file_info['size'])}, "
                          f"Duration: {self.format_duration(file_info['duration'])}")
                
                # Check if trying to convert to same format
                input_ext = os.path.splitext(input_path)[1].lower()
                
                # Find target format extension
                target_ext = None
                for fmt in self.config.AUDIO_FORMATS.values():
                    if fmt['key'] == target_format:
                        target_ext = fmt['ext']
                        break
                
                if target_ext and input_ext == target_ext and not delete_original:
                    self.print_warning("File already in target format, skipping")
                    self.skipped_files += 1
                    with open(log_file, 'a', encoding='utf-8') as f:
                        f.write(f"[SKIPPED] {filename} - already in target format\n")
                    continue
                
                # Convert file
                success, message = self.convert_file(
                    input_path, output_path, target_format, settings
                )
                
                if success:
                    self.converted_files += 1
                    output_size = self.format_file_size(os.path.getsize(output_path))
                    self.print_success(f"Success: {os.path.basename(output_path)} ({output_size})")
                    
                    with open(log_file, 'a', encoding='utf-8') as f:
                        f.write(f"[SUCCESS] {filename} -> {os.path.basename(output_path)}\n")
                    
                    # Delete original if needed
                    if delete_original and input_path != output_path:
                        try:
                            os.remove(input_path)
                            self.print_info("Original deleted")
                            with open(log_file, 'a', encoding='utf-8') as f:
                                f.write(f"  Original deleted\n")
                        except Exception as e:
                            self.print_warning(f"Failed to delete original: {str(e)}")
                else:
                    self.failed_files += 1
                    self.print_error(f"Error: {message}")
                    
                    with open(log_file, 'a', encoding='utf-8') as f:
                        f.write(f"[ERROR] {filename}: {message}\n")
                
                # Update progress
                self.print_progress_bar(i)
                
            except KeyboardInterrupt:
                self.print_warning("\nConversion interrupted")
                with open(log_file, 'a', encoding='utf-8') as f:
                    f.write(f"\nConversion interrupted at file {i}/{self.total_files}\n")
                break
            except Exception as e:
                self.failed_files += 1
                self.print_error(f"Critical error: {str(e)}")
                with open(log_file, 'a', encoding='utf-8') as f:
                    f.write(f"[CRITICAL] {os.path.basename(input_path)}: {str(e)}\n")
        
        # Show statistics
        elapsed_time = time.time() - self.start_time
        self.print_statistics(elapsed_time, log_file)
        
        return log_file
    
    def print_progress_bar(self, current: int):
        """Print progress bar"""
        if self.total_files == 0:
            return
        
        progress = (current / self.total_files) * 100
        bar_length = 40
        filled_length = int(bar_length * current // self.total_files)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        
        cyan_color = self.locale.get_color('cyan')
        end_color = self.locale.get_color('end')
        print(f"\r{cyan_color}[{bar}] {progress:.1f}% ({current}/{self.total_files}){end_color}", end='')
        sys.stdout.flush()
    
    def print_statistics(self, elapsed_time: float, log_file: str):
        """Print conversion statistics"""
        green_color = self.locale.get_color('green')
        end_color = self.locale.get_color('end')
        bold_color = self.locale.get_color('bold')
        
        print(f"\n\n{green_color}{'='*60}{end_color}")
        print(f"{bold_color}{self.locale.t('msg_completed')}{end_color}")
        print(f"{green_color}{'='*60}{end_color}")
        
        print(f"\n{self.locale.t('stats_total')}:      {self.total_files}")
        print(f"{self.locale.t('stats_converted')}:         {self.converted_files}")
        print(f"{self.locale.t('stats_failed')}:        {self.failed_files}")
        print(f"{self.locale.t('stats_skipped')}:         {self.skipped_files}")
        
        if self.total_files > 0:
            success_rate = (self.converted_files / self.total_files) * 100
            print(f"{self.locale.t('stats_success_rate')}:        {success_rate:.1f}%")
        
        print(f"{self.locale.t('stats_time')}: {elapsed_time:.1f} seconds")
        
        if self.converted_files > 0:
            avg_time = elapsed_time / self.converted_files
            print(f"{self.locale.t('stats_avg_time')}: {avg_time:.1f} seconds")
        
        print(f"\n{self.locale.t('log_file')}: {log_file}")
        print(f"\n{green_color}{'='*60}{end_color}")
    
    def conversion_workflow(self):
        """Complete conversion workflow"""
        self.current_step = 1
        
        try:
            # Step 1: Select source folder
            self.print_step(self.current_step, 'step_select_folder')
            self.current_step += 1
            
            while True:
                print(f"\n{self.locale.t('input_folder')}:")
                print(f"{self.locale.t('input_enter')} to {self.locale.t('cancel').lower()}")
                
                folder = input("> ").strip()
                
                if not folder:
                    self.print_info(self.locale.t('msg_cancelled'))
                    return
                
                # Expand home directory if ~ is used
                folder = os.path.expanduser(folder)
                
                if not os.path.exists(folder):
                    self.print_error(f"{self.locale.t('error_no_folder')}: {folder}")
                    
                    try:
                        create = self.get_yes_no('confirm_recursive', False)
                        if create:
                            os.makedirs(folder, exist_ok=True)
                            self.print_success(f"{self.locale.t('success_folder_created')}: {folder}")
                            break
                    except KeyboardInterrupt:
                        return
                    except Exception as e:
                        self.print_error(f"Failed to create folder: {str(e)}")
                    continue
                
                if not os.path.isdir(folder):
                    self.print_error(f"Not a folder: {folder}")
                    continue
                
                break
            
            # Step 2: Recursive scanning
            self.print_step(self.current_step, 'step_recursive_scan')
            self.current_step += 1
            
            try:
                recursive = self.get_yes_no('confirm_recursive', False)
            except KeyboardInterrupt:
                self.print_info(self.locale.t('msg_cancelled'))
                return
            
            # Step 3: Find files
            self.print_step(self.current_step, 'step_find_files')
            self.current_step += 1
            
            files = self.scan_directory(folder, recursive)
            
            if not files:
                self.print_error(self.locale.t('error_no_files'))
                supported_formats = ', '.join(self.config.SUPPORTED_INPUT_EXTENSIONS[:10])
                self.print_info(f"Supported formats: {supported_formats}...")
                
                try:
                    retry = self.get_yes_no('confirm_recursive', False)
                    if retry:
                        return self.conversion_workflow()
                    else:
                        return
                except KeyboardInterrupt:
                    return
            
            # Show file information
            self.display_files_info(files)
            
            try:
                continue_conversion = self.get_yes_no('confirm_start', True)
                if not continue_conversion:
                    self.print_info(self.locale.t('msg_cancelled'))
                    return
            except KeyboardInterrupt:
                return
            
            # Step 4: Select format
            self.print_step(self.current_step, 'step_select_format')
            self.current_step += 1
            
            target_format = self.select_output_format()
            if not target_format:
                return
            
            # Step 5: Configure settings
            self.print_step(self.current_step, 'step_settings')
            self.current_step += 1
            
            settings = self.get_conversion_settings(target_format)
            
            # Step 6: Select output folder
            self.print_step(self.current_step, 'step_output_folder')
            self.current_step += 1
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Find format name for folder
            format_name = target_format.upper()
            for fmt in self.config.AUDIO_FORMATS.values():
                if fmt['key'] == target_format:
                    format_name = self.locale.t(fmt['name_key'])
                    break
            
            default_output = os.path.join(folder, f"converted_{format_name}_{timestamp}")
            
            print(f"\n{self.locale.t('input_output_folder')}:")
            print(f"{self.locale.t('default')}: {default_output}")
            print(f"{self.locale.t('input_enter')} for {self.locale.t('default').lower()}")
            
            output_dir = input("> ").strip()
            
            if not output_dir:
                output_dir = default_output
            
            # Create output folder
            try:
                os.makedirs(output_dir, exist_ok=True)
                self.print_success(f"{self.locale.t('success_folder_created')}: {output_dir}")
            except Exception as e:
                self.print_error(f"Failed to create folder: {str(e)}")
                return
            
            # Step 7: Additional options
            self.print_step(self.current_step, 'step_additional_options')
            self.current_step += 1
            
            try:
                delete_original = self.get_yes_no('confirm_delete', False)
            except KeyboardInterrupt:
                self.print_info(self.locale.t('msg_cancelled'))
                return
            
            # Step 8: Confirmation
            self.print_step(self.current_step, 'step_confirmation')
            self.current_step += 1
            
            cyan_color = self.locale.get_color('cyan')
            end_color = self.locale.get_color('end')
            bold_color = self.locale.get_color('bold')
            
            print(f"\n{bold_color}CONVERSION SETTINGS:{end_color}")
            print(f"{cyan_color}{'='*50}{end_color}")
            
            # Find format name
            format_display_name = target_format.upper()
            for fmt in self.config.AUDIO_FORMATS.values():
                if fmt['key'] == target_format:
                    format_display_name = self.locale.t(fmt['name_key'])
                    break
            
            print(f"  Source folder:    {folder}")
            print(f"  Output folder:    {output_dir}")
            print(f"  Format:           {format_display_name}")
            print(f"  Files:            {len(files)}")
            
            if 'sample_fmt' in settings:
                print(f"  Bit depth:        {settings['sample_fmt']}")
            if 'sample_rate' in settings:
                print(f"  Sample rate:      {settings['sample_rate']} Hz")
            if 'channels' in settings:
                print(f"  Channels:         {settings['channels']}")
            if 'bitrate' in settings:
                print(f"  Bitrate:          {settings['bitrate']}")
            if 'quality' in settings:
                print(f"  Quality:          {settings['quality']}")
            if 'compression_level' in settings:
                print(f"  Compression:      {settings['compression_level']}")
            
            print(f"  Delete originals: {'Yes' if delete_original else 'No'}")
            
            print(f"{cyan_color}{'='*50}{end_color}")
            
            try:
                confirm = self.get_yes_no('confirm_start', True)
                if not confirm:
                    self.print_info(self.locale.t('msg_cancelled'))
                    return
            except KeyboardInterrupt:
                return
            
            # Step 9: Conversion
            self.print_step(self.current_step, 'step_conversion')
            
            log_file = self.run_conversion(files, target_format, settings, output_dir, delete_original)
            
            # Post-conversion menu
            self.post_conversion_menu(output_dir, log_file)
            
        except KeyboardInterrupt:
            self.print_warning("\nWorkflow interrupted")
        except Exception as e:
            self.print_error(f"Error in workflow: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def post_conversion_menu(self, output_dir: str, log_file: str):
        """Post-conversion menu"""
        while True:
            print(f"\n{self.locale.t('menu_post_title')}:")
            print(f"1. 📂 {self.locale.t('menu_open_folder')}")
            print(f"2. 📄 {self.locale.t('menu_show_log')}")
            print(f"3. 🔄 {self.locale.t('menu_new_conversion')}")
            print(f"4. 🏠 {self.locale.t('menu_return_main')}")
            print(f"0. 🚪 {self.locale.t('exit')}")
            
            choice = self.get_menu_choice(f"{self.locale.t('input_choice')} (0-4):", 0, 4, allow_zero=True)
            
            if choice == "1":
                self.open_folder(output_dir)
            elif choice == "2":
                self.show_log_file(log_file)
            elif choice == "3":
                return self.conversion_workflow()
            elif choice == "4":
                return
            elif choice == "0":
                self.print_success("Thank you for using the program!")
                time.sleep(1)
                sys.exit(0)
    
    def open_folder(self, folder: str):
        """Open folder in file explorer"""
        try:
            if os.name == 'nt':  # Windows
                os.startfile(folder)
            elif os.name == 'posix':  # macOS, Linux
                if sys.platform == 'darwin':  # macOS
                    subprocess.run(['open', folder], check=False)
                else:  # Linux
                    subprocess.run(['xdg-open', folder], check=False)
            self.print_success("Folder opened")
        except Exception as e:
            self.print_error(f"Failed to open folder: {str(e)}")
    
    def show_log_file(self, log_file: str):
        """Show log file contents"""
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                cyan_color = self.locale.get_color('cyan')
                end_color = self.locale.get_color('end')
                bold_color = self.locale.get_color('bold')
                
                print(f"\n{bold_color}LOG FILE CONTENTS:{end_color}")
                print(f"{cyan_color}{'='*70}{end_color}")
                print(content)
                print(f"{cyan_color}{'='*70}{end_color}")
                
                input(f"\n{self.locale.t('input_enter')} to continue...")
            except Exception as e:
                self.print_error(f"Failed to read log file: {str(e)}")
        else:
            self.print_error("Log file not found")
    
    def show_about(self):
        """Show about information"""
        self.clear_screen()
        self.print_banner()
        
        cyan_color = self.locale.get_color('cyan')
        end_color = self.locale.get_color('end')
        bold_color = self.locale.get_color('bold')
        
        print(f"{bold_color}{self.locale.t('about_title')}{end_color}")
        print(f"{cyan_color}{'='*60}{end_color}")
        
        print(f"\n{self.locale.t('about_version')}")
        print(f"{self.locale.t('about_description')}")
        
        print(f"\n{bold_color}{self.locale.t('about_features')}:{end_color}")
        print(f"• Conversion between {len(self.config.AUDIO_FORMATS)} audio formats")
        print(f"• Support for {len(self.config.SUPPORTED_INPUT_EXTENSIONS)} input formats")
        print(f"• Batch file processing")
        print(f"• Recursive folder scanning")
        print(f"• Bit depth, sample rate and channel configuration")
        print(f"• Metadata preservation")
        print(f"• Detailed logging")
        print(f"• Original file deletion after conversion")
        print(f"• Russian and English language support")
        
        print(f"\n{bold_color}{self.locale.t('about_tech')}:{end_color}")
        print(f"• Python 3.6+")
        print(f"• FFmpeg")
        print(f"• ffmpeg-python library")
        
        print(f"\n{bold_color}{self.locale.t('about_copyright')}:{end_color}")
        print(f"© 2024 Audio Converter PRO")
        print(f"For personal and commercial use")
        
        print(f"\n{cyan_color}{'='*60}{end_color}")
        input(f"\n{self.locale.t('input_enter')} to return to menu...")
    
    def show_ffmpeg_info(self):
        """Show FFmpeg information"""
        self.clear_screen()
        self.print_banner()
        
        cyan_color = self.locale.get_color('cyan')
        end_color = self.locale.get_color('end')
        bold_color = self.locale.get_color('bold')
        
        print(f"{bold_color}FFMPEG INFORMATION:{end_color}")
        print(f"{cyan_color}{'='*60}{end_color}")
        
        # Check FFmpeg availability
        if self.check_ffmpeg():
            # Get FFmpeg version
            try:
                result = subprocess.run(
                    ["ffmpeg", "-version"], 
                    capture_output=True, 
                    text=True, 
                    check=False
                )
                if result.returncode == 0:
                    lines = result.stdout.split('\n')
                    if lines:
                        print(f"\n{bold_color}FFmpeg version:{end_color}")
                        print(f"{lines[0]}")
            except:
                pass
        else:
            self.print_error(self.locale.t('error_ffmpeg'))
            print(f"\n{bold_color}Installation instructions:{end_color}")
            print("1. Windows: Download from https://ffmpeg.org/download.html")
            print("2. macOS: Install via Homebrew: brew install ffmpeg")
            print("3. Linux: Install via package manager")
            print("   Ubuntu/Debian: sudo apt install ffmpeg")
            print("   Fedora: sudo dnf install ffmpeg")
            print("   Arch: sudo pacman -S ffmpeg")
        
        print(f"\n{cyan_color}{'='*60}{end_color}")
        input(f"\n{self.locale.t('input_enter')} to return to menu...")
    
    def select_language(self):
        """Select interface language"""
        self.clear_screen()
        self.print_banner()
        
        cyan_color = self.locale.get_color('cyan')
        end_color = self.locale.get_color('end')
        bold_color = self.locale.get_color('bold')
        
        print(f"{bold_color}{self.locale.t('other_select_language')}:{end_color}")
        print(f"{cyan_color}{'='*60}{end_color}")
        
        print(f"\n1. 🇺🇸 English (Английский)")
        print(f"2. 🇷🇺 Русский (Russian)")
        print(f"\n0. {self.locale.t('back')}")
        
        choice = self.get_menu_choice(f"{self.locale.t('input_choice')} (0-2):", 0, 2, allow_zero=True)
        
        if choice == "1":
            self.locale = Locale('en')
            self.print_success("Language changed to English")
            time.sleep(1)
        elif choice == "2":
            self.locale = Locale('ru')
            self.print_success("Язык изменен на русский")
            time.sleep(1)
    
    def main_menu(self):
        """Main program menu"""
        while True:
            self.clear_screen()
            self.print_banner()
            
            # Check FFmpeg on first run
            if not hasattr(self, '_ffmpeg_checked'):
                if not self.check_ffmpeg():
                    self.print_warning("FFmpeg is required for program operation")
                    
                    print(f"\nContinue without full functionality?")
                    print(f"1. {self.locale.t('yes')}")
                    print(f"2. {self.locale.t('no')}")
                    
                    choice = self.get_menu_choice(f"{self.locale.t('input_choice')} (1-2):", 1, 2)
                    if choice != "1":
                        print(f"\nProgram cannot work without FFmpeg")
                        input(f"\n{self.locale.t('input_enter')} to exit...")
                        sys.exit(1)
                self._ffmpeg_checked = True
            
            print(f"{self.locale.t('menu_main_title')}:")
            print(f"1. 🎵 {self.locale.t('menu_start_conversion')}")
            print(f"2. ℹ️  {self.locale.t('menu_about')}")
            print(f"3. 🔧 {self.locale.t('menu_ffmpeg_info')}")
            print(f"4. 🌐 {self.locale.t('menu_language')}")
            print(f"0. 🚪 {self.locale.t('menu_exit')}")
            
            choice = self.get_menu_choice(f"{self.locale.t('input_choice')} (0-4):", 0, 4, allow_zero=True)
            
            if choice == "1":
                self.conversion_workflow()
            elif choice == "2":
                self.show_about()
            elif choice == "3":
                self.show_ffmpeg_info()
            elif choice == "4":
                self.select_language()
            elif choice == "0":
                self.print_success("Thank you for using the program!")
                time.sleep(1)
                break

def main():
    """Main program function"""
    try:
        # Always start with English language
        converter = AudioConverter('en')
        converter.main_menu()
    except KeyboardInterrupt:
        print(f"\n\nProgram terminated by user")
    except Exception as e:
        print(f"\nCritical error: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
