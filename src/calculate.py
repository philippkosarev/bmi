"""Calculates body-health metrics and health thresholds for them.

All distance values are assumed to be in centimetres.
All mass values are assumed to be in kilograms.
"""


# Imports
import math

# Internal imports
from .widgets.shared import Gender


def bmi(height: float, mass: float) -> float:
  """Calculates the Body Mass Index."""
  result = mass / ((height / 100) ** 2)
  return result


def bri(height: float, waist: float) -> float|None:
  """Calculates the Body Roundness Index."""
  bri = 1 - (waist / (math.pi * height)) ** 2
  try:
    bri = math.sqrt(bri)
  except (ZeroDivisionError, ValueError):
    return
  bri = 364.2 - (365.5 * bri)
  return bri


def whr(waist: float, hip: float) -> float:
  """Calculates Waist to Hip Ratio."""
  return waist / hip


def whtr(waist: float, height: float) -> float:
  """Calculates To Height Ratio."""
  return waist / height


def mass_from_bmi_and_height(bmi: float, height: float) -> float:
  """Calculates mass from BMI and height."""
  return bmi * ((height / 100) ** 2)


def whtr_unhealthy(age: int) -> float:
  """Calculates the "unhealthy" WHTR thershold for a given age."""
  if   age > 40: return ((age - 40) / 100) + 0.5
  elif age > 50: return 0.6
  else:          return 0.5


_whr_overweight_thresholds = {
  Gender.AVERAGE: 0.85,
  Gender.FEMALE: 0.8,
  Gender.MALE: 0.9,
}

def whr_overweight(gender: int) -> float:
  """Returns the "overweight" thershold for Waist to Hip Ratio."""
  gender = Gender(gender)
  return _whr_overweight_thresholds[gender]


_whr_obese_thresholds = {
  Gender.AVERAGE: 0.925,
  Gender.FEMALE: 0.85,
  Gender.MALE: 1,
}


def whr_obese(gender: int) -> float:
  """Returns "obese" threshold for WHR."""
  gender = Gender(gender)
  return _whr_obese_thresholds[gender]
