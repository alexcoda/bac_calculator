"""Classes for BAC calculation."""
from datetime import datetime
import pandas as pd
import numpy as np

# Local imports
from utils import round_to_nearest_ten

bac_table = pd.read_csv("BAC_by_drink.csv", index_col="Body Weight")

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

    init_time = datetime.now()
    init_bac = 0.0
    self._update_drink_log(init_time, init_bac)

  def _update_drink_log(self, time, bac, drink_name=None):
    """Add a drink or timestep to the drinking log."""
    new_entry = np.array([drink_name, bac]).T
    self.drink_log.loc[time] = new_entry

  def _get_last_drink_log_entry(self):
    """Access the most recent entry in the drink log."""
    num_log_entries = len(self.drink_log)
    return self.drink_log.iloc[num_log_entries - 1]

  def drink(self, drink, time=None):
    """Consume a drink and update BAC."""
    time = datetime.now() if not time else time
    new_bac = self._determine_new_bac(drink, time)

    self._update_drink_log(time, new_bac, drink.name)

  def _determine_new_bac(self, drink, time):
    """Update BAC."""
    last_drink_entry = self._get_last_drink_log_entry()
    last_drink_time = last_drink_entry.name.to_pydatetime()
    last_bac = float(last_drink_entry['BAC'])

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
    rounded_weight = round_to_nearest_ten(self.weight)
    rounded_drinks = int(round(standard_drinks))

    bac_increase = bac_table[str(rounded_drinks)][rounded_weight]
    return bac_increase


class Drink():
  """A drink has a volume and an alcohol content"""

  def __init__(self, name, volume, abv):
    """Make a drink."""
    self.name = name
    self.sd = 1  # Number of standard drinks, currently everything is 1 beer
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
