# from ..nlp_postprocessor import PostprocessingRule, PostprocessingPattern
# from ..nlp_postprocessor import postprocessing_functions as ssvf_postprocessing_functions
from medspacy.postprocess import PostprocessingRule, PostprocessingPattern
from src import constants
from src.nlp.resources import callbacks, postprocessing_functions

import re


# Functions
def is_ignored(ent):
    if ent._.is_ignored:
        return True
    for token in ent:
        if token._.ignore:
            return True
    return False

def set_attribute(ent, i, attribute, value):
    setattr(ent._, attribute, value)

def change_label_need_housing(ent, i):
    """If an 'EVIDENCE_OF_HOUSING' entity is modified by 'need', change the label
    to either 'RISK_OF_HOMELESSNESS' or 'EVIDENCE_OF_HOMELESSNESS'.
    If the text reads 'needs stable housing', the label will be set to 'RISK'.
    If the text reads 'needs housing', the label will be set to 'HOMELESSNESS'.
    """
    postprocessing_functions.set_label(ent, i, "EVIDENCE_OF_HOMELESSNESS")

def change_hypothetical_phrase_housing(ent, i):
    postprocessing_functions.set_ignored(ent, i, False)
    postprocessing_functions.set_hypothetical(ent, i, True)

def change_negated_stable_housing_to_homelessness(ent, i):
    postprocessing_functions.set_label(ent, i, "EVIDENCE_OF_HOMELESSNESS")
    postprocessing_functions.set_negated(ent, i, False)
    postprocessing_functions.set_ignored(ent, i, False)
    for token in ent:
        token._.ignore = False


