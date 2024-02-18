from ..utils import build_nlp

from .helpers import find_ents

import warnings
warnings.filterwarnings("ignore")

nlp = build_nlp()

class TestConcepts:
    def test_classifications(self):

        text_classifications = {
            "UNSTABLY_HOUSED":
                [
                    "The patient is homeless.",
                    "He is looking for an apartment.",
                    "Would like his own apartment.",
                    "Veteran is searching for housing",
                    "Veteran is looking at an apartment",
                    "Needs: stable housing",
                    "Goals: stable housing",
                    "She will stay in a shelter",
                    "He has a goal of looking for housing",
                    "Lives in his car",
                    "cannot pay rent",
                    "staying at Xxx Xxxx",
                    "interested in housing",
                    "he requires rental assistance",
                    "he requires housing assistance",
                    "Patient needs: include stable housing",
                    "eligible for hud-vash",
                    "lives in his car",
                    "lives in the park",
                    "Housing Status: car",
                    "I met her at the shelter to do a home visit",
                    "she is staying at her sister's house",
                    # "his uncle let him stay at his house",
                    "He applied to an apartment",
                    "apply for gpd",
                    "apply for permanent housing",
                    "would like a house",
                    "[X] homeless",
                    "sleeps in a park",
                ],
            "STABLY_HOUSED": [
                "She lives in an apartment.",
                "She is not homeless",
                "Has his own apartment",
                "paid her rent",
                "stably housed",
                "Goals: maintain stable housing",
                "Assist veteran in maintaining stable housing",
                "Assist veteran in maintaining housing",
                "he receives rental assistance",
                "he receives housing assistance",
                "Patient goals: maintain stable housing",
                "Patient goals: maintain housing",
                "patient's goals are to maintain stable housing",
                "patient wants to maintain stable housing",
                # "got an apartment through hud-vash",
                "lives in va supported housing",
                "I met her to do a home visit",
                # "his house",
                "He applied to an apartment and was accepted",
                # "lives in gpd",
                "lives in permanent housing",
                "maintain permanent housing",
                "lives in house",
                "lives in apartment",
            ],

            "UNKNOWN": [
                "drives with his car",
                "park",
                "the streets",
                "streets",
                "discharged: home",
                "rental assistance",
                "housing assistance",
                "patient is eligible to be screened for HUD-VASH",
                "va supported housing",
                "she is at her sister's house",
                "gpd",
                "apartment",
                "house",
                "[] homeless",
            ]
        }

        failed_texts = []

        for (expected, texts) in text_classifications.items():
            for text in texts:
                doc = nlp(text)
                if doc._.document_classification != expected:
                    failed_texts.append((expected, doc._.document_classification, doc))
        assert failed_texts == []
                # assert doc._.document_classification == expected, doc

    def test_template_parsing(self):
        """Test that semi-structured templates can be correctly parsed."""
        text_classifications = {
            "UNSTABLY_HOUSED":
                [
                    "Where are you currently living? The Salvation Army",

                ],
            "STABLY_HOUSED": [
                "Where are you currently living? Stable housing",
            ],
            "UNKNOWN": [
                "Where are you currently living?",
            ]
        }

        for (classification, texts) in text_classifications.items():
            for text in texts:
                doc = nlp(text)
                assert doc._.document_classification == classification, doc

    def test_family_friends(self):
        """Need to differentiate between 'living with family/friends' (stable) and 'staying with' (unstable)"""
        phrases = [
            "mother",
            "brother",
            "father",
            "sister",
            "aunt",
            "uncle",
            "friend",
            "buddy",
        ]

        verbs = {
            "STABLY_HOUSED": [
                "lives with",
                # "staying with"
            ],
            "UNSTABLY_HOUSED": [
                "staying with",
                "crashing with",
            ]
        }

        failed_texts = []

        for expected, verbs in verbs.items():
            for verb in verbs:
                for noun in phrases:
                    text = f"{verb} {noun}"
                    doc = nlp(text)
                    if doc._.document_classification != expected:
                        failed_texts.append((expected, doc._.document_classification, doc))
        assert failed_texts == []

    def test_classification_algorithm(self):
        """Test sequential examples following the document classification algorithm
        presented in the paper. Some of these examples won't really be correct,
        but follow the general logic we want to follow."""
        examples = [
            # Step 1: structured template
            (
                "Where are you currently living? Stable housing",
                "STABLY_HOUSED"
            ),
            (
                "Where are you currently living? Stable housing.\n\nHe is homeless.",
                "STABLY_HOUSED"
            ),
            (
                "Where are you currently living? Homeless",
                "UNSTABLY_HOUSED"
            ),
            (
                "Where are you currently living? Literally Homeless.\n\nHe is homeless.",
                "UNSTABLY_HOUSED"
            ),
            (
                "Where are you currently living?",
                "UNKNOWN"
            ),
            # Step 2: Evidence of housing
            (
                "He is stably housed.",
                "STABLY_HOUSED"
            ),
            (
                "He is stably housed. He is homeless.",
                "STABLY_HOUSED"
            ),
            (
                "He is stably housed. He is looking for an apartment.",
                "STABLY_HOUSED"
            ),
            # Step 3: Evidence of unstable housing
            (
                "He is homeless.",
                "UNSTABLY_HOUSED"
            ),
            (
                "He is homeless. He is not homeless.",
                "UNSTABLY_HOUSED"
            ),
            # Test each of the classes
            (
                "He stayed at the Salvation Army.",
                "UNSTABLY_HOUSED",
            ),
            (
                "He crashed at his friend's house.",
                "UNSTABLY_HOUSED",
            ),
            (
                "He slept on the streets.",
                "UNSTABLY_HOUSED",
            ),
            # Step 4: Negated homelessness
            (
                "He is not homeless.",
                "STABLY_HOUSED"
            ),
            (
                "He is looking for an apartment. He is not homeless.",
                "STABLY_HOUSED"
            ),
            # Step 5: Hypothetical housing
            (
                "He is looking for an apartment.",
                "UNSTABLY_HOUSED"
            ),
            # Step 6: No information
            (
                "Nothing to see here.",
                "UNKNOWN"
            ),



        ]
        failed = []
        for (text, label) in examples:
            doc = nlp(text)
            if doc._.document_classification != label:
                failed.append((text, label, doc._.document_classification))
        assert failed == []