"""Classes for BAC calculation."""
from datetime import datetime
import pandas as pd

import utils

bac_table = pd.read_csv("BAC_by_drink.csv", index_col="Body Weight")

class Person():
  """A person has dimensions and a BAC."""
  
  def __init__(self, name, age, weight, bmi=None):
    """Initialize a non-drunk user."""
    self.name = name
    self.weight = weight
    self.age = age
    self.bmi = bmi
    self.bac = 0.0
    self.current_time = datetime.now()     
  
  def drink(self, drink, time=None):
    """Consume a drink and update BAC."""
    if not time:
      time = datetime.now()
    sd = drink.get_standard_drinks()
    self._update_bac(sd, time)
      
  def _update_bac(self, standard_drinks=0, time=None):
    """Update BAC."""
    self._decrement_bac(time)
    if standard_drinks:
      self._increment_bac(standard_drinks)

  def _decrement_bac(self, time=None):
    """Decrease the BAC since last measure."""
    decrease_per_hour = 0.015
    
    last_time = self.current_time
    if not time:
      self.current_time = datetime.now()
    else:
      self.current_time = time

    time_dif = self.current_time - last_time
    hour_dif = time_dif.seconds / 60. / 60.

    bac_dif = self.bac - hour_dif * decrease_per_hour
    self.bac = max(0.0, bac_dif)
  
  def _increment_bac(self, standard_drinks):
    """Increase bac based off of alcohol consumed."""
    rounded_weight = utils.round_to_nearest_ten(self.weight)
    rounded_drinks = int(round(standard_drinks))
    bac_increase = bac_table[str(rounded_drinks)][rounded_weight]
    self.bac += bac_increase

  def get_bac(self):
    return self.bac


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
