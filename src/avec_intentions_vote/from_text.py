# coding: utf-8

import argparse
import json
import pathlib
import re

import candidate
from common import PROJECT_DIR
import hypothesis
import page
import poll

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent

PAGE_REGEX = re.compile(r"^--- page ([0-9]+) ---$")
SCORE_REGEX = re.compile(rf"{candidate.REGEX_STR}\s+([0-9,.]+)%")

argparser = argparse.ArgumentParser(description="Extract voting intentions from text")
argparser.add_argument(
    "metadata_file",
    type=pathlib.Path,
    help="Path to the input text file"
    )
argparser.add_argument(
    "--hypotheses",
    type=pathlib.Path,
    default=PROJECT_DIR / "hypotheses.csv",
    help="Path to the hypotheses file"
    )
argparser.add_argument(
    "--candidates",
    type=pathlib.Path,
    default=PROJECT_DIR / "candidats.csv",
    help="Path to the candidates file"
    )

args = argparser.parse_args()

poll_metadata = poll.PollMetadata(args.metadata_file)

pg = None
page_number = None
pages = []

# Lecture du fichier
with poll_metadata.path.open("r", encoding="utf-8") as doc:
    for line in doc:
        line = line.strip()
        if not line:
            continue

        page_match = PAGE_REGEX.match(line)
        if page_match:
            page_number = int(page_match.group(1))
            # Page is targeted ?
            if page_number in poll_metadata.pages:
                pg = page.Page(page_number)
                pages.append(pg)
            else:
                pg = None

            continue
        
        if pg:
            score_match = SCORE_REGEX.match(line)
            if score_match:
                cndt = str(score_match.group(1))
                pg.scores[cndt] = line.replace(cndt, "").strip()

# Building hypothesis list
hypotheses = hypothesis.File(args.hypotheses)

candidate_manager = candidate.Manager()
candidate_manager.load_csv(args.candidates)

for pg in pages:
    print(json.dumps(pg.scores, indent=2, ensure_ascii=False))

    # Searching hypothesis amongst existing ones
    hyp = hypotheses.check(pg.scores.keys())

    unknown_candidates = []
    for cnd in pg.scores.keys():
        if not candidate_manager.find_candidate(cnd):
            unknown_candidates.append(cnd)

    if unknown_candidates:
        print(f"Candidats inconnus : {', '.join(unknown_candidates)}.")

        for cnd in unknown_candidates:
            candidate_manager.add_candidate_from_full_name(cnd)

        candidate_manager.write_csv(args.candidates)

    p = poll_metadata.create_poll(hyp, pg.scores)
    p.write()
