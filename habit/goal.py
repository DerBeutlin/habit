from collections import namedtuple
import datetime as dt
from dateutil.relativedelta import relativedelta
import yaml
from uuid import uuid4


def chop_microseconds(delta):
    return delta - dt.timedelta(microseconds=delta.microseconds)


Point = namedtuple('Point', ['stamp', 'value', 'comment', 'uuid'])


def create_point(value, stamp=None, comment=''):
    if stamp is None:
        stamp = dt.datetime.now().replace(microsecond=0)
    uuid = str(uuid4())
    return Point(stamp=stamp, value=value, comment=comment, uuid=uuid)


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
        self.store = None

    def _update(commit_msg):
        def wrapper(func):
            def wrapped_f(s, *args, **kwargs):
                func(s, *args, **kwargs)
                if s.store:
                    s.store.update_goal(
                        s, 'Goal {}: {}'.format(s.name, commit_msg))

            return wrapped_f

        return wrapper

    @_update("Added.")
    def set_store(self, store):
        if self.name in store.list_goal_names():
            raise ValueError(
                'A goal with name {} already exists in the store'.format(
                    self.name))
        self.store = store

    def value(self):
        return sum(p.value for p in self.datapoints)

    def __eq__(self, other):
        return self.__hash__() == hash(other)

    def __hash__(self):
        return hash((self.name, self.pledge, self.active,
                     self.reference_points, self.datapoints))

    @_update("Added datapoint")
    def add_point(self, point):
        self.datapoints = add_point_to_sorted_tuple(self.datapoints, point)

    @_update("Removed datapoint")
    def remove_point(self, uuid):

        point = self.find_datapoint(uuid)
        self.datapoints = tuple(d for d in self.datapoints if d != point)

    @_update("Edited datapoint")
    def edit_point(self, uuid, value=None, stamp=None, comment=None):
        point = self.find_datapoint(uuid)
        self.datapoints = tuple(d for d in self.datapoints if d != point)
        if value is not None:
            point = point._replace(value=value)
        if stamp is not None:
            point = point._replace(stamp=stamp)
        if comment is not None:
            point = point._replace(comment=comment)
        self.datapoints = add_point_to_sorted_tuple(self.datapoints, point)

    def find_datapoint(self, uuid):
        candidates = [d for d in self.datapoints if d.uuid.startswith(uuid)]
        if not candidates:
            raise KeyError('No match for uuid {} found'.format(uuid))
        if len(candidates) > 1:
            raise KeyError('There are multiple matches for uuid {}, '.format(
                uuid) + ','.join((p.uuid for p in candidates)))
        return candidates[0]

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

            delta = (((self.value() - start_point.value) / dy) * dx) - (
                now - start_point.stamp)
            return chop_microseconds(delta)

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


def create_goal(name, daily_slope, pledge, initial_pause_days=3):
    now = dt.datetime.now()
    p1 = create_point(stamp=now, value=-initial_pause_days * daily_slope)
    end = now + relativedelta(years=10)
    p2 = create_point(
        stamp=end, value=((end - now).days - initial_pause_days) * daily_slope)
    return Goal(name=name, reference_points=(p1, p2), pledge=pledge)
