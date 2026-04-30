import os
import sys
import psycopg2

# Adding current folder to Python path so config.py is always found
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import load_config


def connect():
    return psycopg2.connect(**load_config())