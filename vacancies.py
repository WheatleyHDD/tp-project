import csv
import re
from datetime import datetime
from prettytable import PrettyTable


class Salary:
    """Класс для представления зарплаты

    Attributes:
        salary_from (int): Нижний порог зарплаты
        salary_to (int): Верхний порог зарплаты
        salary_currency (str): Валюта
    """
    ru_name = {
        'AZN': 'Манаты',
        'BYR': 'Белорусские рубли',
        'EUR': 'Евро',
        'GEL': 'Грузинский лари',
        'KGS': 'Киргизский сом',
        'KZT': 'Тенге',
        'RUR': 'Рубли',
        'UAH': 'Гривны',
        'USD': 'Доллары',
        'UZS': 'Узбекский сум'
    }

    ru_convert = {
        "AZN": 35.68,
        "BYR": 23.91,
        "EUR": 59.90,
        "GEL": 21.74,
        "KGS": 0.76,
        "KZT": 0.13,
        "RUR": 1,
        "UAH": 1.64,
        "USD": 60.66,
        "UZS": 0.0055,
    }

    def __init__(self, vac):
        """Иницилизирует объект зарплаты

        :param dict vac: Словарь вакансии

        >>> type(Salary({'salary_from': 10, 'salary_to': 20, 'salary_gross': 'True', 'salary_currency': 'RUR'})).__name__
        'Salary'
        >>> Salary({'salary_from': 10, 'salary_to': 20, 'salary_gross': 'True', 'salary_currency': 'RUR'}).salary_from
        10
        >>> Salary({'salary_from': 10, 'salary_to': 20, 'salary_gross': 'True', 'salary_currency': 'RUR'}).salary_to
        20
        >>> Salary({'salary_from': 10, 'salary_to': 20, 'salary_gross': 'True', 'salary_currency': 'RUR'}).salary_currency
        'RUR'
        >>> Salary({'salary_from': 10, 'salary_to': 20, 'salary_gross': 'True', 'salary_currency': 'USD'}).salary_avg
        909.9
        """
        self.salary_from = int(float(vac['salary_from']))
        self.salary_to = int(float(vac['salary_to']))
        self.salary_gross = 'Без вычета налогов' if vac['salary_gross'].lower() == 'true' else 'С вычетом налогов'
        self.salary_currency = vac['salary_currency']

        self.salary_avg = Salary.ru_convert[self.salary_currency] * (self.salary_from + self.salary_to) / 2

    def __str__(self):
        """Получить текстовое представление объекта зарплаты

        :return: Текстовое представление объекта зарплаты

        >>> str(Salary({'salary_from': 10, 'salary_to': 20, 'salary_gross': 'True', 'salary_currency': 'USD'}))
        '10 - 20 (Доллары) (Без вычета налогов)'
        """
        return '{0:,} - {1:,} ({2}) ({3})'.format(self.salary_from,
                                                  self.salary_to,
                                                  self.ru_name[self.salary_currency],
                                                  self.salary_gross).replace(',', ' ')