rules = [

    PostprocessingRule(
        patterns=[
            PostprocessingPattern(lambda ent: ent.lower_ == "housing"),
            PostprocessingPattern(lambda ent: ent.label_ == "EVIDENCE_OF_HOUSING"),
            (
                PostprocessingPattern(postprocessing_functions.is_modified_by_category, condition_args=("HYPOTHETICAL",)),
                PostprocessingPattern(postprocessing_functions.is_modified_by_text, condition_args=(r"(goal|secure|await|obtain|find|worried|need)",)),
                PostprocessingPattern(lambda ent: ent._.section_category == "patient_goals"),
            ),
        ],
        action=change_hypothetical_phrase_housing,
        # action_args=("RISK_OF_HOMELESSNESS",),
        description="If the generic phrase 'housing' occurs in patient goals, allow it to be used as hypothetical housing"
    ),

    PostprocessingRule(
        patterns=[
            PostprocessingPattern(lambda ent: ent.lower_ == "housing"),
            PostprocessingPattern(lambda ent: ent.label_ == "EVIDENCE_OF_HOUSING"),
            (
                PostprocessingPattern(postprocessing_functions.is_preceded_by, condition_args=(r"found",2),),
                PostprocessingPattern(postprocessing_functions.is_modified_by_category, condition_args=("POSITIVE_HOUSING",)),
            ),
        ],
        action=postprocessing_functions.set_ignored,
        action_args=(False,),
        description="If the generic phrase 'housing' is preceded by 'found' or modified by 'positive housing', allow it to be used as evidence of housing."
    ),

    PostprocessingRule(
        patterns=[
            PostprocessingPattern(lambda ent: ent.lower_ == "home"),
            PostprocessingPattern(lambda ent: ent.label_ == "EVIDENCE_OF_HOUSING"),
            PostprocessingPattern(lambda ent: ent._.any_context_attributes is False),
            (
                PostprocessingPattern(lambda ent: ent._.window(2)._.contains(r"(furniture|furnish)")),

                PostprocessingPattern(postprocessing_functions.is_preceded_by, condition_args=(r"found", 2)),
                PostprocessingPattern(postprocessing_functions.is_modified_by_category,
                                          condition_args=("POSITIVE_HOUSING",)),
            )
        ],
        action=postprocessing_functions.set_ignored,
        action_args=(False,),
        description="Require a modifier for the exact phrase 'home'"
    ),

    PostprocessingRule(
        patterns=[
            PostprocessingPattern(lambda ent: ent.lower_ in ("stable housing", "housing")),
            PostprocessingPattern(lambda ent: ent._.is_negated is True),
            PostprocessingPattern(postprocessing_functions.is_modified_by_text,
                                  condition_args=([r"has no", "not have"], True)),
        ],
        action=change_negated_stable_housing_to_homelessness,
        description="If a patient 'does not have stable housing', count that as evidence of homelessness"
    ),

    PostprocessingRule(
        patterns=[
            PostprocessingPattern(lambda ent: ent.lower_.endswith("housing")),
            PostprocessingPattern(postprocessing_functions.is_followed_by, condition_args=(r"situation",)),
        ],
        action=postprocessing_functions.set_ignored,
        action_args=(True,),
        description="Ignore entities overlapping with 'housing situation'"
    ),

    PostprocessingRule(patterns=[
        PostprocessingPattern(lambda ent: ent.label_ == "EVIDENCE_OF_HOUSING"),
        PostprocessingPattern(lambda ent: postprocessing_functions.sentence_contains(ent, "housing options"))
        ], action=set_attribute,
        action_args=("is_hypothetical", True),
        description="If housing is being discussed in the same sentence as 'housing options', the housing should be hypothetical."
    ),

    PostprocessingRule(
        patterns=[
            PostprocessingPattern(lambda ent: ent._.contains(r"(rental|housing) assistance", regex=True, case_insensitive=True)),
            PostprocessingPattern(lambda ent: ent.label_ == "EVIDENCE_OF_HOUSING"),
            PostprocessingPattern(postprocessing_functions.is_preceded_by, condition_args=("receive", True), success_value=False),
        ],
        # action=postprocessing_functions.remove_ent,
        action=postprocessing_functions.set_ignored, action_args=(True,),
        description="Consider 'rental assistance' to be 'evidence of housing' only if it is being received"
    ),

    PostprocessingRule(patterns=[
        PostprocessingPattern(lambda ent: ent.label_ == "EVIDENCE_OF_HOUSING"),
        (
            PostprocessingPattern(lambda ent: postprocessing_functions.is_modified_by_text(ent, "need")),
            PostprocessingPattern(lambda ent: ent._.section_category == "patient_needs",),
         ),
        PostprocessingPattern(postprocessing_functions.is_preceded_by, condition_args=("maintain", 5), success_value=False),
        PostprocessingPattern(postprocessing_functions.span_contains, condition_args=("housing",)),
    ],
        action=postprocessing_functions.set_hypothetical, action_args=(True,),
        description="If evidence of housing is modified by 'need', change to 'EVIDENCE' or 'RISK_OF_HOMELESSNESS'"
    ),

    PostprocessingRule(
        patterns=[
            PostprocessingPattern(lambda ent: ent.label_ == "EVIDENCE_OF_HOUSING"),

            PostprocessingPattern(lambda ent: ent._.section_category in ("patient_goals", "patient_needs")),
            PostprocessingPattern(postprocessing_functions.is_preceded_by, condition_args=("maintain", 5), success_value=False),
            PostprocessingPattern(lambda ent: ent._.contains("resid|liv|maintain", regex=True, case_insensitive=True), success_value=False),
        ],
        # action=change_label_need_housing,
        action=postprocessing_functions.set_hypothetical,
        action_args=(True,),
        description="If evidence of housing occurs in the goals section, set to hypothetical"
    ),

    PostprocessingRule(
        patterns=[
            PostprocessingPattern(lambda ent: ent.label_ == "EVIDENCE_OF_HOUSING"),
            (
                PostprocessingPattern(lambda ent: ent._.section_category in ("patient_goals", "patient_needs")),
                PostprocessingPattern(postprocessing_functions.is_modified_by_text, condition_args=("goals|want",)),
            ),
            (
                PostprocessingPattern(postprocessing_functions.is_preceded_by, condition_args=("maintain", 5),
                                  success_value=True),
                PostprocessingPattern(lambda ent: ent._.contains("maintain", regex=True, case_insensitive=True),
                                  success_value=True)
            ),
        ],
        action=postprocessing_functions.set_hypothetical,
        action_args=(False,),
        description="If evidence of housing occurs in the goals section, change to not to hypothetical'"
    ),

    PostprocessingRule(patterns=[
        PostprocessingPattern(lambda ent: ent.label_ == "EVIDENCE_OF_HOUSING"),
        PostprocessingPattern(lambda ent: postprocessing_functions.is_modified_by_category(ent, "AT_RISK")),

    ],
        action_args=("RISK_OF_HOMELESSNESS",),
        action=postprocessing_functions.set_label,
        description="If evidence of housing is modified by 'AT_RISK', change to 'RISK_OF_HOMELESSNESS'"
    ),

    PostprocessingRule(
        patterns=[
            PostprocessingPattern(lambda ent: ent._.is_historical is True),
            PostprocessingPattern(lambda ent: postprocessing_functions.is_modified_by_category(ent, "CURRENT")),
            PostprocessingPattern(lambda ent: postprocessing_functions.is_modified_by_category(ent, "HISTORICAL"), success_value=False),
        ],
        action_args=(False,),
        action=postprocessing_functions.set_historical,
        description="If a historical entity is modified by 'CURRENT', set 'is_historical' to False"
    ),

    PostprocessingRule(
        patterns=[
            PostprocessingPattern(lambda ent: ent.label_ == "TEMPORARY_HOUSING"),
            PostprocessingPattern(postprocessing_functions.is_modified_by_text, condition_args=("screen",)),

        ],
        action=postprocessing_functions.set_ignored,
        action_args=(True,),
        description="If a patient is being screened for temporary housing, ignore it."
    ),

    PostprocessingRule(
        patterns=[
            PostprocessingPattern(postprocessing_functions.span_contains, condition_args=(r"\b(rent|deposit)\b",)),

            PostprocessingPattern(postprocessing_functions.is_preceded_by,condition_args=(r"my",), success_value=False),
            PostprocessingPattern(postprocessing_functions.is_modified_by_category, condition_args=(r"PAYMENT",), success_value=False),
            PostprocessingPattern(postprocessing_functions.is_preceded_by, condition_args=(r"(pay|paid)", 5), success_value=False),
            PostprocessingPattern(postprocessing_functions.span_contains, condition_args=(r"(current on|behind [io]n|paid)",), success_value=False),
                    ],
        action=postprocessing_functions.set_ignored,
        description="Only allow 'rent' or 'deposit' to be evidence of housing if it is modified by a phrase like 'paid' "
                    "or if it is 'my rent'",
    ),

    PostprocessingRule(
        patterns=[
            PostprocessingPattern(lambda ent:ent.label_ == "EVIDENCE_OF_HOMELESSNESS"),
            PostprocessingPattern(postprocessing_functions.span_contains, condition_args=(r"(car|vehicle|park|woods|street)",), success_value=True),

            PostprocessingPattern(postprocessing_functions.span_contains, condition_args=(r"(live|living)",), success_value=False),
            PostprocessingPattern(postprocessing_functions.is_modified_by_category, condition_args=(r"RESIDES_IN",), success_value=False),
            #
            # PostprocessingPattern(postprocessing_functions.sentence_contains, condition_args=("transport",)),
            PostprocessingPattern(lambda ent: ent._.section_category != "housing_status"),

        ],
        # action=postprocessing_functions.remove_ent,
        action=postprocessing_functions.remove_ent,
        description="For certain words like 'car' or 'park' which are not necessarily related to homelessness, "
                    "only count as homelessness if they are modified by 'lives in'."
    ),

    PostprocessingRule(
        patterns=[
            PostprocessingPattern(lambda ent: ent.label_ == "EVIDENCE_OF_HOUSING"),
            PostprocessingPattern(postprocessing_functions.sentence_contains, condition_args=("open house",)),
        ],
        action=postprocessing_functions.set_hypothetical,
        description="If a sentence contains 'open house', consider housing to be 'hypothetical'"
    ),

    PostprocessingRule(
        [
            PostprocessingPattern(lambda ent: ent.label_ == "EVIDENCE_OF_HOUSING"),
            PostprocessingPattern(postprocessing_functions.span_contains, condition_args=("house",)),
            (
                PostprocessingPattern(postprocessing_functions.is_preceded_by, condition_args=("(his|her)", 10)),
                PostprocessingPattern(postprocessing_functions.span_contains, condition_args=("(his|her)",)),
            ),
            PostprocessingPattern(callbacks.resolve_family_coreference, success_value=True)
        ],
        action=postprocessing_functions.set_ignored,
        description="Avoid phrases like 'his house' which are referring to a friend or family member."
    ),

    PostprocessingRule(
        [
            PostprocessingPattern(lambda ent: ent.label_ == "DOUBLING_UP"),
            PostprocessingPattern(postprocessing_functions.contains_concept_tag, condition_args=("FAMILY",)),
            PostprocessingPattern(postprocessing_functions.sentence_contains, condition_args=("stay|crash",), success_value=False),
        ],
        action=postprocessing_functions.set_ignored,
        description="If a mention of staying with family/friends does not have 'stay' in the sentence, ignore it since it "
                    "might be permanent housing."

    ),

    PostprocessingRule(
        [
            PostprocessingPattern(lambda ent: ent.label_ == "EVIDENCE_OF_HOUSING"),
            PostprocessingPattern(postprocessing_functions.span_contains, condition_args=("visit",)),
            PostprocessingPattern(postprocessing_functions.sentence_contains_ent_label, condition_args=("TEMPORARY_HOUSING",)),
        ],
        action=postprocessing_functions.set_ignored, action_args=(True,),
        # action=postprocessing_functions.remove_ent,
        description="Disambiguate 'home visit' as referring to temporary housing."
    ),


    PostprocessingRule(
        [
            PostprocessingPattern(postprocessing_functions.span_contains, condition_args=("(apartment|apt)",)),
            PostprocessingPattern(postprocessing_functions.is_modified_by_text, condition_args=("appl(y|ied)",)),
            PostprocessingPattern(postprocessing_functions.is_modified_by_category, condition_args=("ACCEPTED",)),
        ],
        action=postprocessing_functions.set_hypothetical, action_args=(False,),
        description="If patient has applied to an apartment and been accepted, change is_hypothetical to False."
    ),

    PostprocessingRule(
        [
            PostprocessingPattern(lambda ent: ent.label_ == "EVIDENCE_OF_HOUSING"),
            PostprocessingPattern(lambda ent: ent.lower_ == "permanent housing"),

            PostprocessingPattern(postprocessing_functions.is_modified_by_category, condition_args=("RESIDES_IN",), success_value=False),
            PostprocessingPattern(postprocessing_functions.is_preceded_by, condition_args=("maintain", 5), success_value=False),

            PostprocessingPattern(lambda ent:ent._.is_hypothetical is False),
        ],
        action=postprocessing_functions.set_ignored, action_args=(True,),
        description="'Permanent housing' is too vague of a term, so require it be modified by 'resides in' or preceded by 'maintain'"
    ),

    # This is the most challenging rule - causes lots of FNs but needed for lots of FPs
    PostprocessingRule(
        [
            PostprocessingPattern(lambda ent: ent.label_ == "EVIDENCE_OF_HOUSING"),
            PostprocessingPattern(lambda ent: ent.lower_ in ("house", "apartment", "apartment complex", "apartment building", "apt")),
            PostprocessingPattern(postprocessing_functions.is_modified_by_text,
                                  condition_args=(r"(apply|applied|visit|available|look)",),
                                  success_value=False),
            PostprocessingPattern(postprocessing_functions.is_modified_by_category, condition_args=("HYPOTHETICAL",),
                                  success_value=False),
            PostprocessingPattern(postprocessing_functions.is_modified_by_category, condition_args=("RESIDES_IN",),
                                  success_value=False),
            PostprocessingPattern(postprocessing_functions.is_modified_by_category, condition_args=("ACCEPTED",),
                                  success_value=False),
            PostprocessingPattern(postprocessing_functions.is_preceded_by, condition_args=("maintain", 5),
                                  success_value=False),
            PostprocessingPattern(postprocessing_functions.is_preceded_by, condition_args=(r"has ?(an|a)?", 3),
                                  success_value=False),
            PostprocessingPattern(lambda ent:ent._.window(5)._.contains(r"(his|her)( own)?"),
                                  success_value=False),
            # PostprocessingPattern(lambda ent:ent._.window(5, left=True, right=False)._.contains(r"transition")),
            PostprocessingPattern(postprocessing_functions.is_modified_by_category, condition_args=("POSITIVE_HOUSING",), success_value=False),
            # PostprocessingPattern(postprocessing_functions.is_preceded_by, condition_args=(["got"],3), success_value=False),
        ],
        action=postprocessing_functions.set_ignored, action_args=(True,),
        description="Require a modifier for 'house' or 'apartment' to be considered housing"
    ),

    PostprocessingRule(
        [
            PostprocessingPattern(lambda ent: ent.label_ == "EVIDENCE_OF_HOMELESSNESS"),
            PostprocessingPattern(lambda ent: ent.lower_ == "homelessness"),
            PostprocessingPattern(lambda ent: ent._.section_category is not None),
            PostprocessingPattern(lambda ent: ent._.section_category.upper() == "DIAGNOSIS"),
        ],
        action=postprocessing_functions.set_historical, action_args=(True,),
        description="If the exact phrase 'homelessness' occurs in the 'Diagnoses' section, mark it as historical "
                    "since it's probably not an accurate diagnosis."
    ),

]

