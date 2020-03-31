import data.saq as saq

# One of my favourites
TEST_BOTTLE_ID = 10703834


def test_stock_retrieval_from_store_is_deterministic():
    all_stock = []
    for i in range(2):
        store_stock = saq.get_per_store_stock(TEST_BOTTLE_ID, max_stores=10)
        all_stock.append(store_stock)

    for i, store in enumerate(all_stock[0]):
        assert all_stock[1][i]['postcode'] == store['postcode']


