import sys
import requests
import json
from bs4 import BeautifulSoup


offer = {'id': None,
         'Заголовок': None,
         'Описание': None,
         'Контакты': None,
         'Картинки': [],
         'Текст': None,
         'Дата': None,
         'Источник': None,
         'Источник id': None,
         'Просмотров': None}


def main():
    # url станицы для парсинга
    url_page = 'http://www.mirkvartir.ru/185464641/'

    # get запрос на страницу
    r = requests.get(url_page)
    r.encoding = 'utf-8'

    #  есди код ответа не 200, то завершаем работу программы
    if r.status_code != 200:
          print('Response status code is not 200')
          sys.exit()

    # создаем объект парсера
    soup = BeautifulSoup(r.text, 'html.parser')

    # id объявления
    offer['id'] = url_page.split('/')[-2]

    # получаем заголовок объявления
    offer_title = soup.find('h1', class_='offer-title').text
    offer['Заголовок'] = offer_title.replace('\t', '').replace('\r', '').replace('\n', '')

    # описание
    offer_description = soup.find('div', class_='b-content-right-col').find('div', class_='options-wrapper').find_all('li')
    offer_contacts = soup.find('div', class_='b-content-right-col').find('div', class_='b-contacts')

    offer['Описание'] = {x.text.split(':')[0].replace('\n', ''): x.text.split(':')[1].replace('\n', '')
                         for x in offer_description}

    offer['Контакты'] = {'Имя продавца': offer_contacts.find('p').text.strip().split('\n')[0].replace('\t', ''),
                         'Организация': offer_contacts.find('p').text.strip().split('\n')[1],
                         'Телефон': offer_contacts.find('span', class_='phone').find('a').attrs['value']}

    # картинки
    offer_images = soup.find('div', class_='actual b-post-load-img-cntnr').find_all('img')
    offer['Картинки'] = [x.attrs['src'] for x in offer_images]

    # текст
    offer['Текст'] = soup.find('div', class_='b-content-left-col').find('p').text

    # дата
    offer_date_and_sell = soup.find('div', id='b-date-and-sell-faster').find('div', class_='date')

    offer['Дата'] = offer_date_and_sell.find('div').find('div').text
    offer['Источник'] = offer_date_and_sell.find('span').text.strip().split('\n')[0].split(':')[-1].strip()
    offer['Источник id'] = offer_date_and_sell.find('span').text.strip().split('\n')[-1].replace(')', '')
    offer['Просмотров'] = offer_date_and_sell.find('div', class_='b-date-and-sell-faster-views-count').text.split(':')[-1]

    # заменяем символ квадрата перед сохранением в файл
    offer['Описание']['Площадь'] = offer['Описание']['Площадь'].replace('м²', 'м^2')

    with open('offer.json', 'w') as f:
        json.dump(offer, f, ensure_ascii=False)

main()
