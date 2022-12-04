import vacancies
import statistics


def start():
    prog = input("Что делаем (Вакансии/Статистика): ")
    if prog == "Вакансии": vacancies.InputConnect()
    elif prog == "Статистика": statistics.InputConnect()
    else: print("Неизвестная программа")


if __name__ == '__main__':
    start()