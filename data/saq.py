from bs4 import BeautifulSoup
import requests
from functools import lru_cache
import re
import numpy as np

HEADER = {'Host': 'www.saq.com',
          'Referer': 'https://www.saq.com/en/12073995',
          'Accept': 'application/json',
          'X-Requested-With': 'XMLHttpRequest'}

MAX_STORES = 100


def get_image_for_wine(product_id):
    url = f"https://www.saq.com/en/{product_id}"
    get_soup(url)


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


def get_per_store_stock(product_id, max_stores=MAX_STORES):
    # # For per stock we need to use this other bloody ID
    try:
        alt_product_id = fetch_alternative_product_id(product_id)
    except:
        # This is already an alt
        alt_product_id = product_id

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
    soup = BeautifulSoup(page.content, 'html.parser')
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


class ListItem:
    def __init__(self, c):
        self.c = c

    @property
    def name(self):
        return self.c.find('span', {'class': 'show-for-sr'}).text.strip().split('   ')[0]

    @property
    def id(self):
        return self.c.find('div', {'product'}).attrs['data-product-id']

    @property
    def url(self):
        return self.c.find('span', {'class': 'product-image-wrapper'}).find('img').attrs['src']

    @property
    def type(self):
        return self.c.find('strong', {'class': 'product-item-identity-format'}).findChildren('span')[0].contents[0].strip()


def parse_product_list(product_list_url):

    wine_soup = get_soup(product_list_url)
    list_items = wine_soup.find('ol', {'class': 'product-items'})
    children = list_items.findChildren('li', {'class': 'item product product-item'})
    product_ids, product_names, product_images, product_types = [], [], [], []
    for c in children:
        product = ListItem(c)
        product_names.append(product.name)
        product_ids.append(product.id)
        product_images.append(product.url)
        product_types.append(product.type)

    return product_names, product_ids, product_images, product_types


def _get_total_number_of_wines(url):
    soup = get_soup(url, 'html.parser')
    return int(soup.find_all('span', {'class': 'toolbar-number'})[-1].contents[0])


def get_all_online_wine_ids(base_url='https://www.saq.com/en/products/wine?availability=Online'):
    #TODO this should not be hardcoded
    total_wines = _get_total_number_of_wines(base_url)
    wines_per_page = 24
    pages = np.ceil(total_wines/wines_per_page)

    wine_names, wine_ids, wine_imgs, wine_types = [], [], [], []

    for p in range(int(pages)):
        names, ids, images, types = parse_product_list(base_url + f'&p={p}')
        wine_names.extend(names), wine_ids.extend(ids), wine_imgs.extend(images), wine_types.extend(types)

    return wine_names, wine_ids, wine_imgs, wine_types


def get_stock_for_top_red_wines(limit=-1):
    output_list = []
    red_wine_names, red_wine_ids, red_wine_imgs, _ = parse_product_list('https://www.saq.com/en/products/wine/red-wine?product_list_limit=96')
    for wine in red_wine_ids[:limit]:
        out = {'id': wine}
        stock = get_stock_from_id(wine)
        out.update(stock)

        output_list.append(out)

    return red_wine_names[:limit], output_list


if __name__ == '__main__':

    names, ids, images, types = get_all_online_wine_ids()
    print(names)
    print(images)
    print(len(ids))
    print(types)