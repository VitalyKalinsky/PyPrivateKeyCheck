import os


def rec_file(directory):
    files = []

    # Проверяем, является ли directory директорий
    if not os.path.isfile(directory):
        # Получаем список всех файлов и поддиректорий внутри текущей директории
        contents = [os.path.join(directory, f) for f in os.listdir(directory)]

        # Рекурсивный обход поддиректорий
        for item in contents:
            if os.path.isfile(item):
                files.append(item)
            else:
                files.extend(rec_file(item))

    else:
        # Если это файл, добавляем его в список
        files.append(directory)

    return files
print(rec_file('src/main/java'))
