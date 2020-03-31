import datetime
import pickle

import data.saq as saq
import numpy as np
from multiprocessing import Process, Queue, Pool, cpu_count

from data import storage
import pandas as pd


def get_wine_pool(id):
    stock = saq.get_stock_from_id(id)
    return {'id': id, 'stock': stock['stock']}


def get_wine_pool_all_stores(id):
    stock_array = saq.get_per_store_stock(id, max_stores=400)
    # print(f"Finished for {id}")
    return {'id': id, 'stock': stock_array}


def get_wine(q, id):

    stock = saq.get_stock_from_id(id)
    q.put({'id': id, 'stock': stock['stock']})


def get_products(q, page):
    names, ids = saq.parse_product_list(page)
    q.put((names, ids))


def load_from_cache_or_get_wine_ids(cache_path='./wine_list.pkl'):

    try:
        with open(cache_path) as f:
            pkl = pickle.load(f)

        wine_names, wine_ids = zip(pkl)

    except FileNotFoundError:
        wine_names, wine_ids = saq.get_all_online_wine_ids()

        with open(cache_path, 'wb') as f:
            pickle.dump(zip(wine_names, wine_ids), f)

    return wine_names, wine_ids


if __name__ == '__main__':

    # TODO cache this
    print('Fetching all pages')
    wine_names, wine_ids, wine_imgs = saq.get_all_online_wine_ids()

    # Short list for debugging
    # wine_names, wine_ids, wine_imgs = saq.parse_product_list('https://www.saq.com/en/products/wine/red-wine')

    wine_name_dict = {id: name for id, name in zip(wine_ids, wine_names)}
    wine_img_dict = {id: img for id, img in zip(wine_ids, wine_imgs)}
    # Get the stock for Online

    print('Beginning multiprocessing online')

    p = Pool(cpu_count())
    result = p.map(get_wine_pool, wine_ids)
    p.close()
    p.join()

    print('Finished multiprocessing')

    df = pd.DataFrame(result)
    df['wine_name'] = df['id'].map(wine_name_dict)
    df['wine_img'] = df['id'].map(wine_img_dict)

    df.set_index('wine_name', inplace=True)
    now = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

    print('Uploading to S3')
    # For now we save to CSV locally, and upload to S3
    filepath = f'./{now}.csv'
    df.to_csv(filepath)
    storage.upload_data_to_s3(filepath, filepath.lstrip('./'))

    # Get the stock per store
    print('Beginning multiprocessing')

    p = Pool(cpu_count())
    result = p.map(get_wine_pool_all_stores, wine_ids)
    p.close()
    p.join()

    print('Finished multiprocessing')

    df = pd.DataFrame(result)
    df['wine_name'] = df['id'].map(wine_name_dict)
    df['wine_img'] = df['id'].map(wine_img_dict)

    df.set_index('wine_name', inplace=True)
    now = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

    print('Uploading to S3')
    # For now we save to CSV locally, and upload to S3
    filepath = f'./all_stores_{now}.csv'
    df.to_csv(filepath)
    storage.upload_data_to_s3(filepath, filepath.lstrip('./'))

