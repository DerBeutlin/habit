import os
from git import Repo


class DataStore:
    def __init__(self, path):
        if not os.path.exists(path):
            raise FileNotFoundError('{} does not exist'.format(path))
        if not os.path.isdir(path):
            raise NotADirectoryError('{} is not a directoy'.format(path))
        self.repo = Repo(path)

    def init(path):
        Repo.init(path)
        return DataStore(path)
