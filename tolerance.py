import os
from dataclasses import dataclass

import psycopg2
import requests
from bs4 import BeautifulSoup
import dotenv

dotenv.load_dotenv()


@dataclass()
class Item:
    id: int
    price: int
    bedrooms: int
    meters: int
    is_ready: int
    type: int
    location: str


def is_page_exists(page):
    response = requests.get(f'https://tolerance-homes.ru/turcia/?PAGEN_1={page}').text
    soup = BeautifulSoup(response, features='html.parser')
    soup_cards = soup.find_all('div', {'class': 'object list box'})
    return len(soup_cards) != 0


def scrape():
    regions = ['antalya', 'istanbul', 'mersin', 'alanya', 'bodrum', 'belek', 'northern-cyprus', 'kemer', 'izmir',
               'fethiye', 'side', 'finike', 'kas', 'kalkan', 'didim', 'kusadasi', 'manavgat']
    for region in regions:

        cards = []
        host = 'https://tolerance-homes.com/turkey/' + region
        page = 1
        locations = set()
        while is_page_exists(page):
            url = f'{host}/?PAGEN_1={page}'
            print(url, len(cards))
            response = requests.get(url).text
            soup = BeautifulSoup(response, features='html.parser')
            soup_cards = soup.find_all('div', {'class': 'object list box'})
            if len(soup_cards) == 0:
                break
            for soup_card in soup_cards:
                object_types = soup_card.find_all('div', {'class': 'object_type'})
                for id, object_type in enumerate(object_types):
                    try:
                        rooms_count = object_type.find('span', {'class': 'object_type_room'}).text
                        try:
                            meters = int(object_type.find('span', {'class': 'object_type_txt'}).text.split()[0])
                        except:
                            meters = 0
                        price = object_type.find('span', {"class": 'object_type_price'}).text
                        marks_div = soup_card.find_all('div', {'class': 'object_mark'})
                        marks = []
                        is_ready = 0
                        for mark_div in marks_div:
                            if 'READY TO MOVE IN' == mark_div.text.strip():
                                is_ready = 1
                        name = soup_card.find('div', {'class': 'object_h h3'}).text.strip()
                        location = name.split(' in ')[1].split()[0].replace(',', '')
                        obj_type = 1 if 'apartment' in name else 0
                        price = price.replace('.', '')
                        cards.append(Item(
                            id=int(soup_card.find('div', {'class': 'object_id'}).text.split()[1]),
                            price=int(price.split()[0]),
                            bedrooms=int(rooms_count.split('+')[0].replace('Duplex ', '').replace('Loft duplex ', '')),
                            meters=int(meters),
                            is_ready=is_ready,
                            type=obj_type,
                            location=region
                        ))
                        locations.add(location)
                    except Exception as e:
                        pass

            page += 1
        insert_cards_to_db(cards)
        print(region, 'finished!')


def insert_cards_to_db(items: list[Item]):
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )
    cur = conn.cursor()
    for i in items:
        cur.execute("INSERT INTO items (id, price, bedrooms, meters, is_ready, type, location) VALUES "
                    "(%s, %s, %s, %s,%s, %s, %s)",
                    (i.id, i.price, i.bedrooms, i.meters, i.is_ready, i.type, i.location))
    conn.commit()
    conn.close()


scrape()
