#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tempfile
import os
import shutil
import pytest
from git import Repo
from git.exc import InvalidGitRepositoryError
from tests.test_goal import dummy_goal

from habit.store import DataStore
from habit.goal import Point
import datetime as dt


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


def test_init_in_git_repo_fails(empty_datastore):
    with pytest.raises(FileExistsError):
        DataStore.init(empty_datastore.path)


@pytest.fixture
def one_goal_datastore(empty_datastore, dummy_goal):
    dummy_goal.set_store(empty_datastore)
    return empty_datastore

def test_one_goal_datastore_has_one_goal(one_goal_datastore):
    assert len(one_goal_datastore.list_goal_names()) == 1

def test_add_goal_raises_Error_if_goal_with_same_name_exists(
        one_goal_datastore, dummy_goal):
    with pytest.raises(ValueError):
        dummy_goal.set_store(one_goal_datastore)


def test_add_goal_results_in_creation_of_yaml_file(one_goal_datastore):
    assert os.path.exists(os.path.join(one_goal_datastore.path, 'Dummy.yaml'))


def test_add_goal_results_in_clean_git_repo(one_goal_datastore):
    assert not one_goal_datastore.repo.is_dirty(untracked_files=True)


def test_add_goal_results_having_one_goal(one_goal_datastore):
    assert len(one_goal_datastore.list_goal_names()) == 1


def test_random_other_files_are_not_counted_as_goals(one_goal_datastore):
    with open(os.path.join(one_goal_datastore.path, 'foobar.txt'), 'w'):
        pass
    assert len(one_goal_datastore.list_goal_names()) == 1


def test_correctly_named_directories_are_not_counted_as_goals(
        one_goal_datastore):
    os.mkdir(os.path.join(one_goal_datastore.path, 'foobar.yaml'))
    assert len(one_goal_datastore.list_goal_names()) == 1


def test_store_can_load_goal(one_goal_datastore):
    goal = one_goal_datastore.load_goal('Dummy')
    assert goal.name == 'Dummy'


def test_store_raises_error_when_loading_a_nonexistent_goal(
        one_goal_datastore):
    with pytest.raises(KeyError):
        one_goal_datastore.load_goal('Dummy2')


def test_store_makes_commit_when_goal_adds_a_datapoint(one_goal_datastore):
    old_head_commit = one_goal_datastore.repo.head.commit
    point = Point(value=1, stamp=dt.datetime.now(), comment='')
    goal = one_goal_datastore.load_goal('Dummy')
    goal.add_point(point)
    assert not one_goal_datastore.repo.is_dirty(untracked_files=True)
    new_head_commit = one_goal_datastore.repo.head.commit
    assert old_head_commit != new_head_commit
    assert new_head_commit.parents[0] == old_head_commit
