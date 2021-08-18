import re
from spacy.tokenizer import Tokenizer

from dataclasses import dataclass

# TODO: Move these rules to a resources file
infix_re = re.compile(r"[^a-z0-9]", flags=re.IGNORECASE)
prefix_re = re.compile(r'[\[\]\(]')
special_cases = {"[]": [{"ORTH": "[]"}],
                 "[X]": [{"ORTH": "[X]"}],
                 "Z59.0": [{"ORTH": "Z59.0"}],
                 "z59.0": [{"ORTH": "Z59.0"}],
                 "V60.0": [{"ORTH": "V60.0"}],
                 "v60.0": [{"ORTH": "V60.0"}],
                 "Z59.8": [{"ORTH": "Z59.8"}],
                 "z59.8": [{"ORTH": "Z59.8"}],
                 "housing/homeless": [{"ORTH": "housing/homeless"}],
                 }

def ssvf_tokenizer(nlp):
    tokenizer = nlp.tokenizer
    for token, pattern in special_cases.items():
        tokenizer.add_special_case(token, pattern)
    return tokenizer
