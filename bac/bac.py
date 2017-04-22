"""Classes for BAC calculation."""
from collections import namedtuple
from datetime import datetime
import pandas as pd
import numpy as np
import pickle

# Local imports
from polyfit import polyval2d

log_entry = namedtuple('log_entry', ['time', 'drink', 'bac'])
try:
    with open('bac_polyfit.pkl', 'r') as f:
        poly_coeff = pickle.load(f)
except IOError:
    poly_coeff = \
        np.array([4.44974702e-03, -1.17137983e-04,  9.12197099e-07,
                  -2.12299842e-09,  9.56141142e-02, -8.64115228e-04,
                  3.26934846e-06, -4.39083421e-09,  2.67995601e-04,
                  -7.61634984e-06,  6.75404403e-08, -1.73084231e-10,
                  -1.11933009e-05,  3.28956868e-07, -3.07216348e-09,
                  8.16564848e-12])


class Person():
    """A person has dimensions and a BAC."""
    decrease_per_hour = 0.015

    def __init__(self, name, age, weight, bmi=None):
        """Initialize a non-drunk user."""
        self.name = name
        self.weight = weight
        self.age = age
        self.bmi = bmi
        self._init_drink_log()

    def _init_drink_log(self):
        """Initialize an empty drinking log."""
        index = pd.Index([], name='Time')
        columns = ['Drink', 'BAC']
        self.drink_log = pd.DataFrame([], index, columns)
        self.add_empty_log_entry()

    def add_empty_log_entry(self):
        """Add an empty log entry. Done to keep track of bac decay."""
        self._update_drink_log(time=datetime.now(), bac=0.0, drink_name=None)

    def _update_drink_log(self, time, bac, drink_name):
        """Add a drink or timestep to the drinking log."""
        new_entry = np.array([drink_name, bac]).T
        self.drink_log.loc[time] = new_entry

    def _get_last_drink_log_entry(self):
        """Access the most recent entry in the drink log."""
        num_log_entries = len(self.drink_log)
        last_entry = self.drink_log.iloc[num_log_entries - 1]

        time = last_entry.name.to_pydatetime()
        drink = last_entry['Drink']
        bac = float(last_entry['BAC'])

        return log_entry(time, drink, bac)

    def drink(self, drink, time=None):
        """Consume a drink and update BAC."""
        time = datetime.now() if not time else time
        new_bac = self._determine_new_bac(drink, time)

        self._update_drink_log(time, new_bac, drink.name)

    def _determine_new_bac(self, drink, time):
        """Update BAC."""
        last_drink_time, __, last_bac = self._get_last_drink_log_entry()
        bac_decrease = self._determine_bac_decrease(last_drink_time, time)
        bac_increase = self._determine_bac_increase(drink)

        new_bac = last_bac - bac_decrease + bac_increase
        new_bac = max(new_bac, 0.0)
        return new_bac

    def _determine_bac_decrease(self, start_time, end_time):
        """Determine the BAC decrease since the last time."""
        time_dif = end_time - start_time
        hour_dif = time_dif.seconds / 60. / 60.

        bac_decrease = hour_dif * self.decrease_per_hour
        return bac_decrease

    def _determine_bac_increase(self, drink):
        """Determine the BAC increase based off of a given drink."""
        standard_drinks = drink.get_standard_drinks()
        x = np.array([standard_drinks], dtype='float64')
        y = np.array([self.weight], dtype='float64')

        bac_increase = polyval2d(x, y, poly_coeff)[0]
        return bac_increase


class Drink():
    """A drink has a volume and an alcohol content"""

    def __init__(self, name, volume, abv):
        """Make a drink."""
        self.name = name
        self.volume = volume
        self.abv = abv
        self._verify_abv()
        self.standard_drinks = self._determine_standard_drinks()

    def _verify_abv(self):
        """Verify that abv is a percentage in the range [0, 1]"""
        if self.abv > 1:
            self.abv /= 100.
            # print "ABV = {}".format(self.abv)

    def get_alcohol_content(self):
        """Get the alcohol content of this drink in the given units."""
        return self.volume * self.abv

    def get_standard_drinks(self):
        """Return the number of standard drinks."""
        return self.standard_drinks

    def _determine_standard_drinks(self):
        """Determine the number of standard drinks for this drink."""
        sd = 0.6
        alcohol_content = self.get_alcohol_content()
        return alcohol_content / sd

    def __add__(self):
        """Add two drinks together."""
