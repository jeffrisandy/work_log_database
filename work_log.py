#!/usr/bin/env python3

from collections import OrderedDict
import datetime
import sys
import os

from peewee import *

db = SqliteDatabase('log.db')


class Entry(Model):
    name = CharField(max_length=255)
    task_title = CharField(max_length=255)
    time_spent = IntegerField(default=0)
    note = TextField()
    timestamp = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db


def initialize():
    """Create the database and table if they don't exist"""
    db.connect()
    db.create_tables([Entry], safe=True)


def menu_loop():
    """ Show the menu """
    choice = None

    while choice != 'q':
        clear()
        print("WORK LOG")
        print("What would you like to do?")
        print("Press 'q' to quit.")

        for k, v in menu.items():
            print(f"{k}) {v.__doc__}")
        choice = input('Action: ').lower().strip()

        if choice in menu:
            clear()
            menu[choice]()


def search_loop():
    """ Show the search menu """
    choice = None

    while choice != 'q':
        clear()
        print("SEARCH ENTRIES")
        print("What would you like to search?")
        print("Press 'q' to quit.")

        for k, v in search_menu.items():
            print(f"{k}) {v.__doc__}")
        choice = input('Action: ').lower().strip()

        if choice in menu:
            clear()
            search_menu[choice]()


def add_entry():
    """Add an entry."""

    name = input("Name: ")
    task_title = input("Task Title: ")
    time_spent = input("Time spent (rounded in minutes: ")
    print("Notes (optional, you can leave this empty. Press ctr+d when finished.")
    note = sys.stdin.read().strip()

    if name:
        if input("\n\nSave entry? [Yn] ").lower() != 'n':
            Entry.create(name=name, task_title=task_title, time_spent=time_spent, note=note)
            print("Saved successfully!")


def view_entries(search_employee=None,
                 search_date=None,
                 search_time_spent=None,
                 search_term=None):
    """View previous entries"""
    entries = Entry.select().order_by(Entry.timestamp.desc())

    if search_employee:
        name = "%" + search_employee + "%"
        entries = entries.where(Entry.name ** name)

    elif search_date:
        pass

    elif search_time_spent:
        pass

    elif search_term:
        # make search_term case insensitive
        term = "%"+ search_term +"%"
        entries = entries.where(Entry.note ** term | Entry.task_title ** term)

    i = 0
    while i < len(entries):
        entry = entries[i]
        timestamp = entry.timestamp.strftime("%A %B %d, %Y %I:%M%p")
        clear()
        print(timestamp)
        print("=" * len(timestamp))
        print(f"NAME: {entry.name}")
        print(f"TASK TITLE: {entry.task_title}")
        print(f"TIME SPENT (minutes): {entry.time_spent}")
        print(f"NOTE: \n{entry.note}")
        print(f"\nEntry {i+1} of {len(entries)}")
        print("=" * len(timestamp))
        print("n) next entry")
        print("p) previous entry")
        print("d) delete entry")
        print("q) return to main menu")

        next_action = input("Action: [Npdq] ").lower().strip()
        if next_action == "q":
            break
        elif next_action == "d":
            delete_entry(entry)
        elif (next_action == "p") & (i > 0):
            i -= 1
        elif (next_action == "n") & (i < len(entries)-1):
            i += 1

def search_entries():
    """Search Entries."""
    search_loop()


def search_by_name():
    """Search Entries by Employee Name"""
    view_entries(search_term=input("Search query: "))
    pass


def search_by_term():
    """Search Entries by term string in title and note)"""
    pass


def search_by_time_spent():
    """Search Entries by time spent"""
    pass


def search_by_date():
    """Search Entries by date"""


def delete_entry(entry):
    """Deletet an entry"""
    if input("Are u sure? [Yn] ").lower() == "y":
        entry.delete_instance()
        print("Entry deleted successfully!")


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


menu = OrderedDict([
    ('a', add_entry),
    ('v', view_entries),
    ("s", search_entries),

])

search_menu = OrderedDict([
    ('d', search_by_date),
    ('n', search_by_name),
    ('s', search_by_term),
    ('t', search_by_time_spent)
])

if __name__ == "__main__":
    initialize()
    menu_loop()