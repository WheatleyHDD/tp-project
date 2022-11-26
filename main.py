import vacancies
import elearn_2_1_3

if __name__ == '__main__':
    prog = input("Что делаем (Вакансии/Статистика): ")
    if prog == "Вакансии": vacancies.InputConnect()
    elif prog == "Статистика": elearn_2_1_3.InputConnect()
    else: print("Неизвестная программа")
