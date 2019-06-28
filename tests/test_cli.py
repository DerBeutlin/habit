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
