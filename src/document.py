# coding: utf-8

import abc
import collections
import pathlib
import re

import candidate
import page

PAGE_REGEX = re.compile(r"^--- page ([0-9]+) ---$")
SCORE_REGEX = re.compile(rf"{candidate.REGEX_STR}\s+([0-9,.]+)%")
NUMBER_REGEX = re.compile(r"^([0-9.]+)")

FILTER_LIST = [
    "Ne se prononcent pas"
]

class Document(abc.ABC):
    def __init__(self, path: pathlib.Path, pages: list[int]):
        self.path = path
        self.pages = pages

    @abc.abstractmethod
    def get_pages(self) -> list[page.Page]:
        pass

class ExtractedText(Document):
    def get_pages(self) -> list[page.Page]:
        pg = None
        page_number = None
        result = []

        with self.path.open("r", encoding="utf-8") as doc:
            for line in doc:
                line = line.strip()
                if not line:
                    continue

                page_match = PAGE_REGEX.match(line)
                if page_match:
                    page_number = int(page_match.group(1))
                    # Page is targeted ?
                    if page_number in self.pages:
                        pg = page.Page(page_number)
                        result.append(pg)
                    else:
                        pg = None

                    continue
                
                if pg:
                    score_match = SCORE_REGEX.match(line)
                    if score_match:
                        cndt = str(score_match.group(1))
                        pg.scores[cndt] = line.replace(cndt, "").strip()

        return result

# -----

from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer

class PDF(Document):
    def get_pages(self) -> list[page.Page]:
        result = []

        index = -1

        for page_layout in extract_pages(self.path, page_numbers=self.pages):
            candidates = {}
            scores = {}
            index += 1
            for element in page_layout:
                if isinstance(element, LTTextContainer):
                    text = element.get_text().strip()
                    y = int(element.y0)

                    candidate_match = candidate.REGEX.match(text)
                    if candidate_match:
                        candidates[y] = text
                        continue
                    number_match = NUMBER_REGEX.match(text)
                    if number_match:
                        scores[y] = text
                        continue

            candidates = collections.OrderedDict(sorted(candidates.items(), reverse=True))
            scores = collections.OrderedDict(sorted(scores.items(), reverse=True))

            p = page.Page(self.pages[index])

            for y, v in scores.items():
                # Si candidat sur la même ligne
                if y in candidates and candidates[y].lower() != "total":
                    cndt = candidates[y]
                    if cndt in candidate.MAP:
                        cndt = candidate.MAP[cndt]
                    elif cndt in FILTER_LIST:
                        continue
                    p.scores[cndt] = v

            result.append(p)

        return result
