import datetime


class DataFetcher:
    """
    A wrapper around data objects which controls refreshing. A hack to avoid using a database which I now regret!
    """
    def __init__(self, data_object, refresh_interval=datetime.timedelta(hours=1)):
        self._data = data_object
        self.last_refreshed = datetime.datetime.now()
        self.refresh_interval = refresh_interval

    @property
    def latest_data(self):
        # TODO can we make this asynchronous, experience will suck when this is
        # refreshed
        if datetime.datetime.now() - self.last_refreshed > self.refresh_interval:
            print('Refreshing data from S3')
            self._data.__init__()

        return self._data
