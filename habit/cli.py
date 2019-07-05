# -*- coding: utf-8 -*-
"""Console script for habit."""
import click
from habit.store import DataStore
from habit.goal import create_goal, create_point
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
    print('Habit Store initialized successfully!')


@main.command()
@click.argument('name')
@click.option('--slope', 'slope', default=1, help='Daily value increase')
@click.option('--pledge', 'pledge', default=0, help='Starting Pledge')
def new(name, slope, pledge):
    store = DataStore(os.getcwd())
    goal = create_goal(name=name, daily_slope=slope, pledge=pledge)
    goal.set_store(store)
    print(
        'Goal named {} with daily slope of {} and a pledge of {}€ created successfully!'
        .format(name, slope, pledge))


@main.command()
def list():
    goals = load_goals()
    table = [[goal.name, goal.pledge,
              goal.time_remaining(dt.datetime.now())] for goal in goals]
    print(tabulate.tabulate(table))


def load_goals():
    store = DataStore(os.getcwd())
    names = store.list_goal_names()
    if not names:
        return []
    pool = multiprocessing.dummy.Pool(len(names))
    return pool.map(lambda name: store.load_goal(name), names)


@main.command()
@click.argument('name')
@click.argument('value')
@click.option('-c', 'comment', default='', help='Comment for the datapoint')
def add(name, value, comment=''):
    store = DataStore(os.getcwd())
    goal = store.load_goal(name)
    point = create_point(value=float(value), comment=comment)
    goal.add_point(point)


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
