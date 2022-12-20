import multiprocessing

import pandas
import requests
import pandas as pd
import datetime

API_URL = 'https://api.hh.ru/{}'
HEADER = {"User-Agent": "HHRu_Parser/1.0 (Dmitriy.Volkov@urfu.me)"}
SAVE_NAME = 'new_vacancies.csv'


def get_post(date_from, date_to, page=0):
    params = {
        'specialization': 1,
        'per_page': 100,
        'page': page,
        'date_from': date_from.strftime('%Y-%m-%dT%H:%M:%S%z'),
        'date_to': date_to.strftime('%Y-%m-%dT%H:%M:%S%z'),
    }
    resp = requests.get(API_URL.format('vacancies'), headers=HEADER, params=params)
    return resp.json()['items'] if 'items' in resp.json() else []


def get_task(freq):
    result = []
    for p in range(0, 20 + 1):
        out = get_post(freq[0], freq[1], p)
        if len(out) == 0: break
        result += out
    return result


def on_end_parse(response):
    df = pandas.DataFrame(columns=['name', 'salary_from', 'salary_to', 'salary_currency', 'area_name', 'published_at'])
    for resp in response:
        for r in resp:
            temp = [r['name'], None, None, None, r['area']['name'], r['published_at']]
            if r['salary'] is not None:
                temp[1] = r['salary']['from']
                temp[2] = r['salary']['to']
                temp[3] = r['salary']['currency']
            df.loc[len(df)] = temp
    df.to_csv(SAVE_NAME, index=False)


if __name__ == "__main__":
    date_to = datetime.datetime.strptime(input("Дата от (ГОД-МЕСЯЦ-ДЕНЬ): "), "%Y-%m-%d")
    SAVE_NAME = input("Название выходного файла: ")
    date_from = date_to - datetime.timedelta(days=1)
    time = pd.date_range(date_from, date_to, freq="H")

    times = []
    for i, t in enumerate(time):
        if i + 1 < len(time): times.append([t, time[i + 1]])

    pool = multiprocessing.Pool(multiprocessing.cpu_count())
    pool.map_async(get_task, times, callback=on_end_parse)
    pool.close()
    pool.join()
