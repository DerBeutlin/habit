from click.testing import CliRunner
from habit.cli import main
from habit.goal import Goal, create_goal
import os
import pytest


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
    result = run_in_store.invoke(main, ['list'])
    assert result.exit_code == 0

@pytest.yield_fixture
def run_in_one_goal_store(run_in_store):
    run_in_store.invoke(main, ['new', 'dummy'])
    yield run_in_store

def test_list_goals(run_in_one_goal_store):
    run_in_one_goal_store.invoke(main,
                        ['new', 'foobar', '--slope', '10', '--pledge', '20'])
    result = run_in_one_goal_store.invoke(main, ['list'])
    assert result.exit_code == 0
    assert "dummy" in result.output
    assert "foobar" in result.output
