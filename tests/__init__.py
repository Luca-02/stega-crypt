import sys
import os

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

SRC_DIR = os.path.join(BASE_DIR, 'src')
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)