from bs4 import BeautifulSoup
import requests
from functools import lru_cache
import re
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

HEADER = {'Host': 'www.saq.com',
          'Referer': 'https://www.saq.com/en/12073995',
          'Host': 'www.saq.com',
          'Accept': 'application/json',
          'X-Requested-With': 'XMLHttpRequest'}

MAX_STORES = 100


def retrieve_stock(product_id):
    query = f"https://www.saq.com/en/saq_inventory/product/internal/id/{product_id}/?_=1585498276470"
    response = requests.get(query, headers=HEADER)
    return response.json()


def _parse_stock_json_for_store(store_json):
    output_list = []
    for store in store_json['list']:
        output_list.append({'id': store['identifier'],
                            'name': store['name'],
                            'postcode': store['postcode'],
                            'qty': store['qty']})
    return output_list


def retrieve_per_store_stock(product_id, max_stores=MAX_STORES):
    # For per stock we need to use this other bloody ID
    alt_product_id = fetch_alternative_product_id(product_id)

    # It's paged, and we want to retrieve multiple sets of 10 stores
    output = []
    for loaded in range(0, max_stores, 10):
        query = f'https://www.saq.com/en/store/locator/ajaxlist/context/product/id/{alt_product_id}?loaded={loaded}&_=1585504408733'
        response = requests.get(query, headers=HEADER)
        output.extend(_parse_stock_json_for_store(response.json()))
    return output


@lru_cache(maxsize=2056)
def fetch_alternative_product_id(original_product_id):
    """This is a time consuming operation whereby we use the URL product ID to fetch the true product ID"""
    page = requests.get(f'https://www.saq.com/en/{original_product_id}')
    soup = BeautifulSoup(page.content)
    ret = soup.find('div', {'class': 'price-box'})
    product_id = int(ret.attrs['data-product-id'])
    return product_id


def get_stock_from_webpage(url):
    product_regex = '1{1}\d{7}'

    # Parse product ID out of webpage
    product_id = re.search(product_regex, url).group(0)

    product_stock = get_stock_from_id(product_id)

    return product_stock


def get_stock_from_id(product_id):
    # per_store = retrieve_per_store_stock(product_id)
    stock_json = retrieve_stock(product_id)

    if stock_json['source'] == 2:
        # Stored under alternative product id
        alternative_product_id = fetch_alternative_product_id(product_id)
        stock_json = retrieve_stock(alternative_product_id)

    return stock_json


def get_soup(url):
    return BeautifulSoup(requests.get(url).content)


def parse_product_list(product_list_url):

    wine_soup = get_soup(product_list_url)
    list_items = wine_soup.find('ol', {'class': 'product-items'})
    children = list_items.findChildren('li', {'class': 'item product product-item'})
    product_ids = []
    product_names = []
    for c in children:
        product_names.append(c.find('span', {'class': 'show-for-sr'}).text.strip().split('   ')[0])
        product_ids.append(c.find('div', {'product'}).attrs['data-product-id'])
    return product_names, product_ids


def get_all_online_wine_ids(base_url='https://www.saq.com/en/products/wine?availability=Online&p=1'):
    total_wines = 1183
    wines_per_page = 24
    pages = np.ceil(total_wines/wines_per_page)

    wine_names = []
    wine_ids = []

    for p in range(int(pages)):
        names, ids = parse_product_list(base_url + f'&p={p}')
        wine_names.extend(names), wine_ids.extend(ids)

    return wine_names, wine_ids


def get_stock_for_top_red_wines(limit=-1):
    output_list = []
    red_wine_names, red_wine_ids = parse_product_list('https://www.saq.com/en/products/wine/red-wine?product_list_limit=96')
    for wine in red_wine_ids[:limit]:
        out = {'id': wine}
        stock = get_stock_from_id(wine)
        out.update(stock)

        output_list.append(out)

    return red_wine_names[:limit], output_list


if __name__ == '__main__':

    names, ids = get_all_online_wine_ids()
    print(names)
    print(len(ids))
