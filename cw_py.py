#!/usr/bin/python
# -*- coding: utf-8 -*-

from os import system
from sys import platform, exit, stdout
import argparse
import random
import sounddevice as sd
from array import array
import math
import wave

version = '1.0.0'
__author__ = 'Aleksandr Jashhuk, Zoer, R5AM, www.r5am.ru'


# Очистка консоли в Windows и Linux
def clear_console():
    if platform == 'win32':
        system('cls')
    else:
        system('clear')


# Создаёт экземпляр parser с нужными параметрами
def create_parser(default_cw_file):
    parser = argparse.ArgumentParser(description='Generation of random CW words.',
                                     epilog='For example: cw_py.py -n 50 -t 750 -s 100 -p 3')
    parser.add_argument('--version', '-v', action='version', version='cw_py {}'.format(version))
    parser.add_argument('file', nargs='?', type=argparse.FileType(),
                        default=default_cw_file, help='file with CW words')
    parser.add_argument('--num', '-n', type=int, default=10, help='quantity of CW words')
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
    random.seed()  # Инициализация
    return random.choice(all_words)


# Воспроизведение символа, буквы или цифры
def symbol_sound(symbol, symbol_cw, dot, dash_conjoint, frequency, sample_rate):
    k = dash_conjoint / dot  # коеффициент для слитных букв ( <AR>, <RN> и т.п.)
    duration = dot / 1000.0  # длительность точки (1000 - в секунды)
    amplitude = 32767.0  # максимальная амплидуда семпла/выборки
    ramp = 0.15  # пологость фронта/ската посылки
    data = array('h')  # 'h' - signed short integer, 2 bytes, массив для семпла буквы

    num_samples = int(sample_rate * duration)  # количество выборок посылки
    ramp_samples = int(ramp * num_samples)  # количество выборок на фронт/спад
    num_samples_per_cycle = int(sample_rate / frequency)  # количество выборок на период
    delta_amplitude = 1.0 / ramp_samples  # прирост амплитуды для следующей выборки фронта

    for counter, msg in enumerate(symbol_cw[symbol]):
        if msg == '.':
            cw_message(amplitude, data, delta_amplitude, num_samples,
                       num_samples_per_cycle, ramp_samples)
        elif msg == '-':
            cw_message(amplitude, data, delta_amplitude, 3 * num_samples,
                       num_samples_per_cycle, ramp_samples)
        if counter < len(symbol_cw[symbol]) - 1:
            cw_message(0, data, delta_amplitude, num_samples,
                       num_samples_per_cycle, ramp_samples)

    cw_message(0, data, delta_amplitude, k * num_samples,
               num_samples_per_cycle, ramp_samples)

    return data, num_samples


def cw_message(amplitude, data, delta_amplitude, num_samples, num_samples_per_cycle, ramp_samples):
    # Фронт посылки
    for n in range(ramp_samples):
        sample = amplitude
        sample *= (n * delta_amplitude) * math.sin(6.2831853 * (n % num_samples_per_cycle) / num_samples_per_cycle)
        data.append(int(sample))

    # Центральная часть посылки
    for n in range(ramp_samples, num_samples - ramp_samples):
        sample = amplitude
        sample *= math.sin(6.2831853 * (n % num_samples_per_cycle) / num_samples_per_cycle)
        # print sample
        data.append(int(sample))

    # Спад посылки
    for n in range(num_samples - ramp_samples, num_samples):
        sample = amplitude
        sample *= ((num_samples - n) * delta_amplitude) * math.sin(
            6.2831853 * (n % num_samples_per_cycle) / num_samples_per_cycle)
        data.append(int(sample))


# Записать массив данных в WAV-файл
def wav_file_save(data, num_samples, sample_rate):
    mono = 1
    sample_width = 2
    f = wave.open('dot.wav', 'w')
    f.setparams((mono, sample_width, sample_rate, num_samples, 'NONE', 'Uncompressed'))
    f.writeframes(data.tostring())
    f.close()


