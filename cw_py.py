#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import random
from time import sleep


version = '1.0.0'

__author__ = 'Aleksandr Jashhuk, Zoer, R5AM, www.r5am.ru'


# Очистка консоли в Windows и Linux
def clear_console():
    if sys.platform == 'win32':
        os.system('cls')
    else:
        os.system('clear')


# Создаёт экземпляр parser с нужными параметрами
def create_parser(default_cw_file):
    parser = argparse.ArgumentParser(description='Generation of random CW words.',
                                     epilog='For example: cw_py.py -n 50 -t 750 -s 100 -p 3')
    parser.add_argument('--version', '-v', action='version', version='%(prog)s {}'.format(version))
    parser.add_argument('file', nargs='?', type=argparse.FileType(),
                        default=default_cw_file, help='file with CW words')
    parser.add_argument('--num', '-n', type=int, default=50, help='quantity of CW words')
    parser.add_argument('--pause', '-p', type=int, default=1, help='pause between words (in the dash)')
    parser.add_argument('--speed', '-s', type=int, default=100, help='speed (characters per minute)')
    parser.add_argument('--tone', '-t', type=int, default=700, help='pitch (Hz)')
    return parser


# Проверка диапазона допустимых значений
def valid_range(minimum, maximum, variable):
    if (variable < minimum) or (variable > maximum):
        result = False
    else:
        result = True
    return result


# Выдача случайного объекта из списка
def get_random_word(all_words):
    random.seed()                      # Инициализация
    return random.choice(all_words)


# Воспроизведение символа, буквы или цифры
def symbol_sound(symbol, dash, dot):
    pass


def main():
    default_cw_file = 'cw.txt'                  # Файл по-умолчанию с CW словами

    # Очистить консоль
    clear_console()

    # Обработать аргументы командной строки
    parser = create_parser(default_cw_file)     # Экземпляр парсера
    namespace = parser.parse_args()

    # Проверить аргументы командной строки
    if not argument_validator(namespace):
        sys.exit()                      # Выход из программы если плохие аргументы

    # Прочитать слова из файла
    cw_name = namespace.file            # файл с CW словами из командной строки
    all_words = cw_name.read().split()
    cw_name.close()                     # Закрыть файл

    # Основной цикл воспроизведения и вывода слов
    word_counter = 0
    while word_counter < namespace.num:

        # Выбор случайного слова, перевод в верхний регистр
        random_word = get_random_word(all_words).upper()
        # print(random_word)

        # Воспроизведение слова
        dot = 5.800 / namespace.speed               # Длительность точки
        dash = 3 * dot                              # Длительность тире
        dash_conjoint = dash                        # Промежуток между слитными буквами типа <KN>

        for symbol in random_word:          # Перебрать буквы в слове
            # Воспроизведение буквы
                # Обработка слитных слов
            if symbol == '<':
                dash_conjoint = dot                 # "<" - слитное слово
            if symbol == '>':
                dash_conjoint = dash                # ">" - раздельное слово
                sleep(dash_conjoint)

            symbol_sound(symbol, dash, dot)         # Воспроизводим символ
            sleep(dash_conjoint)                    # Пауза после буквы

        # Вывод слов на экран
        print(random_word.ljust(8)),                # Через 8 символов, без перевода строки
        word_counter += 1                           # Следующее слово
        # Разбить вывод на 10 столбцов
        if not word_counter % 10:
            print('')                               # После кратного 10 столбца - перевод строки

        sleep(namespace.pause * dash)               # Пауза между словами


# Проверка допустимых значений аргументов командной строки
def argument_validator(namespace):
    validation_result = True
    if not valid_range(1, 1000, namespace.num):
        print('Недопустимое значение для количества слов (1...1000).')
        validation_result = False
    elif not valid_range(1, 15, namespace.pause):
        print('Недопустимое значение для паузы между словами (1...15).')
        validation_result = False
    elif not valid_range(50, 250, namespace.speed):
        print('Недопустимое значение для скорости (50...250).')
        validation_result = False
    elif not valid_range(300, 2000, namespace.tone):
        print('Недопустимое значение для тона (300...2000).')
        validation_result = False
    return validation_result


if __name__ == '__main__':
    main()
