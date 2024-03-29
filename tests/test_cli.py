from click.testing import CliRunner
from habit.cli import main
from habit.goal import Goal, create_goal
import os
import pytest
import datetime as dt


@pytest.yield_fixture
def runner():
    runner = CliRunner()
    with runner.isolated_filesystem():
        yield runner


def test_init_creates_a_git_repository(runner):
    result = runner.invoke(main, ['init'])
    assert result.exit_code == 0
    assert os.path.exists('.git')
    assert "Habit Store initialized successfully!" in result.output


@pytest.yield_fixture
def run_in_store(runner):
    runner.invoke(main, ['init'])
    yield runner


def test_add_goal(run_in_store):
    result = run_in_store.invoke(main, ['new', 'dummy'])
    assert result.exit_code == 0
    assert os.path.exists('dummy.yaml')
    goal = Goal.fromYAML('dummy.yaml')
    assert goal.name == 'dummy'
    assert goal.pledge == 0
    same_goal = create_goal(name='dummy', daily_slope=1, pledge=0)
    assert goal.reference_points[1].value == same_goal.reference_points[
        1].value
    assert 'Goal named dummy with daily slope of 1 and a pledge of 0€ created successfully!' in result.output


def test_add_goal_with_parameter(run_in_store):
    result = run_in_store.invoke(
        main, ['new', 'dummy', '--slope', '10', '--pledge', '10'])
    assert result.exit_code == 0
    assert os.path.exists('dummy.yaml')
    goal = Goal.fromYAML('dummy.yaml')
    assert goal.name == 'dummy'
    assert goal.pledge == 10
    same_goal = create_goal(name='dummy', daily_slope=10, pledge=0)
    assert goal.reference_points[1].value == same_goal.reference_points[
        1].value


def test_list_goal_does_not_fail_for_empty_datastores(run_in_store):
    result = run_in_store.invoke(main, ['goals'])
    assert result.exit_code == 0


@pytest.yield_fixture
def run_in_one_goal_store(run_in_store):
    run_in_store.invoke(main, ['new', 'dummy'])
    yield run_in_store


def test_list_goals(run_in_one_goal_store):
    run_in_one_goal_store.invoke(
        main, ['new', 'foobar', '--slope', '10', '--pledge', '20'])
    result = run_in_one_goal_store.invoke(main, ['goals'])
    assert result.exit_code == 0
    assert "dummy" in result.output
    assert "foobar" in result.output


def test_can_add_datapoint(run_in_one_goal_store):
    run = run_in_one_goal_store
    result = run.invoke(main, ['add', 'dummy', '10'])
    assert result.exit_code == 0
    goal = Goal.fromYAML('dummy.yaml')
    assert len(goal.datapoints) == 1
    assert goal.datapoints[0].value == 10
    assert "added successfully" in result.output


def test_can_add_datapoint_with_comment(run_in_one_goal_store):
    run = run_in_one_goal_store
    result = run.invoke(main, ['add', 'dummy', '10', '-c', 'test'])
    assert result.exit_code == 0
    goal = Goal.fromYAML('dummy.yaml')
    assert len(goal.datapoints) == 1
    assert goal.datapoints[0].comment == 'test'
    assert "added successfully" in result.output


@pytest.yield_fixture
def run_in_one_goal_store_with_one_point(run_in_one_goal_store):
    run_in_one_goal_store.invoke(main, ['add', 'dummy', '10', '-c', 'test'])
    yield run_in_one_goal_store


def test_can_list_datapoints_with_uuid(run_in_one_goal_store_with_one_point):
    run = run_in_one_goal_store_with_one_point
    result = run.invoke(main, ['list', 'dummy'])
    assert result.exit_code == 0
    assert '10' in result.output
    assert 'test' in result.output
    assert dt.datetime.now().strftime('%Y-%m-%d') in result.output
    goal = Goal.fromYAML('dummy.yaml')
    point = goal.datapoints[0]
    assert point.uuid[:8] in result.output

def test_can_remove_datapoint_with_uuid(run_in_one_goal_store_with_one_point):
    run = run_in_one_goal_store_with_one_point
    goal = Goal.fromYAML('dummy.yaml')
    point = goal.datapoints[0]
    result = run.invoke(main, ['remove', 'dummy',point.uuid[:5]])
    assert result.exit_code == 0
    assert 'removed successfully!' in result.output
    goal = Goal.fromYAML('dummy.yaml')
    assert len(goal.datapoints) == 0

def test_can_edit_datapoint_value(run_in_one_goal_store_with_one_point):
    run = run_in_one_goal_store_with_one_point
    goal = Goal.fromYAML('dummy.yaml')
    point = goal.datapoints[0]
    result = run.invoke(main, ['edit', 'dummy', point.uuid[:5] ,'-v', '123'])
    assert result.exit_code == 0
    assert 'edited successfully!' in result.output
    goal = Goal.fromYAML('dummy.yaml')
    point = goal.datapoints[0]
    assert point.value == 123

def test_can_edit_datapoint_comment(run_in_one_goal_store_with_one_point):
    run = run_in_one_goal_store_with_one_point
    goal = Goal.fromYAML('dummy.yaml')
    point = goal.datapoints[0]
    result = run.invoke(main, ['edit', 'dummy', point.uuid[:5], '-c','bar'])
    assert result.exit_code == 0
    assert 'edited successfully!' in result.output
    goal = Goal.fromYAML('dummy.yaml')
    point = goal.datapoints[0]
    assert point.comment == 'bar'

def test_can_edit_datapoint_time(run_in_one_goal_store_with_one_point):
    run = run_in_one_goal_store_with_one_point
    goal = Goal.fromYAML('dummy.yaml')
    point = goal.datapoints[0]
    result = run.invoke(main, ['edit', 'dummy', point.uuid[:5] , '-t', '1 min ago'])
    assert result.exit_code == 0
    assert 'edited successfully!' in result.output
    goal = Goal.fromYAML('dummy.yaml')
    point = goal.datapoints[0]
    assert abs(point.stamp-dt.datetime.now()+dt.timedelta(minutes=1)) < dt.timedelta(seconds=5)
