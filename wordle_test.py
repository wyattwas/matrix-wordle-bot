import unittest
from datetime import datetime

from dotenv import load_dotenv

import db


class MyTestCase(unittest.TestCase):
    def test_get_all_guesses_for_user_for_date(self):
        load_dotenv()
        curser = db.setup()
        user_id = '@withoutwyatt:matrix.opencodespace.org'
        date = datetime.today()
        guesses = db.get_all_guesses_for_user_for_date(user_id, date, curser)
        self.assertNotEqual(guesses, [])


if __name__ == '__main__':
    unittest.main()
