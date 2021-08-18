from ..utils import build_nlp
from spacy.tokens import Span

from .helpers import find_ents, _test_label_text, _test_label_texts

import warnings
warnings.filterwarnings("ignore")

nlp = build_nlp()
postprocessor = nlp.get_pipe("postprocessor")

nlp2 = build_nlp()
nlp2.remove_pipe("postprocessor")

descr_rule_map = {rule.description: rule for rule in postprocessor.rules}

class TestConcepts:
    def test_housing_goals(self):
        """Check that the rule which allows 'housing' to be used as hypothetical goals works."""
        descr = "If the generic phrase 'housing' occurs in patient goals, allow it to be used as hypothetical housing"

        assert _test_label_text(nlp, "housing", "EVIDENCE_OF_HOUSING", None, attrs={"is_ignored": True}) == []
        rule = descr_rule_map[descr]
        texts = [
            "Goals: housing",
            "find housing",
            "obtain housing",
            "seek housing"
        ]
        failed = []
        for text in texts:
            if (_test_label_text(nlp2, text, "EVIDENCE_OF_HOUSING", None,
                             attrs={"is_ignored": True}) != []):
                failed.append(text)
            doc = nlp(text, disable=["postprocessor", "document_classifier"])
            try:
                ent = find_ents(doc, "EVIDENCE_OF_HOUSING", 1)[0]
            except IndexError:
                failed.append(text)
                continue

            if rule(ent, 0):
                if (_test_label_text(nlp, text, "EVIDENCE_OF_HOUSING", None, attrs={"is_ignored": False, "is_hypothetical": True}) != []
                     and nlp(text)._.document_classification != "UNSTABLY_HOUSED"):
                    failed.append(text)
            else:
                failed.append(text)
        assert failed == []

    def test_positive_housing(self):
        descr = "If the generic phrase 'housing' is preceded by 'found' or modified by 'positive housing', allow it to be used as evidence of housing."
        rule = descr_rule_map[descr]
        texts = [
            "found housing",
            "no issues with housing",
            "is able to afford housing",
            "denies any concerns with housing"
        ]
        failed = []
        for text in texts:

            if (_test_label_text(nlp2, text, "EVIDENCE_OF_HOUSING", None,
                             attrs={"is_ignored": True}) != []):
                failed.append(text); continue

            doc = nlp(text, disable=["postprocessor", "document_classifier"])
            try:
                ent = find_ents(doc, "EVIDENCE_OF_HOUSING", 1)[0]
            except IndexError:
                failed.append(text)
                continue

            if rule(ent, 0):
                if (_test_label_text(nlp, text, "EVIDENCE_OF_HOUSING", None,
                                 attrs={"is_ignored": False, "is_asserted": True}) != []
                        or nlp(text)._.document_classification != "STABLY_HOUSED"
                ):
                    failed.append(text)

            else:
                failed.append(text)
        assert failed == []

    def test_found_home(self):
        descr = "Require a modifier for the exact phrase 'home'"
        rule = descr_rule_map[descr]
        _test_label_text(nlp, "home", "EVIDENCE_OF_HOUSING", None, attrs={"is_ignored": True})
        texts = [
            "found a home",
            "got furniture for home",
            "is able to afford a home",
        ]
        failed = []

        for text in texts:
            doc = nlp(text, disable=["postprocessor", "document_classifier"])

            try:
                ent = find_ents(doc, "EVIDENCE_OF_HOUSING", 1)[0]
                assert ent._.is_ignored is True
            except IndexError:
                failed.append(text)
                continue

            if rule(ent, 0):
                if (_test_label_text(nlp, text, "EVIDENCE_OF_HOUSING", None,
                                 attrs={"is_ignored": False, "is_asserted": True}) != []
                        or nlp(text)._.document_classification != "STABLY_HOUSED"
                ):
                    failed.append(text)
            else:
                failed.append(text)
        assert failed == []

    def test_negated_stable_housing(self):
        descr = "If a patient 'does not have stable housing', count that as evidence of homelessness"
        rule = descr_rule_map[descr]
        # _test_label_text(nlp, "home", "EVIDENCE_OF_HOUSING", None, attrs={"is_ignored": True})
        texts = [
            "she does not have stable housing",
            "has no stable housing",
        ]
        failed = []

        for text in texts:
            doc = nlp(text, disable=["postprocessor", "document_classifier"])
            try:
                ent = find_ents(doc, "EVIDENCE_OF_HOUSING", 1)[0]
            except IndexError:
                failed.append(text)
                continue
            if ent._.is_negated is False:
                failed.append(text); continue
            assert ent._.is_negated is True

            if rule(ent, 0):
               if (_test_label_text(nlp, text, "EVIDENCE_OF_HOMELESSNESS", None,
                                 attrs={"is_negated": False}) != []
                or nlp(text)._.document_classification != "UNSTABLY_HOUSED"
               ):
                    failed.append(text)
            else:
                failed.append(text)
        assert failed == []

    def test_ignore_housing_situation(self):
        descr = ("Ignore entities overlapping with 'housing situation'")
        rule = descr_rule_map[descr]
        # _test_label_text(nlp, "home", "EVIDENCE_OF_HOUSING", None, attrs={"is_ignored": True})
        text = "his housing situation"
        doc = nlp.tokenizer(text)
        failed = []

        ent = Span(doc, 0, 2, "EVIDENCE_OF_HOUSING")
        doc.ents += (ent,)

        if rule(ent, 0):
            # Now check that the entity is ignored again
            if ent._.is_ignored is False:
                failed.append(text)
        else:
            failed.append(text)
        assert failed == []

    def test_housing_options_hypothetical(self):
        descr = "If housing is being discussed in the same sentence as 'housing options', the housing should be hypothetical."
        rule = descr_rule_map[descr]
        text = "among his housing options are an apartment"
        doc = nlp(text, disable=["postprocessor"])
        assert doc._.document_classification != "UNSTABLY_HOUSED"
        ent = find_ents(doc, "EVIDENCE_OF_HOUSING", 2)[1]
        assert ent.text.lower() == "apartment"
        assert ent._.is_hypothetical is False
        rule(ent, 1)
        assert ent._.is_hypothetical is True
        doc = nlp(text)
        assert doc._.document_classification == "UNSTABLY_HOUSED"

    def test_rental_assistance(self):
        descr = "Consider 'rental assistance' to be 'evidence of housing' only if it is being received"
        rule = descr_rule_map[descr]
        doc = nlp("he receives rental assistance", disable=["postprocessor"])
        assert doc._.document_classification == "STABLY_HOUSED"
        doc = nlp("rental assistance", disable=["postprocessor", "document_classifier"])
        try:
            ent = doc.ents[0]
        except IndexError:
            raise IndexError("No entity found")
        assert ent._.is_ignored is False
        assert rule(ent, 0)
        assert ent._.is_ignored is True

    def test_housing_needs(self):
        descr = "If evidence of housing occurs in the goals section, set to hypothetical"
        rule = descr_rule_map[descr]
        doc = nlp("Patient Needs: including housing", disable=["postprocessor"])
        ent = find_ents(doc, "EVIDENCE_OF_HOUSING")[0]
        assert ent._.is_hypothetical is False
        assert ent._.section_category == "patient_needs"
        assert rule(ent, 0)
        assert ent._.is_hypothetical

        doc = nlp("Patient Needs: maintain housing", disable=["postprocessor"])
        ent = find_ents(doc, "EVIDENCE_OF_HOUSING")[0]
        assert ent._.is_hypothetical is False
        assert ent._.section_category == "patient_needs"
        assert not rule(ent, 0)
        assert ent._.is_hypothetical is False

    def test_housing_goals_maintain(self):
        descr = "If evidence of housing occurs in the goals section, change to not to hypothetical'"
        rule = descr_rule_map[descr]
        doc = nlp("Patient Goals: maintain housing", disable=["postprocessor"])
        ent = find_ents(doc, "EVIDENCE_OF_HOUSING")[0]
        assert ent._.is_hypothetical is True
        assert ent._.section_category == "patient_goals"
        assert rule(ent, 0)
        assert ent._.is_hypothetical is False

    def test_current_historical(self):
        description = "If a historical entity is modified by 'CURRENT', set 'is_historical' to False"
        rule = descr_rule_map[description]
        text = "Problem: currently homeless"
        doc = nlp(text, disable=["postprocessor"])
        ent = doc.ents[0]
        ent._.is_historical = True
        assert ent.text == "homeless"
        assert ent._.is_historical is True
        assert rule(ent, 0)
        assert ent._.is_historical is False

    def test_screen_temp_housing(self):
        desc = "If a patient is being screened for temporary housing, ignore it."
        rule = descr_rule_map[desc]

        text = "patient is eligible to be screened for shelter"
        doc = nlp(text, disable=["postprocessor", "document_classifier"])
        ent = doc.ents[0]
        assert ent.text == "shelter"
        assert ent.label_ == "TEMPORARY_HOUSING"
        assert ent._.is_ignored is False
        assert rule(ent, 0)
        assert ent._.is_ignored is True

    def test_paid_rent(self):
        desc = ("Only allow 'rent' or 'deposit' to be evidence of housing if it is modified by a phrase like 'paid' "
                    "or if it is 'my rent'")
        rule = descr_rule_map[desc]
        terms = ["rent", "security deposit"]
        for term in terms:
            doc = nlp(term, disable=["postprocessor", "document_classifier"])
            assert len(doc.ents) == 1
            ent = doc.ents[0]
            assert ent._.is_ignored is False
            assert rule(ent, 0)
            assert ent._.is_ignored is True

            doc = nlp(f"paid her {term}", disable=["postprocessor", "document_classifier"])
            ent = doc.ents[0]
            assert ent._.is_ignored is False
            assert not rule(ent, 0)
            assert ent._.is_ignored is False

    def test_homeless_location(self):
        desc = ("For certain words like 'car' or 'park' which are not necessarily related to homelessness, "
                    "only count as homelessness if they are modified by 'lives in'.")
        rule = descr_rule_map[desc]
        terms = ["car", "vehicle", "park", "woods", "the streets"]
        for term in terms:
            doc = nlp(term, disable=["postprocessor", "document_classifier"])
            assert len(doc.ents) == 1
            ent = doc.ents[0]
            assert ent.label_ == "EVIDENCE_OF_HOMELESSNESS"
            assert ent._.is_ignored is False
            assert rule(ent, 0)
            assert len(doc.ents) == 0

            for modifier in ["lives in", "Housing Status:"]:
                doc = nlp(f"{modifier} {term}", disable=["postprocessor", "document_classifier"])
                assert len(doc.ents)
                ent = doc.ents[-1]
                assert term in ent.text
                assert ent._.is_ignored is False
                assert not rule(ent, 0)
                assert len(doc.ents)

    def test_open_house(self):
        desc = "If a sentence contains 'open house', consider housing to be 'hypothetical'"
        text = "stable housing open house"
        rule = descr_rule_map[desc]
        doc = nlp(text, disable=["postprocessor", "document_classifier"])
        ent = doc.ents[0]
        assert ent.label_ == "EVIDENCE_OF_HOUSING"
        assert ent._.is_hypothetical is False
        assert rule(ent, 0)
        assert ent._.is_hypothetical is True

    def test_family_coreference(self):
        desc = "Avoid phrases like 'his house' which are referring to a friend or family member."
        rule = descr_rule_map[desc]
        text = "his uncle let him stay at his house"
        doc = nlp(text, disable=["postprocessor", "document_classifier"])
        ent = find_ents(doc, "EVIDENCE_OF_HOUSING")[0]
        assert ent._.is_ignored is False
        assert rule(ent, 0)
        assert ent._.is_ignored is True

        text = "his house"
        doc = nlp(text, disable=["postprocessor", "document_classifier"])
        ent = find_ents(doc, "EVIDENCE_OF_HOUSING")[0]
        assert ent._.is_ignored is False
        assert not rule(ent, 0)

    def test_live_family(self):
        desc = ("If a mention of staying with family/friends does not have 'stay' in the sentence, ignore it since it "
                    "might be permanent housing.")
        rule = descr_rule_map[desc]
        text = "she is at her sister's house"
        doc = nlp(text, disable=["postprocessor", "document_classifier"])
        ent = find_ents(doc, "DOUBLING_UP")[0]
        assert ent._.is_ignored is False
        assert rule(ent, 0)
        assert ent._.is_ignored is True

        text = "she is staying at her sister's house"
        doc = nlp(text, disable=["postprocessor", "document_classifier"])
        ent = find_ents(doc, "DOUBLING_UP")[0]
        assert ent._.is_ignored is False
        assert not rule(ent, 0)

    def test_home_visit_temp_housing(self):
        desc = "Disambiguate 'home visit' as referring to temporary housing."
        rule = descr_rule_map[desc]
        text = "I met her at the shelter to do a home visit."
        doc = nlp(text, disable=["postprocessor", "document_classifier"])
        ent = find_ents(doc, "EVIDENCE_OF_HOUSING")[0]
        assert ent.text == "home visit"
        ent2 = find_ents(doc, "TEMPORARY_HOUSING")[0]
        assert "shelter" in ent2.text


        assert ent._.is_ignored is False
        assert rule(ent, 0)
        assert ent._.is_ignored is True

        text = "I met her to do a home visit."
        doc = nlp(text, disable=["postprocessor", "document_classifier"])
        ent = find_ents(doc, "EVIDENCE_OF_HOUSING")[0]
        assert ent._.is_ignored is False
        assert not rule(ent, 0)

    def test_accepted_to_apartment(self):
        desc = ("If patient has applied to an apartment and been accepted, "
                "change is_hypothetical to False.")
        rule = descr_rule_map[desc]
        text = "He applied to an apartment and was accepted"
        doc = nlp(text, disable=["postprocessor", "document_classifier"])
        ent = find_ents(doc, "EVIDENCE_OF_HOUSING")[0]
        assert ent._.is_hypothetical is True
        assert rule(ent, 0)
        assert ent._.is_hypothetical is False

        text = "He applied to an apartment"
        doc = nlp(text, disable=["postprocessor", "document_classifier"])
        ent = find_ents(doc, "EVIDENCE_OF_HOUSING")[0]
        assert ent._.is_hypothetical is True
        assert not rule(ent, 0)

    def test_permanent_housing(self):
        desc = ("'Permanent housing' is too vague of a term, so require it be modified by "
                "'resides in' or preceded by 'maintain'")
        rule = descr_rule_map[desc]
        texts = ["lives in permanent housing", "maintain permanent housing", "apply for permanent housing", ]
        for text in texts:
            doc = nlp(text, disable=["postprocessor", "document_classifier"])
            ent = find_ents(doc, "EVIDENCE_OF_HOUSING")[0]
            assert ent._.is_ignored is False
            assert not rule(ent, 0)

        texts = ["permanent housing", ]
        for text in texts:
            doc = nlp(text, disable=["postprocessor", "document_classifier"])
            ent = find_ents(doc, "EVIDENCE_OF_HOUSING")[0]
            assert ent._.is_ignored is False
            assert rule(ent, 0)
            assert ent._.is_ignored is True

    def test_house_apartment_constraints(self):
        desc = "Require a modifier for 'house' or 'apartment' to be considered housing"
        rule = descr_rule_map[desc]
        ent_terms = (
            "house",
            "apartment",
            "apartment complex",
            "apartment building",
            # "apt"
        )
        modifiers = [
            "apply to",
            "applied to",
            "visited",
            "available",
            "look at",
            "needs",
            "lives in",
            "accepted to",
            "maintain",
            "has a",
            "has an",
            "has",
            "his",
            "her",
            "his own",
            "no issues with", # positive housing
        ]
        failed = []
        for term in ent_terms:
            # First check that without a modifier it is ignored
            doc = nlp(term, disable=["postprocessor", "document_classifier"])

            try:
                ent = find_ents(doc, "EVIDENCE_OF_HOUSING")[0]
                assert ent._.is_ignored is False
                assert rule(ent, 0)
                assert ent._.is_ignored is True
            except Exception as e:
                # raise e
                failed.append(term)
                continue

            # Now test with each of the modifiers
            for modifier in modifiers:
                text = f"{modifier} {term} {modifier}" # crude - in case modifiers are forward or backward looking
                doc = nlp(text, disable=["postprocessor", "document_classifier"])
                try:
                    ent = find_ents(doc, "EVIDENCE_OF_HOUSING")[0]
                    assert ent._.is_ignored is False
                    assert not rule(ent, 0)
                    assert ent._.is_ignored is False
                except Exception as e:
                    # raise e
                    failed.append(text)
        assert failed == []

    def test_homelessness_diagnosis_section(self):
        desc = ("If the exact phrase 'homelessness' occurs in the 'Diagnoses' section, mark it as historical "
                    "since it's probably not an accurate diagnosis.")
        rule = descr_rule_map[desc]
        text = "Diagnosis: asdf asdf Homelessness"
        doc = nlp(text, disable=["postprocessor", "document_classifier"])
        ent = find_ents(doc, "EVIDENCE_OF_HOMELESSNESS")[0]
        assert ent._.section_category.upper() == "DIAGNOSIS"
        assert ent._.is_historical is False
        assert rule(ent, 0)
        assert ent._.is_historical is True

        text = "homelessness"
        doc = nlp(text, disable=["postprocessor", "document_classifier"])
        ent = find_ents(doc, "EVIDENCE_OF_HOMELESSNESS")[0]
        assert ent._.is_historical is False
        assert not rule(ent, 0)
