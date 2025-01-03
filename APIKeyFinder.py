import xml.etree.ElementTree as ET
from os import listdir
from os.path import isfile, join
import os
import math
import re
from pathlib import Path

found = []
probability = 5


class Found:
    def __init__(self, file_name: str, line: int, key_chance: float, password: str):
        self._file_name = file_name
        self._line = line
        self._key_chance = key_chance
        self._password = password

    @property
    def file_name(self) -> str:
        return self._file_name

    @file_name.setter
    def file_name(self, value: str):
        self._file_name = value

    @property
    def line(self) -> int:
        return self._line

    @line.setter
    def line(self, value: int):
        self._line = value

    @property
    def key_chance(self) -> float:
        return self._key_chance

    @property
    def password(self) -> str:
        return self._password

    def get_output_key_chance(self) -> int:
        return round(self._key_chance) if self._key_chance <= 10 else round(self._key_chance, -1)


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


def get_files_from_config():
    global probability
    tree = ET.parse('config.xml')
    root = tree.getroot()
    files = []
    for elem in root.findall('filesToCheck'):
        for file in elem.findall('fileToCheck'):
            folder_path = file.text.strip()
            if not isfile(folder_path):
                files += rec_file(folder_path)
            else:
                files.append(folder_path.replace('\\', '/'))
    probability = int(root.find('probability').text.strip())
    return files


def entropy(str_value: str) -> float:
    byte_values = str_value.encode()
    frequency_array = [0] * 256

    for byte_val in byte_values[:-1]:
        frequency_array[byte_val] += 1

    entropy = 0
    total_bytes = len(byte_values) - 1

    for freq in frequency_array:
        if freq != 0:
            prob_byte = freq / total_bytes
            entropy -= prob_byte * math.log2(prob_byte)

    return entropy


def check_file(file_path: Path):
    try:
        _, extension = os.path.splitext(file_path)
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = [line.lower().strip() for line in file]

        if extension == '.xml':
            for i, line in enumerate(lines):
                check_xml_pass(line, i, file_path)
        else:
            for i, line in enumerate(lines):
                check_pass(line, i, file_path)

    except FileNotFoundError as e:
        raise RuntimeError from e


def check_pass(line: str, i: int, file: Path):
    if '"' in line:
        sign = '"'
    elif "'" in line:
        sign = "'"
    else:
        return

    pass_to_add = ""
    chance = 0
    match_and_add(line, i, file, sign, pass_to_add, chance)


def match_and_add(line: str, i: int, file: Path, sign: str, pass_to_add: str, chance: float):
    pattern = rf"{sign}(.*?){sign}"
    matches = re.findall(pattern, line)

    for match in matches:
        password = match.strip()
        current_chance = get_chance(password)

        if current_chance > chance:
            chance = current_chance
            pass_to_add = password

    if chance >= 1:
        # Добавляем найденную информацию в список 'found'
        found.append(Found(str(file), i + 1, chance, pass_to_add))


def check_xml_pass(line: str, i: int, file: Path):
    count = line.count('<')

    if count >= 1:
        if '"' in line:
            sign = '"'
        elif "'" in line:
            sign = "'"
        else:
            sign = None

        pass_to_add = ""
        chance = 0

        if count == 2:
            password = line[line.find('>') + 1:line.rfind('<')].strip()
            current_chance = get_chance(password)

            if current_chance > chance:
                chance = current_chance
                pass_to_add = password

        if sign:
            match_and_add(line, i, file, sign, pass_to_add, chance)
    else:
        password = line.strip()
        chance = get_chance(password)

        if chance >= 1:
            # Добавить в список 'found'
            found.append(Found(str(file), i + 1, chance, password))


def get_chance(password: str) -> float:
    chance = 0
    if re.match(r"[\w:!@.#$%&*(\[\])=\-+]+", password) and len(password) >= 8:
        ent = entropy(password)
        chance += (math.log(ent) * 10 % 10 * 1.9 + 1) if ent >= 3 else 0
    return chance


# print(get_chance("cGFzc3dvcmQxMnUzNS03mVLWwsAawjYr"))
# print(get_chance("97D9gd086nUzNS03mVLawjYr"))
# print(get_chance("dml0YWx5a2FsaW5h"))
# print(get_chance("0imfnc8mVLWwsAawjYr4Rx-Af50DDqtl"))
# print(get_chance("cGFzc3d:vcmQxMnUzNS03mVLrg"))
# print(get_chance("vitaly"))
# print(get_chance("masha"))

for file in get_files_from_config():
    check_file(file)
found = filter(lambda x: x.get_output_key_chance() >= probability,
               sorted(found, key=lambda x: x.get_output_key_chance(), reverse=True))
for f in found:
    print(f"{f.password} at {f.file_name}:{f.line} with probability {f.get_output_key_chance()}")
