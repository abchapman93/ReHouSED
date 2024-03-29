from ..utils import build_nlp

from .helpers import find_ents, _test_label_text, _test_label_texts

import warnings
warnings.filterwarnings("ignore")

nlp = build_nlp()

class TestConcepts:
    def test_simple_concepts(self):
        label_texts = {
            "EVIDENCE_OF_HOMELESSNESS": [
                "The patient is homeless.",
                "Lost her apartment.",
                "lives on street",
                "she does not have stable housing",

            ],
            "TEMPORARY_HOUSING": [
                "She will stay in a shelter",
                "pt states he is staying at the Hope House.",
                "Where are you currently living? The Salvation Army",
                "living at the Dom",
                "Xxxx House"
            ],
            "EVIDENCE_OF_HOUSING": [
                "She lives in an apartment.",
                "apartment",
                "house",
                "home",
                "permanent housing",

            ],
            "RISK_OF_HOMELESSNESS": [
                "eviction notice",
                "housing instability",
            ],
            "IGNORE": [
                "chronically homeless individuals",
                "homeless individuals",
                "permanent housing program"
            ]
        }
        _test_label_texts(nlp, label_texts)

