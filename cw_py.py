#!/usr/bin/python
# -*- coding: utf-8 -*-
from os import system
from sys import platform, stdout
import argparse
import random
import sounddevice as sd
from array import array
import math
import wave

VERSION = '1.0.0'
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
    parser.add_argument('-v', '--version', action='version', version='cw_py {}'.format(VERSION))
    parser.add_argument('file', nargs='?', type=argparse.FileType(),
                        default=default_cw_file, help='file with CW words')
    parser.add_argument('-n', '--num', type=int, default=10, help='quantity of CW words')
    parser.add_argument('-p', '--pause', type=int, default=1, help='pause between words (in the dash)')
    parser.add_argument('-s', '--speed', type=int, default=100, help='speed (characters per minute)')
    parser.add_argument('-t', '--tone', type=int, default=700, help='pitch (Hz)')
    parser.add_argument('-r', '--ramp', type=float, default=0.15, help='flatness of the front')
    parser.add_argument('-d', '--display', type=int, default=1, help='show immediately')
    return parser


# Проверка диапазона допустимых значений
def valid_range(minimum, maximum, variable):
    if (variable >= minimum) and (variable <= maximum):
        result = True
    else:
        result = False
    return result


# Выдача случайного объекта из списка
def get_random_word(all_words):
    random.seed()  # Инициализация
    return random.choice(all_words)


# Воспроизведение символа, буквы или цифры
# def symbol_sound(symbol, symbol_cw, dot, dash_conjoint, frequency, sample_rate, ramp):
def symbol_sound(**kwargs):
    # Извлекаем аргументы функции
    symbol = kwargs['symbol']
    symbol_cw = kwargs['symbol_cw']
    dash_conjoint = kwargs['dash_conjoint']
    dot = kwargs['dot']
    frequency = kwargs['frequency']
    sample_rate = kwargs['sample_rate']
    ramp = kwargs['ramp']

    k = dash_conjoint / dot  # коэффициент для слитных букв ( <AR>, <RN> и т.п.)
    duration = dot / 1000.0  # длительность точки (1000 - в секунды)
    amplitude = 32767.0  # максимальная амплидуда семпла/выборки
    data = array('h')  # 'h' - signed short integer, 2 bytes, массив для семпла буквы

    num_samples = int(sample_rate * duration)  # количество выборок посылки
    ramp_samples = int(ramp * num_samples)  # количество выборок на фронт/спад
    num_samples_per_cycle = int(sample_rate / frequency)  # количество выборок на период
    delta_amplitude = 1.0 / ramp_samples  # прирост амплитуды для следующей выборки фронта

    for counter, msg in enumerate(symbol_cw[symbol]):
        if msg == '.':
            # amplitude, data, delta_amplitude, num_samples, num_samples_per_cycle, ramp_samples
            cw_message(amplitude=amplitude, data=data, delta_amplitude=delta_amplitude,
                       num_samples=num_samples, num_samples_per_cycle=num_samples_per_cycle,
                       ramp_samples=ramp_samples)
        elif msg == '-':
            cw_message(amplitude=amplitude, data=data, delta_amplitude=delta_amplitude,
                       num_samples=3*num_samples, num_samples_per_cycle=num_samples_per_cycle,
                       ramp_samples=ramp_samples)
        if counter < len(symbol_cw[symbol]) - 1:        # тишина - амплитуда=0
            cw_message(amplitude=0, data=data, delta_amplitude=delta_amplitude,
                       num_samples=num_samples, num_samples_per_cycle=num_samples_per_cycle,
                       ramp_samples=ramp_samples)

    cw_message(amplitude=0, data=data, delta_amplitude=delta_amplitude, num_samples=k*num_samples,
               num_samples_per_cycle=num_samples_per_cycle, ramp_samples=ramp_samples)

    return data, num_samples


def cw_message(**kwargs):
    # Извлекаем аргументы функции
    amplitude = kwargs['amplitude']
    data = kwargs['data']
    delta_amplitude = kwargs['delta_amplitude']
    num_samples = kwargs['num_samples']
    num_samples_per_cycle = kwargs['num_samples_per_cycle']
    ramp_samples = kwargs['ramp_samples']

    # Фронт посылки
    for counter in range(ramp_samples):
        sample = amplitude
        sample *= (counter * delta_amplitude) * math.sin(
                                6.2831853 * (counter % num_samples_per_cycle) / num_samples_per_cycle)
        data.append(int(sample))

    # Центральная часть посылки
    for counter in range(ramp_samples, num_samples - ramp_samples):
        sample = amplitude
        sample *= math.sin(6.2831853 * (counter % num_samples_per_cycle) / num_samples_per_cycle)
        data.append(int(sample))

    # Спад посылки
    for counter in range(num_samples - ramp_samples, num_samples):
        sample = amplitude
        sample *= ((num_samples - counter) * delta_amplitude) * math.sin(
            6.2831853 * (counter % num_samples_per_cycle) / num_samples_per_cycle)
        data.append(int(sample))


