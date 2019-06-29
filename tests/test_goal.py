import pytest
from habit.goal import Goal, Point, create_goal
import datetime as dt
from dateutil.relativedelta import relativedelta
import tempfile
import yaml
import os


@pytest.fixture
def dummy_goal():
    reference_points = (Point(stamp=dt.datetime.now()+relativedelta(minutes=-1), value=0, comment=''),
                        Point(
                            stamp=dt.datetime.now() + relativedelta(days=1),
                            value=1,
                            comment=''))
    goal = Goal(name='Dummy', pledge=0, reference_points=reference_points)
    return goal


def test_can_initialize_goal(dummy_goal):
    pass


def test_inialized_goal_is_active(dummy_goal):
    assert dummy_goal.active


def test_initialized_goal_has_zero_datapoints(dummy_goal):
    assert len(dummy_goal.datapoints) == 0


def test_one_can_add_a_datapoint(dummy_goal):
    point = Point(stamp=dt.datetime.now(), value=1, comment='')
    dummy_goal.add_point(point)
    assert len(dummy_goal.datapoints) == 1
    assert dummy_goal.datapoints[0] == point


def test_one_can_add_multiple_datapoints_and_they_are_ordered_in_time(
        dummy_goal):
    later_point = Point(stamp=dt.datetime.now(), value=2, comment='')
    dummy_goal.add_point(later_point)
    earlier_point = Point(
        stamp=dt.datetime.now() - relativedelta(days=1), value=3, comment='')
    dummy_goal.add_point(earlier_point)
    assert len(dummy_goal.datapoints) == 2
    assert dummy_goal.datapoints[0] == earlier_point
    assert dummy_goal.datapoints[1] == later_point


def test_one_can_add_reference_points_and_they_are_ordered_in_time(dummy_goal):
    earlier_point = Point(
        stamp=dt.datetime.now() - relativedelta(days=1), value=-1, comment='')
    dummy_goal.add_reference_point(earlier_point)
    assert len(dummy_goal.reference_points) == 3
    assert dummy_goal.reference_points[0] == earlier_point


@pytest.fixture
def one_goal(dummy_goal):
    point = Point(stamp=dt.datetime.now(), value=1, comment='')
    dummy_goal.add_point(point)
    return dummy_goal


@pytest.fixture
def tmpfile():
    path = tempfile.mkstemp()[1]

    def fin():
        if os.path.exists(path):
            os.remove(path)

    return path


def test_can_write_goal_to_yaml(one_goal, tmpfile):
    one_goal.toYAML(tmpfile)
    with open(tmpfile) as f:
        data = yaml.safe_load(f)
    assert data.get('name') == one_goal.name
    assert data.get('pledge') == one_goal.pledge
    assert data.get('active') == one_goal.active
    assert data.get('reference_points') == [
        dict(p._asdict()) for p in one_goal.reference_points
    ]
    assert data.get('datapoints') == [
        dict(p._asdict()) for p in one_goal.datapoints
    ]
    assert data.get('hash') is not None


@pytest.fixture
def one_goal_clone(one_goal):
    return Goal(one_goal.name, one_goal.pledge, one_goal.reference_points,
                one_goal.active, one_goal.datapoints)


def test_hash_of_goals_with_same_data_are_the_same(one_goal, one_goal_clone):
    assert hash(one_goal_clone) == hash(one_goal)


def test_hash_of_goals_with_different_name_are_not_the_same(
        one_goal, one_goal_clone):
    one_goal_clone.name = "bar"
    assert hash(one_goal_clone) != hash(one_goal)


def test_hash_of_goals_with_different_pledge_are_not_the_same(
        one_goal, one_goal_clone):
    one_goal_clone.pledge += 1
    assert hash(one_goal_clone) != hash(one_goal)


def test_hash_of_goals_with_different_active_are_not_the_same(
        one_goal, one_goal_clone):
    one_goal_clone.active = False
    assert hash(one_goal_clone) != hash(one_goal)


def test_hash_of_goals_with_different_reference_points_are_not_the_same(
        one_goal, one_goal_clone):
    one_goal_clone.reference_points = tuple(
        list(one_goal_clone.reference_points) +
        [Point(stamp=0, value=0, comment='')])
    assert hash(one_goal_clone) != hash(one_goal)


def test_can_parse_goal_from_yaml(one_goal, tmpfile):
    one_goal.toYAML(tmpfile)
    clone = Goal.fromYAML(tmpfile)
    assert one_goal == clone


def test_parse_from_yaml_raises_error_if_hash_is_not_correct(
        one_goal, tmpfile):
    one_goal.toYAML(tmpfile)
    with open(tmpfile) as f:
        data = yaml.safe_load(f)
    data['hash'] = hash("foobar")
    with open(tmpfile, 'w') as f:
        yaml.dump(data, f)
    with pytest.raises(ValueError):
        Goal.fromYAML(tmpfile)


def test_value_for_simple_cumulative_goal_is_correct(dummy_goal):
    assert dummy_goal.value() == 0
    point = Point(stamp=dt.datetime.now(), value=1, comment='')
    dummy_goal.add_point(point)
    assert dummy_goal.value() == 1
    point = Point(stamp=dt.datetime.now(), value=100, comment='')
    dummy_goal.add_point(point)
    assert dummy_goal.value() == 101


def test_remaining_time_is_correct_for_simple_line(one_goal):
    expected_time = one_goal.reference_points[1].stamp - dt.datetime.now()
    assert abs(one_goal.time_remaining(dt.datetime.now()) -
               expected_time) < dt.timedelta(seconds=1)


def test_remaining_time_is_correct_more_complex_line(one_goal):
    point = Point(
        stamp=dt.datetime.now() + relativedelta(days=2), value=10, comment='')
    one_goal.add_reference_point(point)
    point = Point(
        stamp=dt.datetime.now() - relativedelta(days=2), value=-10, comment='')
    one_goal.add_reference_point(point)
    expected_time = one_goal.reference_points[-2].stamp - dt.datetime.now()
    assert abs(one_goal.time_remaining(dt.datetime.now()) -
               expected_time) < dt.timedelta(seconds=1)


def test_create_goal_from_slope():
    goal = create_goal(name='Dummy', daily_slope=10, pledge=10)
    assert goal.name == 'Dummy'
    assert goal.pledge == 10
    assert goal.active
    assert len(goal.datapoints) == 0
    assert len(goal.reference_points) == 2
    p1, p2 = goal.reference_points
    assert (p1.stamp - dt.datetime.now()) < dt.timedelta(seconds=1)
    assert (p2.stamp - (dt.datetime.now() +
                        relativedelta(years=10))) < dt.timedelta(seconds=1)
    assert p1.value == 0
    assert p2.value == (p2.stamp - p1.stamp).days * 10
