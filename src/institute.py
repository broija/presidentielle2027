# coding: utf-8

import pathlib
import re

MAPPING = {
    "Cluster17": "cl",
    "ELABE": "el",
    "Harris Interactive": "hi",
    "IFOP": "if",
    "Ipsos BVA": "ip",
    "Odoxa": "od",
    "OpinionWay": "ow",
}

PATH_MAPPING = { k.lower().replace(' ', ""): k for k in MAPPING.keys() }

REGEX = re.compile('.+(' + "|".join(MAPPING.keys()) + ').+', re.IGNORECASE)

MAPPING_LC = {}
INSTITUTES = []
INSTITUTES_LC = []

class Institute:
    @staticmethod
    def create_from_path(path: pathlib.Path) -> "Institute":
        return Institute(get_name_from_path(path))

    def __init__(self, name: str):
        self.name = name
        self.short_name = MAPPING[name]

for k, v in MAPPING.items():
    k_lower = k.lower()
    MAPPING_LC[k_lower] = v
    INSTITUTES.append(k)
    INSTITUTES_LC.append(k_lower)

def get_name_from_path(path: pathlib.Path):
    match = REGEX.match(path.name)
    if not match:
        raise ValueError("Institute name not found in input path")

    return PATH_MAPPING[match.group(1).lower()]