class Vacancy:
    """Класс для представления вакансии

    Attributes:
        index (int): Идентификатор
        name (str): Название вакансии
        description (str): Описание вакансии
        skills (list): Навыки в списковом представлении
        skills_len (int): Количество навыков
        key_skills (str): Навыки в строковом представлении (вычищенные)
        experience_id (int): Количество опыта
        premium (bool): Премиум вакансия
        employer_name (str): Работодатель
        salary_obj (Salary): Объект зарплаты
        salary (str): Зарплата в текстовом представлении
        area_name (str): Город
        published_str (str): Дата публикации в строковом представлении
        published_at (datetime): Дата публикации
    """

    fields = ['index', 'name', 'description', 'key_skills', 'experience_id',
              'premium', 'employer_name', 'salary', 'area_name', 'published_at']
    exp_weight = {
        'Нет опыта': 1,
        'От 1 года до 3 лет': 2,
        'От 3 до 6 лет': 3,
        'Более 6 лет': 4
    }
    ru_exp = {
        'noExperience': 'Нет опыта',
        'between1And3': 'От 1 года до 3 лет',
        'between3And6': 'От 3 до 6 лет',
        'moreThan6': 'Более 6 лет',
    }

    def __init__(self, vacancy):
        """Конструктор объекта вакансий

        :param dict vacancy: Словарь вакансии

        >>> Vacancy({'test_data': True}).experience_id
        'Нет опыта'
        >>> Vacancy({'test_data': True}).premium
        'Да'
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
                'salary_currency': 'RUR',
                'area_name': 'Test',
                'published_at': datetime.now().strftime('%Y-%m-%dT%H:%M:%S')+'+0300',
            }

        self.index = 0

        self.name = Cleaners.html_remove(vacancy['name'])
        self.description = Cleaners.short_text(Cleaners.html_remove(vacancy['description']), 100)

        self.skills = vacancy['key_skills'].split('\n')
        self.skills_len = len(self.skills)
        self.key_skills = Cleaners.short_text(vacancy['key_skills'], 100)

        self.experience_id = self.ru_exp[vacancy['experience_id']]
        self.premium = 'Да' if vacancy['premium'].lower() == "true" else "Нет"
        self.employer_name = vacancy['employer_name']

        self.salary_obj = Salary(vacancy)
        self.salary = str(self.salary_obj)

        self.area_name = vacancy['area_name']

        self.published_str = vacancy['published_at']
        self.published_at = datetime.strptime(self.published_str, '%Y-%m-%dT%H:%M:%S%z').strftime("%d.%m.%Y")

    @property
    def salary_average(self):
        """ :return: Средняя зарплата """
        return self.salary_obj.salary_avg

    @property
    def salary_currency(self):
        """ :return: Валюта зарплаты """
        return self.salary_obj.salary_currency

    @property
    def salary_from(self):
        """ :return: Нижний порог зарплаты зарплаты """
        return self.salary_obj.salary_from

    @property
    def salary_to(self):
        """ :return: Верхний порог зарплаты зарплаты """
        return self.salary_obj.salary_to

    @property
    def experience_weight(self):
        """ :return: Количество опыта (идентификатор) """
        return self.exp_weight[self.experience_id]

    def get_list(self):
        """ :return: Представление вакансии в виде словаря """
        return [getattr(self, key) for key in self.fields]


class DataSet:
    """Дата-сет для работы с таблицей
    Attributes:
        file_name (str): Название файла
        filter_params (list): Параметр фильтра
        sort_params (list): Параметр сортировки
        sort_reverse (bool): Обратная сортировка?
        slice_num (list): Список со срезом от и до
        vacancies_objects (list): Список с вакансиями
    """
    translate_list = {
        'Описание': 'description',
        'Навыки': 'skills_len',
        'Оклад': 'salary_average',
        'Дата публикации вакансии': 'published_str',
        'Опыт работы': 'experience_weight',
        'Премиум-вакансия': 'premium',
        'Идентификатор валюты оклада': 'salary_currency',
        'Название': 'name',
        'Название региона': 'area_name',
        'Компания': 'employer_name',
    }

    filter_rules = {
        'Навыки': lambda v, val: all([skill in v.skills for skill in val.split(', ')]),
        'Оклад': lambda v, val: v.salary_from <= float(val) <= v.salary_to,
        'Дата публикации вакансии': lambda v, val: v.published_at == val,
        'Опыт работы': lambda v, val: v.experience_id == val,
        'Премиум-вакансия': lambda v, val: v.premium == val,
        'Идентификатор валюты оклада': lambda v, val: Salary.ru_name[v.salary_currency] == val,
        'Название': lambda v, val: v.name == val,
        'Название региона': lambda v, val: v.area_name == val,
        'Компания': lambda v, val: v.employer_name == val
    }

    def __init__(self, filename, filter_params, sort_params, sort_reverse, slice_num):
        """Конструктор класса DataSet

        :param str filename: Название файла
        :param list filter_params: Параметр фильтра
        :param list sort_params: Параметр сортировки
        :param bool sort_reverse: Обратная сортировка?
        :param list slice_num: Список со срезом от и до
        """
        self.file_name = filename
        self.filter_params = filter_params
        self.sort_params = sort_params
        self.sort_reverse = sort_reverse
        self.slice_num = slice_num
        self.vacancies_objects = []

    def csv_reader(self):
        """Читает CSV файл"""
        headers = []
        with open(self.file_name, mode='r', encoding='utf-8-sig') as file:
            reader = csv.reader(file)
            for index, row in enumerate(reader):
                if index == 0:
                    headers = row
                    csv_header_length = len(row)
                elif '' not in row and len(row) == csv_header_length:
                    self.vacancies_objects.append(Vacancy(dict(zip(headers, row))))

        if len(self.vacancies_objects) == 0:
            if len(headers) == 0: print('Пустой файл')
            else: print('Нет данных')
            exit()

    def get_rows(self):
        """Получить вакансии в списке"""
        return [v.get_list() for v in self.vacancies_objects]

    def filtering(self):
        """Фильтрация вакансий"""
        if len(self.filter_params) == 0: return
        self.vacancies_objects = list(
            filter(lambda v:
                   self.filter_rules[self.filter_params[0]](v, self.filter_params[1]),
                   self.vacancies_objects))

    def sorting(self):
        """Сортировка вакансий"""
        if self.sort_params != '':
            self.vacancies_objects.sort(key=lambda a: getattr(a, self.translate_list[self.sort_params]),
                                        reverse=self.sort_reverse)
        elif self.sort_params == '' and self.sort_reverse:
            self.vacancies_objects.reverse()

    def get_range(self):
        """Получить срез вакансий"""
        vacancies_temp = []
        slen = len(self.slice_num)
        for idx, v in enumerate(self.vacancies_objects):
            if (slen > 1 and self.slice_num[0] <= idx < self.slice_num[1]) or \
                    (slen == 1 and self.slice_num[0] <= idx) or slen == 0:
                v.index = idx + 1
                vacancies_temp.append(v)
        self.vacancies_objects = vacancies_temp


class Cleaners:
    """Класс со статическими функциями для очистки"""
    @staticmethod
    def html_remove(text):
        """ Убирает HTML тэги из строки

        :param str text: Исходный текст
        :return str: Почищенная текст

        >>> Cleaners.html_remove("<b>Test</b>",)
        'Test'
        """
        text = re.sub('<.*?>', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    @staticmethod
    def short_text(text, count):
        """ Укорачивет текст до count символов

        :param str text: Исходный текст
        :param int count: Количество оставшихся символов
        :return str: Укороченная строка

        >>> Cleaners.short_text("Testing", 4)
        'Test...'
        """
        return text if len(text) <= count else text[:count] + "..."


class InputConnect:
    """Начальная точка программы. Объединяет всю логику программы

    Attributes:
        err (list): Ошибки при работе программы
        filename (str): Название файла
        filter_params (list): Параметры фильтра
        sort_params (list): Параметры сортировки
        sort_reverse (bool): Обратный порядок сортировки
        slice_num (list): Диапазон вывода
        slice_fields (list): Диапазон столбцов
    """
    table_header = ['№', 'Название', 'Описание', 'Навыки', 'Опыт работы', 'Премиум-вакансия',
                    'Компания', 'Оклад', 'Название региона', 'Дата публикации вакансии']

    def __init__(self):
        """
        Начало работы программы
        """
        self.err = []
        self.filename = input('Введите название файла: ')
        self.filter_params = self.parse_filter(input('Введите параметр фильтрации: '))
        self.sort_params = self.parse_sort(input('Введите параметр сортировки: '))
        self.sort_reverse = self.parse_sort_reverse(input('Обратный порядок сортировки (Да / Нет): '))
        self.slice_num = self.parse_slice_num(input('Введите диапазон вывода: '))
        self.slice_fields = self.parse_slice_fields(input('Введите требуемые столбцы: '))

        if len(self.err) != 0:
            print(self.err[0])
            exit()

        data = DataSet(self.filename, self.filter_params, self.sort_params, self.sort_reverse, self.slice_num)
        data.csv_reader()
        data.filtering()
        data.sorting()
        data.get_range()

        rows = data.get_rows()

        if len(rows) == 0: print('Ничего не найдено')
        else:
            table = PrettyTable(align='l',
                                field_names=InputConnect.table_header,
                                max_width=20, hrules=1)
            table.add_rows(rows)
            print(table.get_string(fields=self.slice_fields))

    def parse_filter(self, filter_params):
        """Парсинг фильтров из строки

        :param str filter_params: Фильтры в строке
        :return list: Параметры фильтрации для дальнейшей работы
        """
        if filter_params == '': return []
        if ': ' not in filter_params:
            self.err.append('Формат ввода некорректен')
            return []
        filter_params = filter_params.split(': ')
        if filter_params[0] not in list(DataSet.filter_rules.keys()):
            self.err.append('Параметр поиска некорректен')
            return []
        return filter_params

    def parse_sort(self, sort_param):
        """Парсинг сортировки из строки

        :param str sort_param: Параметры сортировки в строке
        :return list: Параметры сортировки для дальнейшей работы
        """
        if sort_param not in InputConnect.table_header + ['']:
            self.err.append('Параметр сортировки некорректен')
        return sort_param

    def parse_sort_reverse(self, sort_reverse):
        """Парсинг порядка сортировки

        :param str sort_reverse: Параметр обратного порядка сортировки в строке
        :return bool: Обратный порядок?
        """
        if sort_reverse not in ('', 'Да', 'Нет'): self.err.append('Порядок сортировки задан некорректно')
        return True if sort_reverse == 'Да' else False

    def parse_slice_num(self, sort_range):
        """Парсинг среза вакансий

        :param str sort_range: Срез вакансий в строке
        :return list: Срез вакансий в листе
        """
        return [] if sort_range == '' else [int(l) - 1 for l in sort_range.split()]

    def parse_slice_fields(self, table_fields):
        """Парсинг среза столбцов

        :param str table_fields: Срез столбцов в строке
        :return list: Срез столбцов в листе
        """
        return self.table_header if table_fields == '' else ['№'] + [a for a in table_fields.split(', ')
                                                                     if a in self.table_header]


if __name__ == '__main__':
    InputConnect()
