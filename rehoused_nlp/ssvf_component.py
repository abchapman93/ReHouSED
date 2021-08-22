from spacy.tokens import Doc
from collections import defaultdict

from . import constants

try:
    Doc.set_extension("ssvf_data", default=None)
except:
    pass

def set_document_classification(doc, value): doc._.ssvf_data["document_classification"] = value

try:
    Doc.set_extension("document_classification", getter=lambda doc:doc._.ssvf_data.get("document_classification"),
                      setter=set_document_classification, force=True)
except:
    pass


def set_is_classifier(ents):
    for ent in ents:
        ent._.is_classifier = True

class SSVFDocumentClassifier:
    name = "document_classifier"

    def __init__(self, debug=False):
        self.debug = debug

    def gather_ssvf_data(self, doc):
        doc._.ssvf_data = dict()
        for name in ("asserted_ents", "hypothetical_ents", "negated_ents"):
            doc._.ssvf_data[name] = defaultdict(set)
        doc._.ssvf_data["form_answer"] = self.parse_forms(doc)
        doc._.ssvf_data["housing_status_answer"] = self.parse_housing_status(doc)
        asserted_ents = doc._.ssvf_data["asserted_ents"]
        hypothetical_ents = doc._.ssvf_data["hypothetical_ents"]
        negated_ents = doc._.ssvf_data["negated_ents"]

        for ent in doc.ents:
            if ent.label_ in constants.PRIMARY_LABELS:
                if any([ent._.is_negated, ent._.is_hypothetical, ent._.is_historical, ent._.is_family, ent._.is_ignored]):
                    if ent._.is_ignored:
                        continue
                    if ent._.is_hypothetical:
                        hypothetical_ents[ent.label_].add(ent)
                    if ent._.is_negated:
                        negated_ents[ent.label_].add(ent)
                    continue
                asserted_ents[ent.label_].add(ent)

    def classify_doc(self, doc):
        """Binary classification logic as of 11/2. The gist of this logic is:
            - If there is a reliable form answer, use that
            - If there is an asserted evidence of housing -> Stably Housed
            - If there is a negated homelessness -> Stably Housed
            - If there is asserted evidence of homelessness/housing instability or hypothetical housing -> Unstably Housed
        """
        # ent_label_counts = defaultdict(set)
        # Start by looking for form answers
        form_answer = doc._.ssvf_data.get("form_answer")
        if form_answer is not None:
            if self.debug:
                print("Parsed template for answer:", form_answer)
            return form_answer

        housing_status_answer = doc._.ssvf_data.get("housing_status_answer")
        if housing_status_answer is not None:
            if self.debug:
                print("Parsed housing status for answer:", housing_status_answer)
            return housing_status_answer

        asserted_ents = doc._.ssvf_data["asserted_ents"]
        hypothetical_ents = doc._.ssvf_data["hypothetical_ents"]
        negated_ents = doc._.ssvf_data["negated_ents"]
        if self.debug:
            print(asserted_ents)

        # If there is evidence of housing, check if there's risk of homelessness
        # If there is, consider it unstable housing
        # Otherwise, return stable housing
        if asserted_ents.get("EVIDENCE_OF_HOUSING"):
            set_is_classifier(asserted_ents.get("EVIDENCE_OF_HOUSING"))
            if self.debug:
                print("Found evidence of housing:")
                print(asserted_ents["EVIDENCE_OF_HOUSING"])

            outcome = "STABLY_HOUSED"
        # If there's no evidence of housing, see if there is evidence of homelessness
        else:

            # Check if there's 'DOUBLING_UP', 'HOMELESS', or 'TEMPORARY_HOUSING',
            # We'll call that 'UNSTABLE'
            if sum([len(ents) for (label, ents) in asserted_ents.items() if
                    label in constants.BIN_UNSTABLE_OUTCOME_LABELS]):
                for label, ents in asserted_ents.items():
                    if label in constants.BIN_UNSTABLE_OUTCOME_LABELS:
                        set_is_classifier(ents)
                if self.debug:
                    print("Found unstable housing concept:")
                    print([(label, ents) for (label, ents) in asserted_ents.items() if
                           label in constants.BIN_UNSTABLE_OUTCOME_LABELS])
                outcome = "UNSTABLY_HOUSED"
            # If there is a negated evidence of homelessness, call it stable
            elif negated_ents.get("EVIDENCE_OF_HOMELESSNESS"):
                outcome = "STABLY_HOUSED"
                set_is_classifier(negated_ents.get("EVIDENCE_OF_HOMELESSNESS"))
                if self.debug:
                    print("Found negated evidence of homelessness")
                    print(negated_ents.get("EVIDENCE_OF_HOMELESSNESS"))
            # See if there is any hypothetical mention of housing
            elif hypothetical_ents.get("EVIDENCE_OF_HOUSING"):
                outcome = "UNSTABLY_HOUSED"
                set_is_classifier(hypothetical_ents.get("EVIDENCE_OF_HOUSING"))
                if self.debug:
                    print("Found hypothetical evidence of housing")
                    print(hypothetical_ents.get("EVIDENCE_OF_HOUSING"))
            # Any hypothetical mention of temporary housing
            elif hypothetical_ents.get("TEMPORARY_HOUSING"):
                outcome = "UNSTABLY_HOUSED"
                set_is_classifier(hypothetical_ents.get("TEMPORARY_HOUSING"))
                if self.debug:
                    print("Found hypothetical temporary housing")
                    print(hypothetical_ents.get("TEMPORARY_HOUSING"))
            # If there is a hypothetical mention of homelessness,
            # Call it stable
            elif hypothetical_ents.get("EVIDENCE_OF_HOMELESSNESS"):
                outcome = "STABLY_HOUSED"
                set_is_classifier(hypothetical_ents.get("EVIDENCE_OF_HOMELESSNESS"))
                if self.debug:
                    print("Found hypothetical evidence of homelessness")
                    print(hypothetical_ents.get("EVIDENCE_OF_HOMELESSNESS"))

            # If there's no othere information about their housing status but there is some sort of
            # risk of homelessness, return unstable
            # elif ent_label_counts.get("RISK_OF_HOMELESSNESS") and not negated_ents.get("EVIDENCE_OF_HOMELESSNESS"):

            elif asserted_ents.get("RISK_OF_HOMELESSNESS"):
                outcome = "UNSTABLY_HOUSED"
                set_is_classifier(asserted_ents.get("RISK_OF_HOMELESSNESS"))
                if self.debug:
                    print("Found 'RISK_OF_HOMELESSNESS':")
                    print(asserted_ents.get("RISK_OF_HOMELESSNESS"))
            # Otherwise, we don't have enough information to make a decision
            else:
                outcome = "UNKNOWN"
                if self.debug:
                    print("No relevant entities for document classification")

        return outcome

    def parse_forms(self, doc):
        """Before applying more generalized document classification,
        look for specific template question/answers which can give a clear, concise answer."""
        for ent in doc.ents:
            if ent._.section_category == "KNOWN_QUESTIONNAIRE":
                set_is_classifier([ent])
                if self.debug:
                    print("Found form answer:", ent._.section_title, ent, ent.label_)
                if ent.label_ == "EVIDENCE_OF_HOMELESSNESS":
                    return "UNSTABLY_HOUSED"
                if ent.label_ == "EVIDENCE_OF_HOUSING":
                    return "STABLY_HOUSED"
                if ent.label_ in ("TEMPORARY_HOUSING", "DOUBLING_UP"):
                    return "UNSTABLY_HOUSED"
                if ent.label_ == "RISK_OF_HOMELESSNESS":
                    return "UNSTABLY_HOUSED"

    def parse_housing_status(self, doc):
        """"""
        category = None
        housing_status_ents = set()
        for ent in doc.ents:
            if (ent._.section_category == "housing_status"
                and ent._.is_asserted
                    and ent.label_ in constants.PRIMARY_LABELS
            ):
                housing_status_ents.add(ent)
        housing_status_labels = {ent.label_ for ent in housing_status_ents}

        # Require only positive or negative housing classes - can't have both
        if "EVIDENCE_OF_HOUSING" in housing_status_labels and len(housing_status_labels) > 1:
            return None
        # print("Here:", housing_status_ents)
        # print("Here:", housing_status_labels)
        if len(housing_status_labels) == 1:
            for ent in housing_status_ents:
                if ent.label_ == "EVIDENCE_OF_HOMELESSNESS":
                    category = "UNSTABLY_HOUSED"
                elif ent.label_ == "EVIDENCE_OF_HOUSING":
                    category = "STABLY_HOUSED"
                if ent.label_ in ("TEMPORARY_HOUSING", "DOUBLING_UP"):
                    category = "UNSTABLY_HOUSED"
                # if ent.label_ == "RISK_OF_HOMELESSNESS":
                #     return "UNSTABLY_HOUSED"
            if category is not None and self.debug:
                print("Found housing status answer:", category, housing_status_ents)
        return category


    def is_answer(self, ent):
        import re
        for modifier in ent._.modifiers:
            if re.search("continues to (reside|live) in", modifier.span.lower_):
                return True
        return False

    def __call__(self, doc):
        self.gather_ssvf_data(doc)

        classification = self.classify_doc(doc)
        doc._.document_classification = classification
        return doc