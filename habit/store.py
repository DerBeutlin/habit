import os
from git import Repo


class DataStore:
    def __init__(self, path):
        if not os.path.exists(path):
            raise FileNotFoundError('{} does not exist'.format(path))
        if not os.path.isdir(path):
            raise NotADirectoryError('{} is not a directoy'.format(path))
        self.repo = Repo(path)

    @property
    def path(self):
        return self.repo.working_tree_dir

    def init(path):
        Repo.init(path)
        return DataStore(path)

    def add_goal(self, goal):
        self.update_goal(goal, "Added {} Goal.".format(goal.name))

    def update_goal(self, goal, commit_msg):
        filename = os.path.join(self.path, '{}.yaml'.format(goal.name))
        goal.toYAML(filename)
        self.repo.index.add([filename])
        self.repo.index.commit(commit_msg)

    def list_goal_names(self):
        goals = []
        for f in os.listdir(self.path):
            file_path = os.path.join(self.path, f)
            if not os.path.isfile(file_path):
                continue
            goal_name, extension = os.path.splitext(f)
            if not extension == '.yaml':
                continue
            goals.append(goal_name)
        return goals
