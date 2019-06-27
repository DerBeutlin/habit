from collections import namedtuple
import yaml

Point = namedtuple('Point', ['stamp', 'value', 'comment'])


class Goal():
    def __init__(self,
                 name,
                 pledge,
                 reference_points,
                 active=True,
                 datapoints=()):
        self.name = name
        self.pledge = pledge
        self.active = active
        self.reference_points = reference_points
        self.datapoints = datapoints

    def value(self):
        return sum(p.value for p in self.datapoints)

    def __eq__(self, other):
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
                'hash':
                self.__hash__(),
            }, f)

    def fromYAML(path):
        with open(path) as f:
            data = yaml.safe_load(f)
        goal = Goal(
            name=data.get('name'),
            pledge=data.get('pledge'),
            active=data.get('active'),
            reference_points=tuple(
                [Point(**p) for p in data.get('reference_points')]),
            datapoints=tuple([Point(**p) for p in data.get('datapoints')]))
        if hash(goal) != data.get('hash'):
            raise ValueError('Hash in Yaml does not fit the data')
        return goal
