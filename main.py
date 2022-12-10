import vacancies
import statistics
import year_splitter


def start():
    prog = input("Что делаем (Вакансии/Статистика/Разбить по годам): ")
    if prog == "Вакансии": vacancies.InputConnect()
    elif prog == "Статистика": statistics.InputConnect()
    elif prog == "Разбить по годам": year_splitter.InputConnect()
    else: print("Неизвестная программа")


if __name__ == '__main__':
    start()