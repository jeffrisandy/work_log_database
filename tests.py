import unittest
from unittest.mock import patch
import datetime
# (see: https://dev.to/patrnk/how-to-test-input-processing-in-python-3)

from peewee import SqliteDatabase

from app import WorkLog, Entry

db = SqliteDatabase(":memory:")
log = WorkLog(db)


class WorkLogTests(unittest.TestCase):

    def test_get_int_number(self):
        with patch('builtins.input', side_effect=['21']):
            output = log.get_int_number("")

        self.assertEqual(output, 21)

    def test_entry_to_db(self):
        with patch('builtins.input', side_effect=['y'] ):
            data = {"name": "Jeff",
                    "task_title": "task test",
                    "time_spent": 15,
                    "note": "test note"}

            log.add_entry_to_db(**data)

            entry = Entry.select(Entry.id).where((Entry.name == data['name']) &
                                         (Entry.task_title == data['task_title']) &
                                         (Entry.time_spent == data['time_spent']) &
                                         (Entry.note == data['note'])
                                         )

            self.assertEqual(len(entry), 1)

    def test_get_date(self):
        input_date = "12/06/2019"
        fmt = "%d/%m/%Y"
        expected = datetime.datetime.strptime(input_date, fmt)

        with patch('builtins.input', side_effect=[input_date]):
            self.assertEqual(log.get_date(""), expected)

    def test_quit_menu_loop(self):
        with patch('builtins.input', side_effect=['v', 'q', 'q']):
            output = log.menu_loop()
            self.assertIsNotNone(output)

    def test_quit_search_loop(self):
        with patch('builtins.input', side_effect=['d', 'xxx', '', 'q']):
            output = log.search_loop()
            self.assertIsNotNone(output)

if __name__ == "__main__":
    unittest.main()