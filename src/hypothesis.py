# coding: utf-8

import abc
import hashlib
import pathlib
import re
import sys
from typing import Dict, List

HYPOTHESIS_REGEX = re.compile(r'^(H([0-9_]+)),"([^"]+)"')

class Hypothesis:
    @staticmethod
    def get_class_name(candidates: List[str]) -> str:
        return "FirstRoundHypothesis" if len(candidates) > 2 else "SecondRoundHypothesis"

    @classmethod
    def get_class(cls, candidates: List[str]) -> str:
        return getattr(sys.modules[__name__], cls.get_class_name(candidates))

    @classmethod
    def create(cls, id: str, candidates: List[str]) -> "Hypothesis":
        return cls.get_class_name(candidates)(id, candidates)

    @classmethod
    def create(cls, number: int, candidates: List[str]) -> "Hypothesis":
        c = cls.get_class(candidates)

        return c(c.build_id(number), candidates)

    @staticmethod
    @abc.abstractmethod
    def build_id(number: int) -> str:
        pass

    @staticmethod
    @abc.abstractmethod
    def get_round() -> str:
        pass

    def __init__(self, id: str, candidates: List[str]):
        if not isinstance(id, str):
            raise ValueError(f"{id} must be of type str")

        self.id = id
        self.candidates = candidates
        self.hash = hashlib.sha256(','.join(candidates).encode("utf-8")).hexdigest()

    def get_key(self) -> str:
        """Candidate list unique key."""

        return ','.join(sorted(self.candidates))

    def __str__(self) -> str:
        return f"{self.id},\"{self.get_key()}\",{self.hash}\n"

class FirstRoundHypothesis(Hypothesis):
    @staticmethod
    def build_id(number: int):
        return f"H{number}"

    @staticmethod
    def get_round() -> str:
        return "1er Tour"

class SecondRoundHypothesis(Hypothesis):
    @staticmethod
    def build_id(number: int):
        return f"H2_{number}"

    @staticmethod
    def get_round() -> str:
        return "2nd Tour"

class File:
    def __init__(self, path: pathlib.Path) -> Dict[str, Hypothesis]:
        self.path = path

        self.hypotheses = {}
        self.first_round_max = 0
        self.second_round_max = 0

        # Loading hypotheses
        with path.open("r", encoding="utf-8") as doc:
            for line in doc:
                line = line.strip()
                if not line:
                    continue

                hyp_match = HYPOTHESIS_REGEX.match(line)
                if hyp_match:
                    hyp_number = hyp_match.group(2)
                    candidates = [c.strip() for c in hyp_match.group(3).split(',') if c.strip()]
                    hyp_class = Hypothesis.get_class(candidates)

                    if hyp_class is FirstRoundHypothesis:
                        number = int(hyp_number)
                        if number > self.first_round_max:
                            self.first_round_max = number
                    else:
                        number = int(hyp_number.split('_')[1])
                        if number > self.second_round_max:
                            self.second_round_max = number

                    hyp = hyp_class.create(number, candidates)
                    
                    hyp_key = hyp.get_key()
                    if hyp_key in self.hypotheses:
                        raise ValueError(f"Hypothesis {hyp.id} already encountered in {self.hypotheses[hyp_key].id}")

                    self.hypotheses[hyp_key] = hyp

    def check(self, candidates: List[str]) -> Hypothesis:
        """Check if hypothesis exists. If not, append it to the hypothesis file."""

        result = None

        key = ','.join(sorted(candidates))
        if key not in self.hypotheses:
            cls = Hypothesis.get_class(candidates)
            if cls is FirstRoundHypothesis:
                self.first_round_max += 1
                number = self.first_round_max
            else:
                self.second_round_max += 1
                number = self.second_round_max

            result = Hypothesis.create(
                number,
                candidates
                )

            id_regex = re.compile(rf"^{result.id}")

            # Checking if hypothesis is already known
            with self.path.open("r") as hyp_file:
                for line in hyp_file:
                    if id_regex.match(line):
                        raise ValueError(f"Hypothesis\"{result.id}\" already present in {self.path.name}")

            self.hypotheses[key] = result

            with self.path.open("a") as hyp_file:
                hyp_file.write(str(result))
        else:
            result = self.hypotheses[key]

        return result


