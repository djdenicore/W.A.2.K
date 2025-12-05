import os
import shutil
import json
from bs4 import BeautifulSoup

# Загружаем конфиг
with open("config.json", "r", encoding="utf-8") as f:
    CONFIG = json.load(f)

INPUT_DIR = CONFIG["input_dir"]
OUTPUT_DIR = CONFIG["output_dir"]

def clean_and_split_html(src_path, dst_html, dst_css):
    """Чистим HTML и выносим встроенные стили в отдельный CSS"""
    with open(src_path, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")

    # Удаляем мусорные скрипты
    if CONFIG.get("remove_scripts", True):
        for script in soup.find_all("script"):
            script_text = str(script)
            if (
                "wombat" in script_text
                or "archive.org" in script_text
                or "RufflePlayer" in script_text
            ):
                script.decompose()

    # Удаляем архивные стили
    if CONFIG.get("remove_archive_css", True):
        for link in soup.find_all("link", href=True):
            href = link["href"]
            if "archive.org" in href or "banner-styles" in href or "iconochive" in href:
                link.decompose()

    # Удаляем комментарии Wayback
    for comment in soup.find_all(string=lambda text: isinstance(text, str) and "web.archive.org" in text):
        comment.extract()

    # Вытаскиваем встроенные стили
    styles = []
    for style_tag in soup.find_all("style"):
        styles.append(style_tag.get_text())
        style_tag.decompose()

    # Если есть стили — сохраняем в отдельный CSS
    if styles:
        os.makedirs(os.path.dirname(dst_css), exist_ok=True)
        with open(dst_css, "w", encoding="utf-8") as f:
            f.write("\n\n".join(styles))

        # Подключаем CSS в HTML
        new_link = soup.new_tag(
            "link",
            rel="stylesheet",
            href=f"/{CONFIG['css_dir']}/{os.path.basename(dst_css)}"
        )
        if soup.head:
            soup.head.append(new_link)

    # Сохраняем очищенный HTML
    os.makedirs(os.path.dirname(dst_html), exist_ok=True)
    with open(dst_html, "w", encoding="utf-8") as f:
        f.write(str(soup))

def cleaner_splitter():
    """Основная функция: чистим и сортируем файлы"""
    # очищаем только выходную папку
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)

    html_dir = os.path.join(OUTPUT_DIR, CONFIG["html_dir"])
    css_dir  = os.path.join(OUTPUT_DIR, CONFIG["css_dir"])
    os.makedirs(html_dir)
    os.makedirs(css_dir)

    # Обход всех файлов
    for root, _, files in os.walk(INPUT_DIR):
        for file in files:
            if file.lower().endswith((".html", ".htm")):
                src_path = os.path.join(root, file)

                if file.lower() == "index.html":
                    dst_html = os.path.join(OUTPUT_DIR, "index.html")
                    dst_css  = os.path.join(css_dir, "index.css")
                else:
                    dst_html = os.path.join(html_dir, file)
                    dst_css  = os.path.join(css_dir, file.replace(".html", ".css"))

                print("Обрабатываю:", src_path)
                clean_and_split_html(src_path, dst_html, dst_css)

    print(f"✅ HTML очищен и стили вынесены в {OUTPUT_DIR}")

if __name__ == "__main__":
    cleaner_splitter()
