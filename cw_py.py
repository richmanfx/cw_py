#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import argparse
# import random

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


# Провка диапазона допустимых значений
def valid_range(minimum, maximum, variable):
    if (variable < minimum) or (variable > maximum):
        result = False
    else:
        result = True
    return result


def main():
    default_cw_file = 'cw.txt'  # Файл по-умолчанию с CW словами

    # Очистить консоль
    clear_console()
    # Обработать аргументы командной строки
    parser = create_parser(default_cw_file)  # Экземпляр парсера
    namespace = parser.parse_args()
    cw_name = namespace.file  # файл из командной строки с CW словами

    # Проверить аргументы командной строки
    if not argument_validator(namespace):
        sys.exit()                       # Выход из программы если плохие аргументы



    print(namespace)


def argument_validator(namespace):
    # Проверка допустимых значений аргументов командной строки
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
