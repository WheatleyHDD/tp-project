import csv
import multiprocessing
import os
from datetime import datetime
import pandas as pd


class Vacancy:
    """Класс для представления вакансии

    Attributes:
        name (str): Название вакансии
        salary (float): Зарплата
        date (datetime): Дата публикации
        area_name (str): Город
    """

    def __init__(self, vacancy, sc):
        """Конструктор объекта вакансий

        :param dict vacancy: Словарь вакансии
        :param SalaryConverter sc: Конвентер валют
        """
        self.name = vacancy['name']
        self.salary = 0
        if vacancy['salary_from'] != '' and vacancy['salary_to'] != '':
            self.salary = (int(float(vacancy['salary_from'])) + int(float(vacancy['salary_to']))) / 2
        elif vacancy['salary_from'] != '':
            self.salary = int(float(vacancy['salary_from']))
        else: self.salary = int(float(vacancy['salary_to']))
        self.area_name = vacancy['area_name']
        self.date = datetime.strptime(vacancy['published_at'], '%Y-%m-%dT%H:%M:%S%z')

        self.salary *= float(sc.get_currency_val(self.date.strftime("%Y-%m"), vacancy['salary_currency']))

    def to_dict(self):
        return {
            "name": self.name,
            "salary": self.salary,
            "area_name": self.area_name,
            "date": self.date.strftime('%Y-%m-%dT%H:%M:%S%z'),
        }


class DataSet:
    """Дата-сет для работы с таблицей
    Attributes:
        file_name (str): Название файла
    """
    def __init__(self, file_name, sc):
        """Конструктор класса DataSet

        :param str file_name: Название файла
        :param SalaryConverter sc: Конвентер валюты
        """
        self.file_name = file_name
        self.sc = sc

    def csv_reader(self):
        """Читает CSV файл"""
        with open(self.file_name, mode='r', encoding='utf-8-sig') as file:
            reader = csv.reader(file)
            header = next(reader)
            header_length = len(header)
            for row in reader:
                if len(row) == header_length:
                    v = dict(zip(header, row))
                    if v['salary_from'] != '' or v['salary_to'] != '':
                        yield v

    def get_info(self):
        """Получить статистические данные

        :return Statistics: Статистика
        """
        result = pd.DataFrame(columns=['name', 'salary', 'area_name', 'date'])

        for vacancy in self.csv_reader():
            v = Vacancy(vacancy, self.sc)
            if v.salary != 0:
                result.loc[len(result)] = list(v.to_dict().values())

        return result


class SalaryConverter:
    def __init__(self, fn):
        self.file_name = fn
        self.info = {}
        self.currencies_list = []
        self.csv_reader()

    def csv_reader(self):
        """Читает CSV файл"""
        with open(self.file_name, mode='r', encoding='utf-8-sig') as file:
            reader = csv.reader(file)
            header = next(reader)
            header.pop(0)
            header.pop(0)
            self.currencies_list = header
            header_length = len(header)
            for row in reader:
                row.pop(0)
                date = row.pop(0)
                if len(row) == header_length:
                    self.info[date] = dict(zip(header, row))

    def get_currency_val(self, date, curr):
        if date in self.info:
            if curr in self.info[date]:
                return self.info[date][curr]
        return 0

    def get_currencies(self):
        return self.currencies_list


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

        self.sc = SalaryConverter('date_dinamics.csv')
        files = [self.file_name + "/" + f for f in os.listdir(self.file_name)]
        pool = multiprocessing.Pool(multiprocessing.cpu_count())
        pool.map_async(self.generate_statistic, files, callback=self.on_end_pool)
        pool.close()
        pool.join()

    def generate_statistic(self, filename):
        """Таск для многопотока

        :param filename: Название файла
        :return: Статистика одного года
        """
        dataset = DataSet(filename, self.sc)
        info = dataset.get_info()
        return info

    def on_end_pool(self, response):
        """Коллбэк по окончанию работы

        :param response: ответ
        :return:
        """
        print('Собираем')
        d = pd.concat(response)
        d.to_csv('updated_vacancies.csv',index=False)


if __name__ == '__main__': InputConnect("chunks2")
