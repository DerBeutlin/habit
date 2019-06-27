# -*- coding: utf-8 -*-
"""Console script for habit."""
import click
from habit.store import DataStore
import os


@click.group()
def main(args=None):
    pass

@main.command()
def init():
    DataStore.init(os.getcwd())
