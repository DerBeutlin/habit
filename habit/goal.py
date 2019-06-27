from collections import namedtuple
import yaml

Point = namedtuple('Point', ['stamp', 'value', 'comment'])


def add_point_to_sorted_tuple(t, p):
    new_t = list(t) + [p]
    new_t.sort(key=lambda d: d.stamp)
    return tuple(new_t)



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
        self.datapoints = add_point_to_sorted_tuple(self.datapoints, point)

    def add_reference_point(self, point):
        self.reference_points = add_point_to_sorted_tuple(
            self.reference_points, point)

    def time_remaining(self, now):
        for start_point, end_point in zip(self.reference_points[:-1],
                                          self.reference_points[1:]):
            if end_point.stamp < now:
                continue
            slope = (end_point.value - start_point.value) / (
                end_point.stamp - start_point.stamp)
            return (self.value() - start_point.value) / slope

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
