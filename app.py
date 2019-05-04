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


class WorkLog:

    def __init__(self, dbs):
        """Create the database and table if they don't exist"""
        dbs.bind([Entry])
        dbs.connect()
        dbs.create_tables([Entry], safe=True)

        # menus
        self.menu = OrderedDict([
            ('a', self.add_entry),
            ('v', self.view_entries),
            ("s", self.search_entries),

        ])

        # search menu
        self.search_menu = OrderedDict([
            ('a', self.search_by_date),
            ('b', self.search_by_date_range),
            ('c', self.search_by_name),
            ('d', self.search_by_term),
            ('e', self.search_by_time_spent)
        ])

        # edit menu
        self.edit_menu = OrderedDict([
            ("a", self.edit_name),
            ("b", self.edit_date),
            ("c", self.edit_task_title),
            ("d", self.edit_time_spent),
            ("e", self.edit_note)
        ])

    def menu_loop(self):
        """ Show the menu """
        choice = None

        while choice != 'q':
            self.clear()
            print("WORK LOG")
            print("What would you like to do?")
            print("Press 'q' to quit.")

            for k, v in self.menu.items():
                print(f"{k}) {v.__doc__}")
            choice = input('Action: ').lower().strip()

            if choice in self. menu:
                self.clear()
                self.menu[choice]()
        return choice

    def search_loop(self):
        """ Show the search menu """
        choice = None

        while choice != 'q':
            self.clear()
            print("SEARCH ENTRIES")
            print("What would you like to search?")
            print("Press 'q' to quit.")

            for k, v in self.search_menu.items():
                print(f"{k}) {v.__doc__}")
            choice = input('Action: ').lower().strip()

            if choice in self.search_menu:
                self.clear()
                self.search_menu[choice]()
        return choice

    def add_entry(self):
        """Add an entry."""

        name = input("Name: ")
        task_title = input("Task Title: ")
        time_spent = self.get_int_number("Time spent (rounded in minutes: ")
        try:
            print("Notes (optional, you can leave this empty. When finished press 'ctr+d' for unix user or 'ctr+z then enter' for window user.")
            note = sys.stdin.read().strip()
        except EOFError:
            note = ""

        # add to db
        self.add_entry_to_db(name, task_title, time_spent, note)

    @staticmethod
    def add_entry_to_db(name, task_title, time_spent, note):
        if name:
            if input("\n\nSave entry? [Yn] ").lower() != 'n':
                Entry.create(name=name, task_title=task_title, time_spent=time_spent, note=note)
                print("Saved successfully!")

    def view_entries(self,
                     search_name=None,
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
        self.display_entry(entries_ids)

    def display_entry(self, entries_ids):

        if entries_ids:
            i = 0
            while i < len(entries_ids):
                entry_id = entries_ids[i]
                entry = Entry.get(Entry.id == entry_id)
                timestamp = entry.timestamp.strftime("%A %B %d, %Y %I:%M%p")
                self.clear()
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
                    self.edit_entry(entry)

                elif next_action == "d":
                    self.delete_entry(entry)
                    entries_ids.remove(entry_id)

                elif (next_action == "p") & (i > 0):
                    i -= 1
                elif (next_action == "n") & (i < len(entries_ids)-1):
                    i += 1
        else:
            input("Entry is not found. Press enter to return to search menu. ")

    def search_entries(self):
        """Search Entries."""
        self.search_loop()

    def search_by_name(self):
        """Search Entries by Employee Name"""
        self.view_entries(search_name=input("Search by name: "))

    def search_by_term(self):
        """Search Entries by term string in title and note)"""
        self.view_entries(search_term=input("Search by term string: "))

    def search_by_time_spent(self):
        """Search Entries by time spent"""

        time_spent_input = self.get_int_number("Search by time spent (rounded minutes): ")
        self.view_entries(search_time_spent=time_spent_input)

    def search_by_date(self):
        """Search Entries by date"""
        date_input = self.get_date("Search by date.")
        self.view_entries(search_date=date_input)

    def search_by_date_range(self):
        """Search Entry by range of dates"""
        print("Search by range of dates")
        start_date = self.get_date("Start date.")
        end_date = self.get_date("End date")
        self.view_entries(search_date_range=(start_date, end_date))

    def delete_entry(self, entry):
        """Delete an entry"""
        if input("Are u sure? [Yn] ").lower() == "y":
            entry.delete_instance()
            print("Entry deleted successfully!")

    def edit_entry(self, entry):
        """Edit an entry"""

        choice = None
        while choice != "q":
            self.clear()
            print("EDIT ENTRY")
            print("What field would you like to edit?")
            print("Press 'q' to return to the previous menu.")

            for k, v in self.edit_menu.items():
                print(f"{k}) {v.__doc__}")

            choice = input('Action: ').lower().strip()

            if choice in self.edit_menu:
                self.edit_menu[choice](entry)

    def edit_name(self, entry):
        """Name"""
        self.clear()
        name = input("Name : ")
        param = {'name': name}
        self.update_entry(entry, param)

    def edit_date(self, entry):
        """Date"""
        self.clear()
        timestamp = self.get_date("Edit Date", timestamp=True)
        param = {"timestamp": timestamp}
        self.update_entry(entry, param)

    def edit_task_title(self, entry):
        """Task title"""
        self.clear()
        task_title = input("Task title: ")
        param = {"task_title": task_title}
        self.update_entry(entry, param)

    def edit_time_spent(self, entry):
        """Time spent"""
        self.clear()
        time_spent = self.get_int_number("Time Spent (rounded minutes): ")
        param = {"time_spent": time_spent}
        self.update_entry(entry, param)

    def edit_note(self, entry):
        """Note"""
        self.clear()
        print("Note (press ctr+d when finished) : ")
        note = sys.stdin.read().strip()
        param = {"note": note}
        self.update_entry(entry, param)

    @staticmethod
    def update_entry(entry, param_dict):
        entry.update(**param_dict).execute()
        fields = [ k for k, _ in param_dict.items()]
        input(f"\nLog field of '{', '.join(fields)}' edited successfully! Press Enter to continue")

    @staticmethod
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

    @staticmethod
    def get_int_number(msg):
        """Get user input integer number"""
        while True:

            user_input = input(msg)

            try:
                int_num = int(user_input)
            except ValueError:
                print("The value entered was not a number, try again")
            else:
                return int_num

    @staticmethod
    def clear():
        os.system('cls' if os.name == 'nt' else 'clear')



if __name__ == "__main__":
    work_log = WorkLog(db)
    work_log.menu_loop()