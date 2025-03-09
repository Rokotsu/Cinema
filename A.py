import os

# Список папок, которые не включаем в сканирование (чтобы не перегружать вывод лишними файлами)
EXCLUDED_DIRS = {".venv", ".git", ".idea", ".pytest_cache", "node_modules", "dist", "build", "coverage"}

# Имя выходного файла
OUTPUT_FILENAME = "combined_code.txt"


def generate_tree(dir_path, prefix=""):
    """
    Рекурсивно генерирует строку с деревом файлов и папок.
    """
    tree_str = ""
    try:
        entries = sorted(os.listdir(dir_path))
    except Exception as e:
        return f"{prefix}[Ошибка доступа: {e}]\n"

    # Фильтруем записи: исключаем системные и нежелательные папки
    entries = [entry for entry in entries if entry not in EXCLUDED_DIRS]
    entries_count = len(entries)

    for index, entry in enumerate(entries):
        full_path = os.path.join(dir_path, entry)
        connector = "└── " if index == entries_count - 1 else "├── "
        tree_str += prefix + connector + entry + "\n"
        if os.path.isdir(full_path):
            extension = "    " if index == entries_count - 1 else "│   "
            tree_str += generate_tree(full_path, prefix + extension)
    return tree_str


def write_project_tree(out_file, base_dir):
    """
    Записывает в файл полное дерево проекта.
    """
    out_file.write("Полное дерево проекта:\n")
    tree = generate_tree(base_dir)
    out_file.write(tree)
    out_file.write("\n" + "=" * 80 + "\n\n")


def write_files_content(out_file, base_dir):
    """
    Рекурсивно обходит все файлы в проекте и записывает их содержимое с разделителями.
    """
    for root, dirs, files in os.walk(base_dir):
        # Исключаем нежелательные директории из обхода
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        for file in files:
            # Пропускаем сам файл-сканер, чтобы не попадать в цикл
            if file == OUTPUT_FILENAME:
                continue
            file_path = os.path.join(root, file)
            out_file.write(f"Файл: {file_path}\n")
            out_file.write("-" * 80 + "\n")
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                out_file.write(content)
            except Exception as e:
                out_file.write(f"Ошибка при чтении файла: {e}")
            out_file.write("\n" + "=" * 80 + "\n\n")


def main():
    base_dir = os.path.abspath(os.path.dirname(__file__))
    output_path = os.path.join(base_dir, OUTPUT_FILENAME)
    with open(output_path, "w", encoding="utf-8") as out_file:
        write_project_tree(out_file, base_dir)
        write_files_content(out_file, base_dir)
    print(f"Сканирование завершено. Результат сохранён в {output_path}")


if __name__ == "__main__":
    main()
