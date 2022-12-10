import csv
import os


class Vacancy:
    """Класс для представления вакансии

    Attributes:
        name (str): Название вакансии
        salary_from (int): Нижний порог зарплаты
        salary_to (int): Верхний порог зарплаты
        salary_currency (str): Валюта зарплаты
        salary_average (int): Средняя зарплата
        area_name (str): Город
        year (int): Год публикации
    """
    currency_to_rub = {
        "AZN": 35.68, "BYR": 23.91, "EUR": 59.90, "GEL": 21.74, "KGS": 0.76,
        "KZT": 0.13, "RUR": 1, "UAH": 1.64, "USD": 60.66, "UZS": 0.0055,
    }

    def __init__(self, vacancy):
        """Конструктор объекта вакансий

        :param dict vacancy: Словарь вакансии

        >>> Vacancy({'test_data': True}).salary_average
        909.9
        >>> type(Vacancy({'test_data': True})).__name__
        'Vacancy'
        >>> Vacancy({'test_data': True}).year
        2007

        """
        if 'test_data' in vacancy.keys():
            vacancy = {
                'name': 'Test',
                'description': 'Test',
                'key_skills': 'Test',
                'experience_id': 'noExperience',
                'premium': 'True',
                'employer_name': 'Test',
                'salary_from': 10,
                'salary_to': 20,
                'salary_gross': 'True',
                'salary_currency': 'USD',
                'area_name': 'Test',
                'published_at': '2007-12-03T17:34:36+0300',
            }

        self.name = vacancy['name']
        self.salary_from = int(float(vacancy['salary_from']))
        self.salary_to = int(float(vacancy['salary_to']))
        self.salary_currency = vacancy['salary_currency']
        self.salary_average = self.currency_to_rub[self.salary_currency] * (self.salary_from + self.salary_to) / 2
        self.area_name = vacancy['area_name']
        # Ранняя имплементация
        # self.year = int(datetime.strptime(vacancy['published_at'], '%Y-%m-%dT%H:%M:%S%z').year)
        # Новая
        self.year = int(vacancy['published_at'][:4])


class DataSet:
    """Дата-сет для работы с таблицей
    Attributes:
        file_name (str): Название файла
        data (dict): Вакансии по годам
        header (list): Поля
    """
    def __init__(self, file_name):
        """Конструктор класса DataSet

        :param str file_name: Название файла
        """
        self.file_name = file_name
        self.data = {}
        self.header = []

    def csv_reader(self):
        """Читает CSV файл"""
        with open(self.file_name, mode='r', encoding='utf-8-sig') as file:
            reader = csv.reader(file)
            self.header = next(reader)
            header_length = len(self.header)
            for row in reader:
                if '' not in row and len(row) == header_length:
                    v_year = str(Vacancy(dict(zip(self.header, row))).year)
                    if v_year not in self.data.keys():
                        self.data[v_year] = []
                    self.data[v_year].append(dict(zip(self.header, row)))

    def export_csv(self, directory):
        os.makedirs(directory, exist_ok=True)
        for year in self.data.keys():
            filename = directory + "/" + str(year) + ".csv"
            with open(filename, "w", encoding='utf-8-sig', newline="") as file:
                writer = csv.DictWriter(file, fieldnames=self.header)
                writer.writeheader()
                writer.writerows(self.data[year])


class InputConnect:
    """Начальная точка программы. Объединяет всю логику программы

    Attributes:
        file_name (str): Название файла
        vacancy_name (list): Название необходимой вакансии
    """
    def __init__(self):
        """
        Начало работы программы
        """
        self.file_name = input('Введите название файла: ')

        dataset = DataSet(self.file_name)
        dataset.csv_reader()
        dataset.export_csv("chunks")


if __name__ == '__main__': InputConnect()
