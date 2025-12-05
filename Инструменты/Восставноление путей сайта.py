import re
import os

# Путь к папке с HTML
folder_path = r"C:\Users\Protogen\Desktop\Новая папка (2)"

# Регулярка: ищем пути типа ../../../../20231008164221im_/https_/heckscaper.com/backcat/cataimg/whatareyou.png
# Захватываем весь путь, потом будем использовать только имя файла
pattern = re.compile(r'(?:\.\./)+\d+im_/https_/[^\s"\'<>]+/([^/]+\.[a-zA-Z0-9]+)')

# Новый путь, на который заменяем (оставляем только имя файла)
replacement_base = "/img/CatD/catbimg/"

# Файл для сохранения всех найденных оригинальных ссылок
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

            # Находим все пути (только для записи в файл)
            matches = pattern.findall(html)

            if matches:
                links_file.write(f"Файл: {filename}\n")
                for link in matches:
                    links_file.write(link + "\n")
                links_file.write("\n")

            # Заменяем каждый найденный путь на новый
            cleaned_html = pattern.sub(lambda m: replacement_base + m.group(1), html)

            # Сохраняем обновлённый файл рядом
            output_path = os.path.join(folder_path, filename.replace(".html", "_updated.html"))
            try:
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(cleaned_html)
            except Exception as e:
                print(f"Не удалось записать {output_path}: {e}")
                continue

            print(f"{filename} -> {output_path} обработан")

print(f"Все найденные пути сохранены в {found_links_file}")
print("Готово!")
