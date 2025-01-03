import xml.etree.ElementTree as ET
from os import listdir
from os.path import isfile, join
def rec_file(directory):
    files = []
    # Проверяем, является ли directory директорий
    if not isfile(directory):
        # Получаем список всех файлов и поддиректорий внутри текущей директории
        contents = [join(directory, f) for f in listdir(directory)]
        # Рекурсивный обход поддиректорий
        for item in contents:
            if isfile(item):
                files.append(item.replace('\\', '/'))
            else:
                files.extend(rec_file(item))
    else:
        # Если это файл, добавляем его в список
        files.append(directory)

    return files

tree = ET.parse('config.xml')
root = tree.getroot()
files = []
for elem in root.findall('filesToCheck'):
    for file in elem.findall('fileToCheck'):
        folder_path = file.text.strip()
        files += rec_file(folder_path)
print(files)
