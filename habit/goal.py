from collections import namedtuple
import yaml

Point = namedtuple('Point', ['stamp', 'value', 'comment'])


class Goal():
    def __init__(self,
                 name,
                 pledge,
                 reference_points,
                 active=None,
                 datapoints=None):
        self.name = name
        self.pledge = pledge
        if active is None:
            self.active = True
        else:
            self.active = active
        self.reference_points = reference_points
        if datapoints is None:
            self.datapoints = ()
        else:
            self.datapoints = datapoints

    def __eq__(self,other):
        return self.__hash__() == hash(other)

    def __hash__(self):
        return hash((self.name, self.pledge, self.active,
                     self.reference_points, self.datapoints))

    def add_point(self, point):
        datapoints = (list(self.datapoints) + [point])
        datapoints.sort(key=lambda d: d.stamp)
        self.datapoints = tuple(datapoints)

    def toYAML(self, path):
        with open(path, 'w') as f:
            yaml.dump({
                'name':
                self.name,
                'pledge':
                self.pledge,
                'active':
                self.active,
                'reference_points':
                [dict(p._asdict()) for p in self.reference_points],
                'datapoints': [dict(p._asdict()) for p in self.datapoints],
            }, f)

    def fromYAML(path):
        with open(path) as f:
            data = yaml.safe_load(f)
        return Goal(
            name=data['name'],
            pledge=data['pledge'],
            active=data['active'],
            reference_points=tuple([Point(**p) for p in data['reference_points']]),
            datapoints=tuple([Point(**p) for p in data['datapoints']]))
