import re
from spacy.tokenizer import Tokenizer

from dataclasses import dataclass

# TODO: Move these rules to a resources file
infix_re = re.compile(r"[^a-z0-9]", flags=re.IGNORECASE)
prefix_re = re.compile(r'[\[\]\(]')
special_cases = {"[]": [{"ORTH": "[]"}],
                 "[X]": [{"ORTH": "[X]"}],
                 "Z59.0": [{"ORTH": "Z59.0"}],
                 "z59.0": [{"ORTH": "z59.0"}],
                 "V60.0": [{"ORTH": "V60.0"}],
                 "v60.0": [{"ORTH": "v60.0"}],
                 "Z59.8": [{"ORTH": "Z59.8"}],
                 "z59.8": [{"ORTH": "z59.8"}],
                 "housing/homeless": [{"ORTH": "housing/homeless"}],
                # "d/c'd": [{"ORTH": "d/c'd"}]
                 }

def ssvf_tokenizer(nlp):
    tokenizer = nlp.tokenizer
    for token, pattern in special_cases.items():
        tokenizer.add_special_case(token, pattern)
    # return Tokenizer(rehoused_nlp.vocab,
    #                  rules=special_cases,
    #                  # prefix_search=prefix_re.search,
    #                  )
    #                  # infix_finditer=infix_re.finditer
    return tokenizer

@dataclass
class PreprocessorRule:
    pattern: re.Pattern
    repl: str = ""
    desc: str = None

class SSVFPreprocessor:
    def __init__(self, tokenizer, preprocess_rules, **cfg):
        """Take a raw string text and preprocess and tokenize it.
        Preprocessing steps may include separating certain punctuation and letters
        to enable better punctuation or removing problematic phrases in the text.

        tokenizer (spacy.tokenizer.Tokenizer): A tokenizer with any special cases or additional rules
        preprocess_rules: a list of PreprocessorRules which are similar to tuples containing
            a compiled regular expression pattern and a replacement string.
        """
        self.tokenizer = tokenizer
        self.preprocess_rules = preprocess_rules

    def __call__(self, text):
        """Preprocess and tokenize a raw text file.
        Returns a spacy Doc.
        """
        for rule in self.preprocess_rules:
            text = rule.pattern.sub(rule.repl, text)
        return self.tokenizer(text)