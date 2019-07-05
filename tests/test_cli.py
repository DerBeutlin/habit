from click.testing import CliRunner
from habit.cli import main
from habit.goal import Goal, create_goal
import os
import pytest


@pytest.fixture
def runner():
    return CliRunner()


def test_init_creates_a_git_repository(runner):
    with runner.isolated_filesystem():
        result = runner.invoke(main, ['init'])
        assert result.exit_code == 0
        assert os.path.exists('.git')
        assert "Habit Store initialized successfully!" in result.output


def test_add_goal(runner):
    with runner.isolated_filesystem():
        result = runner.invoke(main, ['init'])
        result = runner.invoke(main, ['new', 'dummy'])
        assert result.exit_code == 0
        assert os.path.exists('dummy.yaml')
        goal = Goal.fromYAML('dummy.yaml')
        assert goal.name == 'dummy'
        assert goal.pledge == 0
        same_goal = create_goal(name='dummy', daily_slope=1, pledge=0)
        assert goal.reference_points[1].value == same_goal.reference_points[
            1].value
        assert 'Goal named dummy with daily slope of 1 and a pledge of 0€ created successfully!' in result.output


def test_add_goal_with_parameter(runner):
    with runner.isolated_filesystem():
        result = runner.invoke(main, ['init'])
        result = runner.invoke(
            main, ['new', 'dummy', '--slope', '10', '--pledge', '10'])
        assert result.exit_code == 0
        assert os.path.exists('dummy.yaml')
        goal = Goal.fromYAML('dummy.yaml')
        assert goal.name == 'dummy'
        assert goal.pledge == 10
        same_goal = create_goal(name='dummy', daily_slope=10, pledge=0)
        assert goal.reference_points[1].value == same_goal.reference_points[
            1].value


def test_list_goal_does_not_fail_for_empty_datastores(runner):
    with runner.isolated_filesystem():
        runner.invoke(main, ['init'])
        result = runner.invoke(main, ['list'])
        assert result.exit_code == 0


def test_list_goals(runner):
    with runner.isolated_filesystem():
        runner.invoke(main, ['init'])
        runner.invoke(main,
                      ['new', 'dummy', '--slope', '10', '--pledge', '10'])
        runner.invoke(main,
                      ['new', 'foobar', '--slope', '10', '--pledge', '20'])
        result = runner.invoke(main, ['list'])
        assert result.exit_code == 0
        assert "dummy" in result.output
        assert "foobar" in result.output
