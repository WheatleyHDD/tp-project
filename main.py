import vacancies
import statistics

if __name__ == '__main__':
    prog = input("Что делаем (Вакансии/Статистика): ")
    if prog == "Вакансии": vacancies.InputConnect()
    elif prog == "Статистика": statistics.InputConnect()
    else: print("Неизвестная программа")
