from click.testing import CliRunner
from habit.cli import main
import os
import pytest

@pytest.fixture
def runner():
    return CliRunner()

def test_init_creates_a_git_repository(runner):
    with runner.isolated_filesystem():
        result = runner.invoke(main,['init'])
        assert result.exit_code == 0
        assert os.path.exists('.git')
