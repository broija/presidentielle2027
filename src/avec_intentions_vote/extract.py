# coding: utf-8

import argparse
import json
import pathlib

import candidate
from common import PROJECT_DIR
import hypothesis
import poll

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent

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

# Lecture du fichier
pages = poll_metadata.get_pages()

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
