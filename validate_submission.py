#!/usr/bin/env python3

import csv
import re
import sys
from pathlib import Path


REQUIRED_HEADER = [
    "candidate_id",
    "rank",
    "score",
    "reasoning"
]

CANDIDATE_ID_PATTERN = re.compile(
    r"^CAND_[0-9]{7}$"
)


def validate_submission(csv_path):

    errors=[]

    path=Path(csv_path)

    if path.suffix.lower()!=".csv":
        errors.append(
            "Filename must use .csv"
        )

    try:

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as f:

            reader=csv.reader(f)

            try:
                header=next(reader)

            except StopIteration:

                errors.append(
                    "File empty"
                )

                return errors


            if header!=REQUIRED_HEADER:

                errors.append(
                    "Wrong header"
                )


            rows=[]

            for row in reader:

                if any(
                    x.strip()
                    for x in row
                ):

                    rows.append(
                        row
                    )

    except Exception as e:

        errors.append(
            str(e)
        )

        return errors


    if len(rows)!=100:

        errors.append(
            f"Need exactly 100 rows. Found {len(rows)}"
        )


    ids=set()

    ranks=set()

    scores=[]


    for row in rows:

        if len(row)!=4:

            errors.append(
                "Wrong number columns"
            )

            continue


        cid=row[0]

        rank=row[1]

        score=row[2]


        if not CANDIDATE_ID_PATTERN.match(cid):

            errors.append(
                f"Bad ID {cid}"
            )


        if cid in ids:

            errors.append(
                f"Duplicate {cid}"
            )

        ids.add(cid)


        try:

            rank=int(rank)

            if rank<1 or rank>100:

                errors.append(
                    f"Bad rank {rank}"
                )

            ranks.add(rank)

        except:

            errors.append(
                f"Rank error {rank}"
            )


        try:

            score=float(score)

            scores.append(score)

        except:

            errors.append(
                f"Score error {score}"
            )


    for i in range(
        len(scores)-1
    ):

        if scores[i] < scores[i+1]:

            errors.append(
                "Scores increasing"
            )


    if len(ranks)!=100:

        errors.append(
            "Ranks not unique"
        )


    return errors



if __name__=="__main__":

    if len(sys.argv)!=2:

        print(
            "Usage:"
        )

        print(
            "python validate_submission.py yourfile.csv"
        )

        sys.exit()


    errors=validate_submission(
        sys.argv[1]
    )


    if errors:

        print(
            "\nFAILED\n"
        )

        for e in errors:

            print("-",e)

    else:

        print(
            "\nSubmission is valid\n"
        )