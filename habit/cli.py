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
from dateparser import parse as dparse


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
@click.option(
    '--initial-pause',
    'initial_pause',
    default=3,
    help='Number of flat days in the beginning')
def new(name, slope, pledge, initial_pause):
    store = DataStore(os.getcwd())
    goal = create_goal(
        name=name,
        daily_slope=slope,
        pledge=pledge,
        initial_pause_days=initial_pause)
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
    print('Point added successfully!')


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
        print('Point with uuid {} removed successfully!'.format(uuid))
    except KeyError as e:
        print(e)
        exit(1)


@main.command()
@click.argument('name')
@click.argument('uuid')
@click.option('-v', '--value', 'value', help='The new value', default=None)
@click.option(
    '-t',
    '--time',
    'time',
    help='The new time, either as absolute value or relative to now',
    default=None)
@click.option(
    '-c', '--comment', 'comment', help='The new comment', default=None)
def edit(name, uuid, value, time, comment):
    store = DataStore(os.getcwd())
    goal = load_goal(store, name)
    try:
        if time is not None:
            time = dparse(time)
        if value is not None:
            value = float(value)
        goal.edit_point(uuid, value=value, comment=comment, stamp=time)
        print('Point with uuid {} edited successfully!'.format(uuid))
    except KeyError as e:
        print(e)
        exit(1)


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
