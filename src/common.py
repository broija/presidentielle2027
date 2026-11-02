# coding: utf-8

import pathlib

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent

PROJECT_DIR = SCRIPT_DIR.parent
POLL_DIR = PROJECT_DIR / "polls"