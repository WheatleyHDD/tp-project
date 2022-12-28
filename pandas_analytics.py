import pandas as pd
import os
import multiprocessing


class Vacancy:
    """Класс для представления вакансии

    Attributes:
        name (str): Название вакансии
        salary (int): Зарплата в рублях
        area_name (str): Город
        year (int): Год публикации
    """

    def __init__(self, vacancy):
        """Конструктор объекта вакансий

        :param dict vacancy: Словарь вакансии
        """
        self.name = vacancy['name']
        self.salary = vacancy['salary']
        self.area_name = vacancy['area_name']
        self.year = int(vacancy['published_at'][:4])


class StatsContainer:
    """Класс для объединения объектов статистики

    Attributes:
        stats (list): Объекты статистики
    """

    def __init__(self):
        self.stats = []
        self.vacancies_number = {}
        self.salary_dict = {}

    def write(self, stat_list):
        """Записать статистику за год в единую
        :param stat_list: статистика
        """
        self.stats = stat_list

    def get_stat1(self):
        """ Получить динамику уровня зарплат по годам

        :return dict: Динамика уровня зарплат по годам
        """
        for o in self.stats:
            self.salary_dict.update(o.salary)
        result = {}
        for year, sal in self.salary_dict.items():
            result[year] = int(sum(sal) / len(sal))
        return result

    def get_stat2(self):
        """Получить динамику количества вакансий по годам

        :return dict: Динамика количества вакансий по годам
        """
        for o in self.stats: self.vacancies_number.update(o.vacancies_number)
        return self.vacancies_number

    def get_stat3(self):
        """Получить динамику уровня зарплат по годам для выбранной профессии

        :return dict: Динамика уровня зарплат по годам для выбранной профессии
        """
        vac_sal = {}
        for o in self.stats: vac_sal.update(o.salary_of_vacancy_name)
        if not vac_sal: vac_sal = dict([(key, []) for key, value in self.salary_dict.items()])
        result = {}
        for year, sal in vac_sal.items():
            if len(sal) == 0:
                result[year] = 0
            else:
                result[year] = int(sum(sal) / len(sal))
        return result

    def get_stat4(self):
        """Получить динамику количества вакансий по годам для выбранной профессии

        :return dict: Динамика количества вакансий по годам для выбранной профессии
        """
        vac_count_sal = {}
        for o in self.stats: vac_count_sal.update(o.vac_count_of_vacancy_name)
        if not vac_count_sal: vac_count_sal = dict( [(key, 0) for key, value in self.vacancies_number.items()])
        return vac_count_sal

    def print_statistics(self):
        """Вывести статистику в консоль"""
        print('Динамика уровня зарплат по годам: ' + str(self.get_stat1()))
        print('Динамика количества вакансий по годам: ' + str(self.get_stat2()))
        print('Динамика уровня зарплат по годам для выбранной профессии: ' + str(self.get_stat3()))
        print('Динамика количества вакансий по годам для выбранной профессии: ' + str(self.get_stat4()))


class Statistic:
    """Класс для представления статистики

    Attributes:
        salary (dict): Зарплата по годам
        vacancies_number (dict): Количество вакансий по названиям
        salary_of_vacancy_name (dict): Зарплата по вакансиям
        vac_count_of_vacancy_name (dict): Количество вакансий по названию
        count_of_vacancies (int): Количество вакансий
    """

    def __init__(self):
        """Конструктор класса статистики"""
        self.salary = {}
        self.vacancies_number = {}
        self.salary_of_vacancy_name = {}
        self.vac_count_of_vacancy_name = {}
        self.count_of_vacancies = 0

    def year_sal_dynamics(self, vacancy):
        """Составление динамики зарплаты по годам

        :param Vacancy vacancy: Вакансия
        """
        if vacancy.year not in self.salary:
            self.salary[vacancy.year] = [vacancy.salary]
        else: self.salary[vacancy.year].append(vacancy.salary)

    def year_vac_dynamics(self, vacancy):
        """Составление динамики вакансий по годам

        :param Vacancy vacancy: Вакансия
        """
        if vacancy.year not in self.vacancies_number:
            self.vacancies_number[vacancy.year] = 1
        else: self.vacancies_number[vacancy.year] += 1

    def curr_vac_dynamics(self, vacancy, vacancy_name):
        """Составление динамики зарплаты по конкретной вакансии по городам

        :param Vacancy vacancy: Вакансия
        :param str vacancy_name: Название вакансии
        """
        if vacancy.name.find(vacancy_name) == -1: return

        if vacancy.year not in self.salary_of_vacancy_name:
            self.salary_of_vacancy_name[vacancy.year] = [vacancy.salary]
        else: self.salary_of_vacancy_name[vacancy.year].append(vacancy.salary)

        if vacancy.year not in self.vac_count_of_vacancy_name:
            self.vac_count_of_vacancy_name[vacancy.year] = 1
        else: self.vac_count_of_vacancy_name[vacancy.year] += 1

    def write(self, vacancy, vacancy_name):
        """Заполение статистики

        :param Vacancy vacancy: Вакансия
        :param str vacancy_name: Название определенной вакансии
        """
        self.year_sal_dynamics(vacancy)
        self.year_vac_dynamics(vacancy)
        self.curr_vac_dynamics(vacancy, vacancy_name)
        self.count_of_vacancies += 1


class DataSet:
    """Дата-сет для работы с таблицей
    Attributes:
        file_name (str): Название файла
        vacancy_name (str): Название необходимой вакансии
    """

    def __init__(self, file_name, vacancy_name):
        """Конструктор класса DataSet

        :param str file_name: Название файла
        :param str vacancy_name: Название необходимой вакансии
        """
        self.file_name = file_name
        self.vacancy_name = vacancy_name
        self.data = pd.read_csv(self.file_name)

    def get_statistic(self):
        """Получить статистические данные

        :return Statistics: Статистика
        """
        statistics = Statistic()
        for _, row in self.data.iterrows():
            statistics.write(Vacancy(dict(zip(row.keys(), row.values()))),self.vacancy_name)
        return statistics


class InputConnect:
    """Начальная точка программы. Объединяет всю логику программы

    Attributes:
        file_name (str): Название файла
        vacancy_name (list): Название необходимой вакансии
    """

    def __init__(self, fn=None, vn=None):
        """
        Начало работы программы
        """
        self.file_name = fn
        if fn is None:
            self.file_name = input('Введите название файла: ')
        self.vacancy_name = vn
        if vn is None:
            self.vacancy_name = input('Введите название профессии: ')

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
        dataset = DataSet(filename, self.vacancy_name)
        return dataset.get_statistic()

    def on_end_pool(self, response):
        """Коллбэк по окончанию работы

        :param response: ответ
        :return:
        """
        self.container.write(response)
        self.container.print_statistics()


if __name__ == '__main__': InputConnect()
