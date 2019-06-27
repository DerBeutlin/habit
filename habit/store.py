import os
from git import Repo


class DataStore:
    def __init__(self, path):
        if not os.path.exists(path):
            raise FileNotFoundError('{} does not exist'.format(path))
        if not os.path.isdir(path):
            raise NotADirectoryError('{} is not a directoy'.format(path))
        self.repo = Repo(path)
        self.path = path

    def init(path):
        Repo.init(path)
        return DataStore(path)

    def add_goal(self,goal):
        filename = os.path.join(self.path,'{}.yaml'.format(goal.name))
        goal.toYAML(filename)
        self.repo.index.add([filename])
        self.repo.index.commit("Added {} Goal.".format(goal.name))

    # def list_goal_names(self):
