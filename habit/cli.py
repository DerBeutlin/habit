# -*- coding: utf-8 -*-
"""Console script for habit."""
import click
from habit.store import DataStore
from habit.goal import create_goal
import os


@click.group()
def main(args=None):
    pass


@main.command()
def init():
    DataStore.init(os.getcwd())


@main.command()
@click.argument('name')
@click.option('--slope', 'slope', default=1, help='Daily value increase')
@click.option('--pledge', 'pledge', default=0, help='Starting Pledge')
def new(name, slope, pledge):
    store = DataStore(os.getcwd())
    goal = create_goal(name=name, daily_slope=slope, pledge=pledge)
    store.add_goal(goal)
