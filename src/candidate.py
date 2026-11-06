# coding: utf-8

import pathlib
import re
from typing import Dict, List

REGEX_STR = r"([A-Za-zÀ-ȕ- ]+[A-Za-zÀ-ȕ])"
REGEX = re.compile(REGEX_STR)

MAP = {
    "Edouard Philippe": "Édouard Philippe"
}

class Candidate:
    def __init__(self, id: str, first_name: str, last_name: str):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name

class Manager:
    def __init__(self):
        # Prénom d'abord
        self.candidates_first: Dict[str, Candidate] = {}
        # Nom d'abord
        self.candidates_last: Dict[str, Candidate] = {}

        self.candidates_by_id: Dict[str, Candidate] = {}

        self.new_candidates: List[Candidate] = []

    def load_csv(self, filepath: pathlib.Path):
        with filepath.open("r", encoding="utf-8") as f:
            lines = f.readlines()

        for line in lines[1:]:  # Skip header
            parts = line.strip().split(",")
            if len(parts) >= 3:
                candidate = Candidate(id=parts[0], first_name=parts[2].strip(), last_name=parts[3].strip())
                self.add_candidate(candidate)

    def add_candidate(self, candidate: Candidate):
        first_name = candidate.first_name.lower()
        last_name = candidate.last_name.lower()
        self.candidates_first[first_name + " " + last_name] = candidate
        self.candidates_last[last_name + " " + first_name] = candidate
        self.candidates_by_id[candidate.id] = candidate

    def find_candidate(self, full_name: str) -> Candidate:
        result = None

        full_name = full_name.strip().lower()
        if full_name in self.candidates_first:
            result = self.candidates_first[full_name]
        elif full_name in self.candidates_last:
            result = self.candidates_last[full_name]

        return result
    
    def add_candidate_from_full_name(self, full_name: str):
        full_name_lower = full_name.strip().lower()
        if full_name_lower in self.candidates_first or full_name_lower in self.candidates_last:
            raise ValueError(f"Candidat {full_name} déjà présent dans le fichier.")
        
        parts = full_name.split(" ", 1)

        first_name, last_name = parts

        # Construction de l'ID à partir de la première lettre de chaque mot
        words = re.findall(r"\w+", full_name)

        candidate_id = "".join(word[0].upper() for word in words)
        if candidate_id in self.candidates_by_id:
            print(f"ID {candidate_id} déjà utilisé pour un autre candidat. Tentative de différenciation...")
            candidate_id += words[-1][1]

            if candidate_id in self.candidates_by_id:
                raise ValueError(f"ID {candidate_id} déjà utilisé pour un autre candidat.")
        candidate = Candidate(id=candidate_id, first_name=first_name, last_name=last_name)
        self.add_candidate(candidate)
        self.new_candidates.append(candidate)
    
    def write_csv(self, filepath: pathlib.Path):
        with filepath.open("a", encoding="utf-8") as f:
            for candidate in self.new_candidates:
                line = f"{candidate.id},{candidate.first_name},{candidate.last_name},,,,\n"
                f.write(line)
