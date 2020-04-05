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
        wine_names, wine_ids = saq.get_all_online_wines()

        with open(cache_path, 'wb') as f:
            pickle.dump(zip(wine_names, wine_ids), f)

    return wine_names, wine_ids


def _add_metadata(df, products):
    df['wine_name'] = df['id'].map({p.id: p.name for p in products})
    df['wine_img'] = df['id'].map({p.id: p.img for p in products})
    df['wine_type'] = df['id'].map({p.id: p.type for p in products})
    df['wine_origin'] = df['id'].map({p.id: p.origin for p in products})

    return df


def update_df_for_online_stock(products):

    # Get the stock for Online
    print('Beginning multiprocessing online')

    p = Pool(cpu_count())
    result = p.map(get_wine_pool, [p.id for p in products])
    p.close()
    p.join()

    print('Finished multiprocessing')

    df = pd.DataFrame(result)

    df = _add_metadata(df, products)

    df.set_index('wine_name', inplace=True)
    now = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

    print('Uploading to S3')
    # For now we save to CSV locally, and upload to S3
    filepath = f'./{now}.csv'
    df.to_csv(filepath)
    storage.upload_data_to_s3(filepath, filepath.lstrip('./'))


def update_df_for_instore_stock(products):
    # Get the stock per store
    print('Beginning multiprocessing')

    p = Pool(cpu_count())
    result = p.map(get_wine_pool_all_stores, [p.id for p in products])
    p.close()
    p.join()

    print('Finished multiprocessing')

    df = pd.DataFrame(result)

    df = _add_metadata(df, products)

    df.set_index('wine_name', inplace=True)
    now = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

    print('Uploading to S3')

    # For now we save to CSV locally, and upload to S3
    filepath = f'./all_stores_{now}.csv'
    df.to_csv(filepath)
    storage.upload_data_to_s3(filepath, filepath.lstrip('./'))


if __name__ == '__main__':
    # TODO cache this
    print('Fetching all pages')
    products = saq.get_all_online_wines()

    # Short list for debugging
    # products = saq.parse_product_list('https://www.saq.com/en/products/wine/red-wine')

    update_df_for_online_stock(products)
    # update_df_for_instore_stock()



