import csv
import multiprocessing
import os
from datetime import datetime
import pytz

import pandas as pd

import requests
from xml.etree import ElementTree


class Vacancy:
    """Класс для представления вакансии

    Attributes:
        name (str): Название вакансии
        salary_currency (str): Валюта зарплаты
        date (datetime): Дата публикации
    """
    currency_to_rub = {
        "AZN": 35.68, "BYR": 23.91, "EUR": 59.90, "GEL": 21.74, "KGS": 0.76,
        "KZT": 0.13, "RUR": 1, "UAH": 1.64, "USD": 60.66, "UZS": 0.0055,
    }

    def __init__(self, vacancy):
        """Конструктор объекта вакансий

        :param dict vacancy: Словарь вакансии
        """
        self.name = vacancy['name']
        self.salary_currency = vacancy['salary_currency']
        self.date = datetime.strptime(vacancy['published_at'], '%Y-%m-%dT%H:%M:%S%z')


class StatsContainer:
    """Класс для объединения объектов статистики

    Attributes:
        stats (list): Объекты статистики
    """

    def __init__(self):
        self.stats = []
        self.old_date = datetime(2022, 12, 22, tzinfo=pytz.UTC)
        self.new_date = datetime(1970, 1, 1, tzinfo=pytz.UTC)

    def write(self, stat_list):
        self.stats = stat_list

        for s in self.stats:
            if s.old_date < self.old_date: self.old_date = s.old_date
            if s.new_date > self.new_date: self.new_date = s.new_date

    def get_count(self):
        temp = {}
        for s in self.stats:
            d = s.get_count()
            for k, v in d.items():
                if k in temp.keys(): temp[k] += v
                else: temp[k] = v
        temp = dict(sorted(temp.items(), key=lambda item: item[1], reverse=True))
        return {k: v for k, v in temp.items() if v > 5000 and k != 'RUR'}

    def print_statistics(self, output='date_dinamics.csv'):
        currencies = self.get_count().keys()
        date_list = pd.date_range(self.old_date, self.new_date, freq='M')
        info = pd.DataFrame({
            'date': date_list.strftime('%Y-%m').tolist(),
        })
        for v in currencies:
            info[v] = 0
        for i, date in enumerate(date_list.strftime('%d/%m/%Y').tolist()):
            response = requests.get('http://www.cbr.ru/scripts/XML_daily.asp?date_req={}'.format(date))
            root = ElementTree.fromstring(response.content)
            for v in currencies:
                for item in range(len(root)):
                    if root[item][1].text == v:
                        info.at[i, v] = float(root[item][4].text.replace(",", ".")) / float(
                            root[item][2].text.replace(",", "."))
                        break
                    if root[item][1].text == 'BYN':
                        info.at[i, 'BYR'] = float(root[item][4].text.replace(",", ".")) / float(
                            root[item][2].text.replace(",", "."))
        info.to_csv(output)


class Statistic:
    """Класс для представления статистики

    Attributes:
        salary_currency (dict): Количество каждой вадюты
    """
    def __init__(self):
        """Конструктор класса статистики"""
        self.salary_currency = {}
        self.old_date = datetime(2022, 12, 22, tzinfo=pytz.UTC)
        self.new_date = datetime(1970, 1, 1, tzinfo=pytz.UTC)

    def write(self, vacancy):
        """Заполение статистики

        :param Vacancy vacancy: Вакансия
        """
        if vacancy.salary_currency in self.salary_currency:
            self.salary_currency[vacancy.salary_currency] += 1
        else:
            self.salary_currency[vacancy.salary_currency] = 1

        if vacancy.date < self.old_date: self.old_date = vacancy.date
        if vacancy.date > self.new_date: self.new_date = vacancy.date

    def get_count(self):
        return dict(sorted(self.salary_currency.items(), key=lambda item: item[1], reverse=True))


class DataSet:
    """Дата-сет для работы с таблицей
    Attributes:
        file_name (str): Название файла
    """
    def __init__(self, file_name):
        """Конструктор класса DataSet

        :param str file_name: Название файла
        """
        self.file_name = file_name

    def csv_reader(self):
        """Читает CSV файл"""
        with open(self.file_name, mode='r', encoding='utf-8-sig') as file:
            reader = csv.reader(file)
            header = next(reader)
            header_length = len(header)
            for row in reader:
                if row[3] != '' and len(row) == header_length:
                    yield dict(zip(header, row))

    def get_statistic(self):
        """Получить статистические данные

        :return Statistics: Статистика
        """
        statistics = Statistic()

        for vacancy in self.csv_reader():
            statistics.write(Vacancy(vacancy))

        return statistics


class InputConnect:
    """Начальная точка программы. Объединяет всю логику программы

    Attributes:
        file_name (str): Название файла
    """
    def __init__(self, fn=None):
        """
        Начало работы программы
        """
        self.file_name = fn
        if fn is None:
            self.file_name = input('Введите название файла: ')

        files = [self.file_name + "/" + f for f in os.listdir(self.file_name)]

        self.container = StatsContainer()
        pool = multiprocessing.Pool(multiprocessing.cpu_count())
        pool.map_async(self.generate_statistic, files, callback=self.on_end_pool)
        pool.close()
        pool.join()

    def generate_statistic(self, filename):
        """Таск для многопотока

        :param filename: Название файла
        :return: Статистика одного года
        """
        dataset = DataSet(filename)
        return dataset.get_statistic()

    def on_end_pool(self, response):
        """Коллбэк по окончанию работы

        :param response: ответ
        :return:
        """
        self.container.write(response)
        print(self.container.get_count())
        self.container.print_statistics()


if __name__ == '__main__': InputConnect("chunks2")