def main():
    default_cw_file = 'cw.txt'  # Файл по-умолчанию с CW словами
    data_file_name = 'symbol-cw.dat'  # Файл соответствия символов посылкам, A = .-

    clear_console()  # Очистить консоль

    parser = create_parser(default_cw_file)  # Обработать аргументы командной строки
    namespace = parser.parse_args()

    if not argument_validator(namespace):  # Проверить аргументы командной строки
        exit()  # Выход из программы если плохие аргументы

    symbol_cw = method_name(data_file_name)  # Считать из файла соответствия символов посылкам

    all_words = get_cw_words(namespace)  # Прочитать слова CW из файла

    # Основной цикл воспроизведения и вывода слов
    word_counter = 0
    while word_counter < namespace.num:
        random_word = get_random_word(all_words).upper()  # Выбор случайного слова, верхний регистр

        # Воспроизведение слова
        sample_rate = 44100  # частота дискретизации, Гц
        dot = 5800 / namespace.speed  # Длительность точки
        dash = 3 * dot  # Длительность тире
        dash_conjoint = dash  # Промежуток между слитными буквами типа <KN>
        num_samples = 0  # Количество выборок
        # 'h' - signed short integer, 2 bytes, массив для семпла буквы
        data_word = array('h')

        for symbol in random_word:  # Перебрать буквы/символы в слове
            # Воспроизведение буквы
            # Обработка слитных слов
            if symbol == '<':
                dash_conjoint = dot  # "<" - слитное слово
            if symbol == '>':
                dash_conjoint = dash  # ">" - раздельное слово
                # sd.sleep(dash_conjoint)

            # Воспроизводим символ
            if symbol != '<' or symbol != '>':
                data, num_samples = symbol_sound(symbol, symbol_cw, dot, dash_conjoint, namespace.tone, sample_rate)
                for symbol_sample in data.tolist():  # Добавить букву в массив семплов
                    data_word.append(symbol_sample)

            # sd.sleep(dash_conjoint)  # Пауза после буквы

        wav_file_save(data_word, num_samples, sample_rate)  # Записать в файл данные
        dot_read_from_file('dot.wav')

        # Вывод слов на экран
        print(random_word.ljust(8)),                # Через 8 символов, без перевода строки
        stdout.flush()                              # Обновить консоль для отображения print-ом с ','
        word_counter += 1  # Следующее слово
        # Разбить вывод на 10 столбцов
        if not word_counter % 10:
            print('')  # После кратного 10 столбца - перевод строки

        sd.sleep(namespace.pause * dash)  # Пауза между словами


# Считать слова CW из файла
def get_cw_words(namespace):
    cw_name = namespace.file  # файл с CW словами из командной строки
    all_words = cw_name.read().split()
    cw_name.close()  # Закрыть файл
    return all_words


# Считывание из файла соответствия символов посылкам
def method_name(data_file_name):
    data_file = open(data_file_name, 'r')
    strings = data_file.readlines()
    symbol_cw = {}
    for string in strings:
        if string != '\n':  # пропустить пустые строки в файле
            symbol_cw.update({string.strip().split()[0]: string.strip().split()[1]})
    data_file.close()
    return symbol_cw


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


def dot_read_from_file(file_name):
    import pyaudio
    # define stream chunk
    chunk = 1024

    # open a wav format music
    f = wave.open(file_name, 'rb')
    # instantiate PyAudio
    p = pyaudio.PyAudio()
    # open stream
    stream = p.open(format=p.get_format_from_width(f.getsampwidth()),
                    channels=f.getnchannels(),
                    rate=f.getframerate(),
                    output=True)
    # read data
    data = f.readframes(chunk)

    # play stream
    while data != '':
        stream.write(data)
        data = f.readframes(chunk)

    # stop stream
    stream.stop_stream()
    stream.close()

    # close PyAudio
    p.terminate()


if __name__ == '__main__':
    main()
