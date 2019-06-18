#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tempfile
import os
import shutil
import pytest

from habit.store import DataStore


def test_datastore_raises_error_if_directory_does_not_exists():
    path = tempfile.mkdtemp()
    os.rmdir(path)
    with pytest.raises(FileNotFoundError):
        _ = DataStore(path)

def test_datastore_raises_error_if_path_is_not_a_directory():
    _,path = tempfile.mkstemp()
    with pytest.raises(NotADirectoryError):
        _ = DataStore(path)
    os.remove(path)

@pytest.fixture
def datastore():
    path = tempfile.mkdtemp()
    def fin():
        shutil.rmtree(path)
    return DataStore(path)


def test_datastore_can_be_initialized_with_an_existing_directory(datastore):
    pass

def test_datastore_creates_git_repository_at_path(datastore):
    assert os.path.isdir(os.path.join(datastore.path,'.git'))
