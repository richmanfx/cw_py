#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import argparse
# import random

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
    parser.add_argument('--version', action='version', version='cw_py 1.0.0')
    parser.add_argument('--file', '-f', default=default_cw_file, help='file with CW words')
    parser.add_argument('--num', '-n', type=int, default=50, help='quantity of CW words')
    parser.add_argument('--pause', '-p', type=int, default=1, help='pause between words (in the dash)')
    parser.add_argument('--speed', '-s', type=int, default=100, help='speed (characters per minute)')
    parser.add_argument('--tone', '-t', type=int, default=700, help='pitch (Hz)')
    return parser


def main():
    default_cw_file = 'cw.txt'                              # Файл по-умолчанию с CW словами

    # Очистить консоль
    clear_console()
    # Обработать аргументы командной строки
    parser = create_parser(default_cw_file)                 # Экземпляр парсера
    namespace = parser.parse_args()
    cw_name = namespace.file                                # имя CW файла из командной строки


if __name__ == '__main__':
    main()
