"""Misc helper functions for bac calculation."""
from datetime import datetime
from functools import wraps

def round_to_nearest_ten(num):
  """Round a number to the nearest ten."""
  return int(round(num, -1))