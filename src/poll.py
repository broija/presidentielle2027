# coding: utf-8

from dataclasses import dataclass
import datetime
import json
import pathlib
import re
from typing import Dict, List

import common
import hypothesis
import institute

def date(value:str):
    return datetime.datetime.strptime(value, "%Y%m%d")

@dataclass
class Sample:
    value: int
    population: str

class Poll:
    # Class counters
    first_round_count = 0
    second_round_count = 0

    def __init__(
            self,
            path: pathlib.Path,
            inst: institute.Institute,
            hyp: hypothesis.Hypothesis,
            begin: datetime.datetime,
            end: datetime.datetime,
            sponsor: str,
            samples: Dict[str, List],
            scores: Dict[str, float],
            media: bool=True,
            rolling=None,
            ):
        self.path = path
        self.institute = inst
        self.hypothesis = hyp

        if isinstance(hyp, hypothesis.FirstRoundHypothesis):
            self.__class__.first_round_count += 1
            self.index = self.first_round_count
        else:
            self.__class__.second_round_count += 1
            self.index = self.second_round_count

        self.subid = chr(0x40 + self.index)
        if isinstance(hyp, hypothesis.SecondRoundHypothesis):
            self.subid = '2' + self.subid

        self.begin = begin
        self.end = end
        self.sponsor = sponsor
        self.samples = [Sample(s[0], s[1]) for s in samples]
        self.scores = scores

        self.media = media
        self.rolling = rolling

        if self.begin.year != self.end.year or self.begin.month != self.end.month:
            raise ValueError("Inconsistent dates")

        self.id = (
            f"{self.begin.strftime('%Y%m%d')}_"
            f"{self.end.strftime('%m%d')}_"
            f"{self.institute.short_name}_{self.subid}"
        )

    def write(self):
        output_path = (common.POLL_DIR / self.id).with_suffix(".csv")
        if output_path.exists():
            raise FileExistsError(output_path)

        id_regex = re.compile(rf"^{self.id},")

        # Loading poll file to check if this poll is already present.
        polls_path = common.PROJECT_DIR / "polls.csv"
        with polls_path.open("r") as poll_file:
            for line in poll_file:
                if id_regex.match(line):
                    raise ValueError(f"\"{self.id}\" is already in {polls_path.name}")

        with output_path.open("w") as csv_file:
            csv_file.write("candidat,intentions,erreur_sup,erreur_inf\n")
            for name, score in self.scores.items():
                csv_file.write(','.join([
                    name,
                    str(score),
                    ""
                ]) + "\n")

        with polls_path.open("a") as poll_file:
            poll_file.write(f"{self}\n")

    def __str__(self) -> str:
        items = [
            self.id,
            self.hypothesis.id,
            self.institute.name,
            self.sponsor,
            self.begin.strftime("%Y-%m-%d"),
            self.end.strftime("%Y-%m-%d"),
            str(self.samples[0].value),
            self.samples[0].population,
            self.rolling if self.rolling is not None else "",
            "True" if self.media else "False",
            self.hypothesis.get_round(),
        ]
        for sample in self.samples[1:]:
            items.extend([
                str(sample.value),
                sample.population
            ])

        remaining_samples = 4 - len(self.samples)
        while remaining_samples > 0:
            items.extend(["", ""])
            remaining_samples -= 1

        items.append(str(self.path.name))
        return ','.join(items)

class PollMetadata:
    def __init__(self, metadata_path: pathlib.Path):
        self.metadata_path = metadata_path
        self.metadata = json.load(metadata_path.open("r"))

        self.path = (metadata_path.parent / self.metadata["path"]).resolve(strict=True)
        self.institute = institute.Institute.create_from_path(self.path)
        self.sponsor = self.metadata["sponsor"]
        self.begin = date(self.metadata["begin"])
        self.end = date(self.metadata["end"])
        self.pages = self.metadata["pages"]

        self.polls = self.metadata["polls"]
        self.poll_index = 0

    def create_poll(self, hyp: hypothesis.Hypothesis, scores: Dict[str, float]) -> Poll:
        result = Poll(
            self.path,
            self.institute,
            hyp,
            self.begin,
            self.end,
            self.sponsor,
            self.polls[self.poll_index],
            scores,
            )
        self.poll_index += 1

        return result
