import re
import os

# Путь к папке с HTML
folder_path = r"C:\Users\Protogen\Desktop\cov"

# Регулярка: ищем ссылки вида https://web.archive.org/web/1234567890/https://www.mediafire.com/file/...
pattern = re.compile(r"https://web\.archive\.org/web/\d+/(https://www\.mediafire\.com/file/[^\s\"'>]+)")

# Файл для сохранения всех найденных ссылок
found_links_file = os.path.join(folder_path, "found_links.txt")

with open(found_links_file, "w", encoding="utf-8") as links_file:
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".html"):
            file_path = os.path.join(folder_path, filename)

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    html = f.read()
            except Exception as e:
                print(f"Не удалось открыть {filename}: {e}")
                continue

            # Находим все ссылки
            matches = pattern.findall(html)

            if matches:
                links_file.write(f"Файл: {filename}\n")
                for link in matches:
                    links_file.write(link + "\n")
                links_file.write("\n")

            # Заменяем на чистые ссылки (оставляем только https://www.mediafire.com/...)
            cleaned_html = pattern.sub(r"\1", html)

            # Сохраняем очищенный файл рядом
            output_path = os.path.join(folder_path, filename.replace(".html", "_cleaned.html"))
            try:
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(cleaned_html)
            except Exception as e:
                print(f"Не удалось записать {output_path}: {e}")
                continue

            print(f"{filename} -> {output_path} обработан")

print(f"Все ссылки сохранены в {found_links_file}")
print("Готово!")
