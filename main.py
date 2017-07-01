import requests
import json
from bs4 import BeautifulSoup


def main():

    search_urls = [('http://www.mirkvartir.ru/Волгоградская+область/Волгоград/', 'http://www.mirkvartir.ru/'),
                   ('http://arenda.mirkvartir.ru/Волгоградская+область/Волгоград/', 'http://arenda.mirkvartir.ru/'),
                   ('http://dom.mirkvartir.ru/Волгоградская+область/Волгоград/', 'http://dom.mirkvartir.ru/')]

    for url, main_url in search_urls:
        print('Start scaning:', url)

        req = requests.get(url)
        if req.status_code != 200:
            print('Url {} does not return 200 code'.format(url))
            continue

        for page in range(1, 300):
            print('Page {}'.format(page))

            req = requests.get(url, params={'p': page})
            if req.status_code != 200:
                break

            items_soup = BeautifulSoup(req.text, 'html.parser')
            items = items_soup.find_all('div', class_='b-offer-item')
            print('Offers:', len(items))

            for counter, item in enumerate(items):
                print('Item {}/{}'.format(counter+1, len(items)))
                id = item.get('data-alias-id')
                print('ID:', id)

                req = requests.get(main_url + id)
                req.encoding = 'utf-8'

                if req.status_code != 200:
                    continue

                item_soup = BeautifulSoup(req.text, 'html.parser')

                offer = {'id': None,
                         'Заголовок': None,
                         'Описание': None,
                         'Стоимость': None,
                         'Контакты': None,
                         'Картинки': [],
                         'На карте': None,
                         'Описание от продавца': None,
                         'Дата': None,
                         'Источник': None,
                         'Источник id': None,
                         'Просмотров': None}
                try:
                    # id объявления
                    offer['id'] = id

                    # заголовок объявления
                    offer_title = item_soup.find('h1', class_='offer-title').text
                    offer['Заголовок'] = offer_title.replace('\t', '').replace('\r', '').replace('\n', '')

                    # стоимость
                    offer_price = item_soup.find('p', class_='price').find('strong').text
                    offer['Стоимость'] = offer_price.replace('.', '')

                    # описание
                    offer_description = item_soup.find('div', class_='b-content-right-col').find('div', class_='options-wrapper').find_all('li')
                    offer_contacts = item_soup.find('div', class_='b-content-right-col').find('div', class_='b-contacts')

                    offer['Описание'] = {x.text.split(':')[0].replace('\n', ''): x.text.split(':')[1].replace('\n', '')
                                         for x in offer_description}

                    offer['Контакты'] = {
                        'Имя продавца': offer_contacts.find('p').text.strip().split('\n')[0].replace('\t', ''),
                        'Организация': offer_contacts.find('p').text.strip().split('\n')[1],
                        'Телефон': offer_contacts.find('span', class_='phone').find('a').attrs['value']}

                    # картинки
                    offer_images = item_soup.find('div', class_='actual b-post-load-img-cntnr').find_all('img')
                    offer['Картинки'] = [x.attrs['src'] for x in offer_images]

                    # текст
                    offer['Описание от продавца'] = item_soup.find('div', class_='b-content-left-col').find('p').text

                    # дата
                    offer_date_and_sell = item_soup.find('div', id='b-date-and-sell-faster').find('div', class_='date')

                    offer['Дата'] = offer_date_and_sell.find('div').find('div').text
                    offer['Источник'] = offer_date_and_sell.find('span').text.strip().split('\n')[0].split(':')[-1].strip()
                    offer['Источник id'] = offer_date_and_sell.find('span').text.strip().split('\n')[-1].replace(')', '')
                    offer['Просмотров'] = \
                    offer_date_and_sell.find('div', class_='b-date-and-sell-faster-views-count').text.split(':')[-1]

                    # заменяем символ квадрата перед сохранением в файл
                    offer['Описание']['Площадь'] = offer['Описание']['Площадь'].replace('м²', 'м^2')

                except:
                    print('Bad item data, skip.')
                    continue

                with open('offer.json', 'a') as f:
                    try:
                        json.dump(offer, f, ensure_ascii=False)
                        f.write('\n')
                    except:
                        print('Bad encoding, or unexpected symbol in text. Skip item.')

main()
