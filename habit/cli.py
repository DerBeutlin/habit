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
    try:
        DataStore.init(os.getcwd())
        print('Habit Store initialized successfully!')
    except FileExistsError as e:
        print(e)
        exit(1)


@main.command()
@click.argument('name')
@click.option('--slope', 'slope', default=1, help='Daily value increase')
@click.option('--pledge', 'pledge', default=0, help='Starting Pledge')
def new(name, slope, pledge):
    store = DataStore(os.getcwd())
    goal = create_goal(name=name, daily_slope=slope, pledge=pledge)
    try:
        goal.set_store(store)
        print(
            'Goal named {} with daily slope of {} and a pledge of {}€ created successfully!'
            .format(name, slope, pledge))
    except ValueError as e:
        print(e)
        exit(1)


@main.command()
def goals():
    goals = load_goals()
    table = [[goal.name, goal.pledge,
              goal.time_remaining(dt.datetime.now())] for goal in goals]
    print(tabulate.tabulate(table))


def load_goal(store, name):
    try:
        return store.load_goal(name)
    except KeyError as e:
        print(e)
        exit(1)


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
    goal = load_goal(store, name)
    point = create_point(value=float(value), comment=comment)
    goal.add_point(point)


@main.command()
@click.argument('name')
def list(name):
    store = DataStore(os.getcwd())
    goal = load_goal(store, name)
    table = [[d.uuid[:8], d.value,
              d.stamp.isoformat(), d.comment] for d in goal.datapoints]
    print(
        tabulate.tabulate(table, headers=['Hash', 'Value', 'Time', 'Comment']))


@main.command()
@click.argument('name')
@click.argument('uuid')
def remove(name, uuid):
    store = DataStore(os.getcwd())
    goal = load_goal(store, name)
    try:
        goal.remove_point(uuid)
        print('Point with uuid {} removed successfully!'.format(hash))
    except KeyError as e:
        print(e)
        exit(1)


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
