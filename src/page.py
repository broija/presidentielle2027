# coding: utf-8

import collections

from typing import Dict

class Page:
    def __init__(self, number: int):
        self.number = number
        self.scores: collections.OrderedDict[str, float] = collections.OrderedDict()
