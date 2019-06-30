# -*- coding: utf-8 -*-
"""Console script for habit."""
import click
from habit.store import DataStore
from habit.goal import create_goal
import os
import tabulate
import multiprocessing.dummy
import sys
import datetime as dt


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


@main.command()
def list():
    goals = load_goals()
    table = [[goal.name, goal.pledge, goal.time_remaining(dt.datetime.now())] for goal in goals]
    print(tabulate.tabulate(table))


def load_goals():
    store = DataStore(os.getcwd())
    names = store.list_goal_names()
    pool = multiprocessing.dummy.Pool(len(names))
    return pool.map(lambda name: store.load_goal(name), names)



if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
