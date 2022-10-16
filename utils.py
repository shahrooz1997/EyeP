import sys
import math


def is_linux_based():
    return sys.platform.startswith("linux") or sys.platform.startswith("darwin")


def compute_distance(p1, p2):
    return math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)
