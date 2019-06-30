from collections import namedtuple
import datetime as dt
from dateutil.relativedelta import relativedelta
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
            dy = end_point.value - start_point.value
            dx = end_point.stamp - start_point.stamp

            return (((self.value() - start_point.value) / dy) * dx) - (
                now - start_point.stamp)

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
        goal = Goal(
            name=data.get('name'),
            pledge=data.get('pledge'),
            active=data.get('active'),
            reference_points=tuple(
                [Point(**p) for p in data.get('reference_points')]),
            datapoints=tuple([Point(**p) for p in data.get('datapoints')]))
        return goal


def create_goal(name, daily_slope, pledge):
    now = dt.datetime.now()
    p1 = Point(stamp=now, value=0, comment='')
    end = now + relativedelta(years=10)
    p2 = Point(stamp=end, value=(end - now).days * daily_slope, comment='')
    return Goal(name=name, reference_points=(p1, p2), pledge=pledge)
