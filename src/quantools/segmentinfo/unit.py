"""
Unit Enum for T1 and T2 relaxation times.

@Author: Jannik Stebani 2024
"""
import enum

class Unit(enum.Enum):
    SECONDS = 'seconds'
    MILLISECONDS = 'milliseconds'
    NONE = 'none'