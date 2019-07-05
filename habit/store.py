import os
from git import Repo
from habit.goal import Goal


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
        if os.path.exists(os.path.join(path, '.git')):
            raise FileExistsError(
                'Directory {} is already a git repository.'.format(path))
        Repo.init(path)
        return DataStore(path)

    def update_goal(self, goal, commit_msg):
        filename = self.get_path_to_goal(goal.name)
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

    def get_path_to_goal(self, name):
        return os.path.join(self.path, '{}.yaml'.format(name))

    def load_goal(self, name):
        if not name in self.list_goal_names():
            raise KeyError(
                'There is no goal named {} in this store'.format(name))
        goal = Goal.fromYAML(self.get_path_to_goal(name))
        goal.store = self
        return goal
