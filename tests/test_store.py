#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tempfile
import os
import pytest

from habit.store import DataStore

def test_datastore_can_be_initialized_with_an_existing_directory():
    path = tempfile.mkdtemp()
    _ = DataStore(path)

def test_datastore_raises_error_if_directory_does_not_exists():
    path = tempfile.mkdtemp()
    os.rmdir(path)
    with pytest.raises(FileNotFoundError):
        _ = DataStore(path)

def test_datastore_raises_error_if_path_is_not_a_directory():
    _,path = tempfile.mkstemp()
    with pytest.raises(NotADirectoryError):
        _ = DataStore(path)

def test_datastore_creates_git_repository_at_path():
    path = tempfile.mkdtemp()
    _ = DataStore(path)
    assert os.path.isdir(os.path.join(path,'.git'))
