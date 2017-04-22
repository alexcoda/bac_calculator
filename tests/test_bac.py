"""File for testing core of bac module."""
from datetime import datetime, timedelta

# local imports
from context import bac
reload(bac)

Person = bac.Person
Drink = bac.Drink
rtol = 1e-3  # Relative tolerance to use if considering two floats are the same
hour = timedelta(hours=1)
minute = timedelta(minutes=1)
second = timedelta(seconds=1)


class TestPerson:
    """Class for testing the Person implementation."""

    def test_initialize_drink_log(self):
        """Test initializing an empty drink log."""
        cyborg = Person(name='Cyborg', age=1000, weight=350)
        cyborg._init_drink_log()
        time, drink, bac = cyborg._get_last_drink_log_entry()

        assert(datetime.now() - time < second and drink is None and bac == 0.0)

    def test_update_drink_log(self):
        """Test updating the drink log."""
        # TODO