# Записать массив данных в WAV-файл
def wav_file_save(data, num_samples, sample_rate, file_name):
    mono = 1
    sample_width = 2
    wav_file = wave.open(file_name, 'w')
    wav_file.setparams((mono, sample_width, sample_rate, num_samples, 'NONE', 'Uncompressed'))
    wav_file.writeframes(data.tostring())
    wav_file.close()


def main():
    default_cw_file = 'cw.txt'  # Файл по-умолчанию с CW словами
    data_file_name = 'symbol-cw.dat'  # Файл соответствия символов посылкам, A = .-
    temporary_wav_file = 'dot.wav'

    clear_console()  # Очистить консоль

    parser = create_parser(default_cw_file)  # Обработать аргументы командной строки
    namespace = parser.parse_args()

    if not argument_validator(namespace):  # Проверить аргументы командной строки
        exit()  # Выход из программы если плохие аргументы

    symbol_cw = method_name(data_file_name)  # Считать из файла соответствия символов посылкам

    all_words = get_cw_words(namespace)  # Прочитать слова CW из файла

    # Основной цикл воспроизведения и вывода слов
    word_counter = 0
    console_buffer = ""
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
                # symbol, symbol_cw, dot, dash_conjoint, frequency, sample_rate, ramp
                data, num_samples = symbol_sound(symbol=symbol, symbol_cw=symbol_cw,
                                                 dot=dot, dash_conjoint=dash_conjoint,
                                                 frequency=namespace.tone,
                                                 sample_rate=sample_rate,
                                                 ramp=namespace.ramp)
                for symbol_sample in data.tolist():  # Добавить букву в массив семплов
                    data_word.append(symbol_sample)

            # sd.sleep(dash_conjoint)  # Пауза после буквы

        # Записываем слово во временный WAV-файл и озвучиваем
        wav_file_save(data_word, num_samples, sample_rate, temporary_wav_file)
        play_from_wave_file(temporary_wav_file)

        if namespace.display == 1:      # Сразу отображаить слова
            # Вывод слов на экран
            print(random_word.ljust(8)),                # Через 8 символов, без перевода строки
            stdout.flush()                              # Обновить консоль для отображения print-ом с ','
            word_counter += 1  # Следующее слово
            # Разбить вывод на 10 столбцов
            if not word_counter % 10:
                print ''  # После кратного 10 столбца - перевод строки
        else:       # Не отображать слова сразу, а записывать в буфер
            console_buffer = console_buffer + random_word.ljust(8)
            word_counter += 1  # Следующее слово
            # Разбить вывод на 10 столбцов
            if not word_counter % 10:
                console_buffer = console_buffer + "\n"

        sd.sleep(namespace.pause * dash)  # Пауза между словами

    # Вывести из буфера все слова на экран
    if namespace.display == 0:
        print console_buffer,


# Считать слова CW из файла
def get_cw_words(namespace):
    cw_name = namespace.file  # файл с CW словами из командной строки
    all_words = cw_name.read().decode('utf-8').split()
    cw_name.close()  # Закрыть файл
    return all_words


# Считывание из файла соответствия символов посылкам
def method_name(data_file_name):
    data_file = open(data_file_name, 'r')
    strings = data_file.readlines()
    symbol_cw = {u'': ''}
    for string in strings:
        if string != '\n':  # пропустить пустые строки в файле
            symbol_cw.update({string.strip().split()[0].decode('utf-8'): string.strip().split()[1]})
    data_file.close()
    return symbol_cw


# Проверка допустимых значений аргументов командной строки
def argument_validator(namespace):
    validation_result = True
    if not valid_range(1, 1000, namespace.num):
        print 'Недопустимое значение для количества слов (1...1000).'
        validation_result = False
    elif not valid_range(1, 30, namespace.pause):
        print 'Недопустимое значение для паузы между словами (1...30).'
        validation_result = False
    elif not valid_range(50, 250, namespace.speed):
        print 'Недопустимое значение для скорости (50...250).'
        validation_result = False
    elif not valid_range(300, 2000, namespace.tone):
        print 'Недопустимое значение для тона (300...2000).'
        validation_result = False
    elif not valid_range(0.01, 0.50, namespace.ramp):
        print 'Недопустимое значение пологости фронта посылки (0,01...0,5).'
        validation_result = False
    elif not valid_range(0, 1, namespace.display):
        print 'Недопустимое значение параметра немедленного отображения (0 или 1).'
        validation_result = False
    return validation_result


def play_from_wave_file(file_name):
    import pyaudio
    chunk = 1024                                # define stream chunk
    wav_file = wave.open(file_name, 'rb')       # open a wav format music
    py_audio = pyaudio.PyAudio()                # instantiate PyAudio
    stream = py_audio.open(format=py_audio.get_format_from_width(wav_file.getsampwidth()),           # open stream
                           channels=wav_file.getnchannels(),
                           rate=wav_file.getframerate(),
                           output=True)
    data = wav_file.readframes(chunk)           # read data

    while data != '':                           # play stream
        stream.write(data)
        data = wav_file.readframes(chunk)

    stream.stop_stream()                        # stop stream
    stream.close()                              # close stream
    py_audio.terminate()                        # close PyAudio


if __name__ == '__main__':
    main()
