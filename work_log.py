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


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


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

        if choice in search_menu:
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


def view_entries(search_name=None,
                 search_date=None,
                 search_date_range = None,
                 search_time_spent=None,
                 search_term=None):
    """View previous entries"""

    entries = Entry.select(Entry.id).order_by(Entry.timestamp.desc())

    if search_name:
        name = "%" + search_name + "%"
        entries = entries.where(Entry.name ** name)

    elif search_date:
        entries = entries.where( (Entry.timestamp.year == search_date.year) &
                                 (Entry.timestamp.month == search_date.month) &
                                 (Entry.timestamp.day == search_date.day))

    elif search_date_range:
        start_date, end_date = search_date_range
        entries = entries.where(Entry.timestamp <= start_date and Entry.timestamp <= end_date)

    elif search_time_spent:
        entries = entries.where(Entry.time_spent == search_time_spent)

    elif search_term:
        # make search_term case insensitive
        term = "%"+ search_term +"%"
        entries = entries.where(Entry.note ** term | Entry.task_title ** term)

    # convert to a list of id
    entries_ids = [entry.id for entry in entries]
    display_entry(entries_ids)


def display_entry(entries_ids):

    if entries_ids:
        i = 0
        while i < len(entries_ids):
            entry_id = entries_ids[i]
            entry = Entry.get(Entry.id == entry_id)
            timestamp = entry.timestamp.strftime("%A %B %d, %Y %I:%M%p")
            clear()
            print(timestamp)
            print("=" * len(timestamp))
            print(f"ID: {entry.id} ")
            print(f"NAME: {entry.name}")
            print(f"TASK TITLE: {entry.task_title}")
            print(f"TIME SPENT (minutes): {entry.time_spent}")
            print(f"NOTE: \n{entry.note}")
            print(f"\nEntry {i+1} of {len(entries_ids)}")
            print("=" * len(timestamp))
            print("n) next entry")
            print("p) previous entry")
            print("e) edit entry")
            print("d) delete entry")
            print("q) return to main menu")

            next_action = input("Action: [Npdq] ").lower().strip()
            if next_action == "q":
                break
            elif next_action == "e":
                edit_entry(entry)

            elif next_action == "d":
                delete_entry(entry)
                entries_ids.remove(entry_id)

            elif (next_action == "p") & (i > 0):
                i -= 1
            elif (next_action == "n") & (i < len(entries_ids)-1):
                i += 1
    else:
        input("Entry is not found. Press enter to return to search menu. ")


def search_entries():
    """Search Entries."""
    search_loop()


def search_by_name():
    """Search Entries by Employee Name"""
    view_entries(search_name=input("Search by name: "))


def search_by_term():
    """Search Entries by term string in title and note)"""
    view_entries(search_term=input("Search by term string: "))


def search_by_time_spent():
    """Search Entries by time spent"""

    time_spent_input = get_int_number("Search by time spent (rounded minutes): ")
    view_entries(search_time_spent=time_spent_input)


def search_by_date():
    """Search Entries by date"""
    date_input = get_date("Search by date.")
    view_entries(search_date=date_input)


def search_by_date_range():
    """Search Entry by range of dates"""
    print("Search by range of dates")
    start_date = get_date("Start date.")
    end_date = get_date("End date")
    view_entries(search_date_range=(start_date, end_date))


def delete_entry(entry):
    """Delete an entry"""
    if input("Are u sure? [Yn] ").lower() == "y":
        entry.delete_instance()
        print("Entry deleted successfully!")


def edit_entry(entry):
    """Edit an entry"""

    choice = None
    while choice != "q":
        clear()
        print("EDIT ENTRY")
        print("What field would you like to edit?")
        print("Press 'q' to return to the previous menu.")

        for k, v in edit_menu.items():
            print(f"{k}) {v.__doc__}")

        choice = input('Action: ').lower().strip()

        if choice in edit_menu:
            edit_menu[choice](entry)



def edit_name(entry):
    """Name"""
    clear()
    name = input("Name : ")
    param = {'name': name}
    update_entry(entry, param)

def edit_date(entry):
    """Date"""
    clear()
    timestamp = get_date("Edit Date", timestamp=True)
    param = {"timestamp": timestamp}
    update_entry(entry, param)

def edit_task_title(entry):
    """Task title"""
    clear()
    task_title = input("Task title: ")
    param = {"task_title": task_title}
    update_entry(entry, param)

def edit_time_spent(entry):
    """Time spent"""
    clear()
    time_spent = get_int_number("Time Spent (rounded minutes): ")
    param = {"time_spent": time_spent}
    update_entry(entry, param)

def edit_note(entry):
    """Note"""
    clear()
    print("Note (press ctr+d when finished) : ")
    note = sys.stdin.read().strip()
    param = {"note": note}
    update_entry(entry, param)

def update_entry(entry, param_dict):
    entry.update(**param_dict).execute()
    fields = [ k for k, _ in param_dict.items()]
    input(f"\nLog field of '{', '.join(fields)}' edited successfully! Press Enter to continue")

def get_date(msg, timestamp=False):
    """
    Get user input date
    :param msg: string, additional msg to display to user
    :param timestamp: boolean, get date and time
    :return: datetime object
    """
    if timestamp:
        msg += "\nPlease use 'DD/MM/YYYY HH:MM' (24 hour) format: "
        fmt = "%d/%m/%Y %H:%M"
    else:
        msg += "\nPlease use 'DD/MM/YYYY' format: "
        fmt = "%d/%m/%Y"

    while True:
        input_date = input(msg)
        try:
            date = datetime.datetime.strptime(input_date, fmt)
        except ValueError:
            print(f"{input_date} doesn't seem to be a valid date or format.")
        else:
            return date


def get_int_number(msg):
    """Get user input integer number"""
    clear()
    while True:

        user_input = input(msg)

        try:
            int_num = int(user_input)
        except ValueError:
            print("The value entered was not a number, try again")
        else:
            return int_num


menu = OrderedDict([
    ('a', add_entry),
    ('v', view_entries),
    ("s", search_entries),

])

search_menu = OrderedDict([
    ('1', search_by_date),
    ('2', search_by_date_range),
    ('3', search_by_name),
    ('4', search_by_term),
    ('5', search_by_time_spent)
])

edit_menu = OrderedDict([
    ("a", edit_name),
    ("b", edit_date),
    ("c", edit_task_title),
    ("d", edit_time_spent),
    ("e", edit_note)
])

if __name__ == "__main__":
    initialize()
    menu_loop()