#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tempfile
import os
import shutil
import pytest
from git import Repo
from git.exc import InvalidGitRepositoryError

from habit.store import DataStore


@pytest.fixture
def empty_folder():
    path = tempfile.mkdtemp()

    def fin():
        if os.path.exists(path):
            shutil.rmtree(path)

    return path


def test_datastore_raises_error_if_directory_does_not_exists(empty_folder):
    os.rmdir(empty_folder)
    with pytest.raises(FileNotFoundError):
        _ = DataStore(empty_folder)


def test_datastore_raises_error_if_path_is_not_a_directory():
    _, path = tempfile.mkstemp()
    with pytest.raises(NotADirectoryError):
        _ = DataStore(path)
    os.remove(path)


def test_datastore_raises_error_if_not_a_git_repository(empty_folder):
    with pytest.raises(InvalidGitRepositoryError):
        _ = DataStore(empty_folder)


def test_datastore_can_be_initialized_and_creates_a_git_repository(
        empty_folder):
    _ = DataStore.init(empty_folder)
    assert os.path.exists(os.path.join(empty_folder, '.git'))


@pytest.fixture
def empty_datastore(empty_folder):
    return DataStore.init(empty_folder)
