# from ..nlp_postprocessor import PostprocessingRule, PostprocessingPattern
# from ..nlp_postprocessor import postprocessing_functions as ssvf_postprocessing_functions
from ..rehoused_postprocessor import PostprocessingRule, PostprocessingPattern, postprocessing_functions
from .. import constants
from ..resources import callbacks

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

def contains_concept_tag(ent, target):
    if isinstance(target, str):
        target = {target.lower()}
    else:
        target = {t.lower() for t in target}
    for token in ent:
        if token._.concept_tag.lower() in target:
            return True
    return False

def change_label_need_housing(ent, i):
    """If an 'EVIDENCE_OF_HOUSING' entity is modified by 'need', change the label
    to either 'RISK_OF_HOMELESSNESS' or 'EVIDENCE_OF_HOMELESSNESS'.
    If the text reads 'needs stable housing', the label will be set to 'RISK'.
    If the text reads 'needs housing', the label will be set to 'HOMELESSNESS'.
    """
    postprocessing_functions.set_label(ent, i, "EVIDENCE_OF_HOMELESSNESS")
    # if "stable" in ent.text.lower():
    #     postprocessing_functions.set_label(ent, i, "RISK_OF_HOMELESSNESS")
    # else:
    #     postprocessing_functions.set_label(ent, i, "EVIDENCE_OF_HOMELESSNESS")

def change_hypothetical_phrase_housing(ent, i):
    postprocessing_functions.set_ignored(ent, i, False)
    postprocessing_functions.set_hypothetical(ent, i, True)

def change_negated_stable_housing_to_homelessness(ent, i):
    postprocessing_functions.set_label(ent, i, "EVIDENCE_OF_HOMELESSNESS")
    postprocessing_functions.set_negated(ent, i, False)
    postprocessing_functions.set_ignored(ent, i, False)
    for token in ent:
        token._.ignore = False

# Rules
rules = [
    # PostprocessingRule(patterns=[
    #     PostprocessingPattern(condition=lambda ent: ent.label_ == "EVIDENCE_OF_HOMELESSNESS"),
    #     PostprocessingPattern(condition=lambda ent: postprocessing_functions.is_modified_by_category(ent, "DEFINITE_NEGATED_EXISTENCE")),
    #     ],
    #     action=postprocessing_functions.set_label,
    #     action_args=("EXIT_FROM_HOMELESSNESS",),
    #     name="negated_homelessness->exit_homelessness",
    #     description="If a mention of homelessness is explicitly negated, change the label to 'EXIT_FROM_HOMELESSNESS'. "
    #                 "This will only apply to a subset of negative modifiers: 'DEFINITE_NEGATED_EXISTENCE'."
    # ),

    # PostprocessingRule(
    #     patterns=[
    #         PostprocessingPattern(lambda ent: ent.text.lower() == "housing"),
    #         PostprocessingPattern(lambda ent: ent.label_ == "EVIDENCE_OF_HOUSING"),
    #         (
    #             PostprocessingPattern(postprocessing_functions.sentence_contains, condition_args=("axis iv|stressor",)),
    #             PostprocessingPattern(lambda ent: ent._.section_category == "patient_needs"),
    #         ),
    #     ],
    #     action=postprocessing_functions.set_label,
    #     action_args=("RISK_OF_HOMELESSNESS",),
    #     description="If the lone phrase 'housing' is preceded by 'stressors', change the label to 'RISK_OF_HOMELESSNESS'"
    # ),

    PostprocessingRule(
        patterns=[
            PostprocessingPattern(lambda ent: ent.text.lower() == "housing"),
            PostprocessingPattern(lambda ent: ent.label_ == "EVIDENCE_OF_HOUSING"),
            (
                PostprocessingPattern(postprocessing_functions.is_modified_by_category, category="HYPOTHETICAL"),
                PostprocessingPattern(postprocessing_functions.is_modified_by_text, target=r"(goal|secure|await|obtain|find|worried|need)",),
                PostprocessingPattern(lambda ent: ent._.section_category == "patient_goals"),
            ),
        ],
        action=change_hypothetical_phrase_housing,
        # action_args=("RISK_OF_HOMELESSNESS",),
        description="If the generic phrase 'housing' occurs in patient goals, allow it to be used as hypothetical housing"
    ),

    PostprocessingRule(
        patterns=[
            PostprocessingPattern(lambda ent: ent.text.lower() == "housing"),
            PostprocessingPattern(lambda ent: ent.label_ == "EVIDENCE_OF_HOUSING"),
            (
                PostprocessingPattern(postprocessing_functions.is_preceded_by, target=r"found", window=2,),
                PostprocessingPattern(postprocessing_functions.is_modified_by_category, category="POSITIVE_HOUSING",),
                # PostprocessingPattern(postprocessing_functions.is_modified_by_text, condition_args=(["has no", "not have"],)),
            ),
        ],
        action=postprocessing_functions.set_ignored,
        value=False,
        description="If the generic phrase 'housing' is preceded by 'found' or modified by 'positive housing', allow it to be used as evidence of housing."
    ),

    PostprocessingRule(
        patterns=[
            PostprocessingPattern(lambda ent: ent.text.lower() == "home"),
            PostprocessingPattern(lambda ent: ent.label_ == "EVIDENCE_OF_HOUSING"),
            PostprocessingPattern(lambda ent: ent._.any_context_attributes is False),
            (
                PostprocessingPattern(lambda ent: ent._.window(2)._.contains(r"(furniture|furnish)")),

                PostprocessingPattern(postprocessing_functions.is_preceded_by, target=r"found", window=2),
                PostprocessingPattern(postprocessing_functions.is_modified_by_category,
                                          category="POSITIVE_HOUSING",),
            )

        ],
        action=postprocessing_functions.set_ignored,
        value=False,
        description="Require a modifier for the exact phrase 'home'"
    ),

    PostprocessingRule(
        patterns=[
            PostprocessingPattern(lambda ent: ent.text.lower() in ("stable housing", "housing")),
            PostprocessingPattern(lambda ent: ent._.is_negated is True),
            PostprocessingPattern(postprocessing_functions.is_modified_by_text,
                                  target=[r"has no", "not have"]),
        ],
        action=change_negated_stable_housing_to_homelessness,
        description="If a patient 'does not have stable housing', count that as evidence of homelessness"
    ),

    # PostprocessingRule(patterns=[
    #     PostprocessingPattern(lambda ent: ent._.is_ignored is False),
    #     PostprocessingPattern(condition=is_ignored)],
    #                    # action=postprocessing_functions.remove_ent,
    #                    action=postprocessing_functions.set_ignored, action_args=(True,),
    #                    name="remove_ents_w_ignored_tokens",
    #                    description="If any tokens in an entity have an ignore attribute set to True, "
    #                                "set the entity to be ignored",
    #                    ),

    # PostprocessingRule(
    #     patterns=[
    #         PostprocessingPattern(lambda ent: ent.text.lower() == "housing"),
    #         PostprocessingPattern(lambda ent: ent.label_ == "EVIDENCE_OF_HOUSING"),
    #         (
    #             PostprocessingPattern(postprocessing_functions.is_modified_by_text, condition_args=(r"(goal|secure)",)),
    #             PostprocessingPattern(lambda ent: ent._.section_category == "patient_goals"),
    #         ),
    #     ],
    #     action=postprocessing_functions.set_label,
    #     action_args=("RISK_OF_HOMELESSNESS",),
    #     description="If the generic phrase 'housing' occurs in patient goals, allow it to be used as hypothetical housing"
    # ),

    PostprocessingRule(
        patterns=[
            PostprocessingPattern(lambda ent: ent.text.lower().endswith("housing")),
            PostprocessingPattern(postprocessing_functions.is_followed_by, target=r"situation",),
        ],
        action=postprocessing_functions.set_ignored,
        value=True,
        description="Ignore entities overlapping with 'housing situation'"
    ),

    # PostprocessingRule(
    #     patterns=[
    #         PostprocessingPattern(lambda ent: ent.text.lower() == "housing"),
    #         PostprocessingPattern(lambda ent: ent.label_ == "EVIDENCE_OF_HOUSING"),
    #         PostprocessingPattern(lambda ent: ent._.section_category == "patient_strengths"),
    #     ],
    #     action=postprocessing_functions.set_ignored,
    #     action_args=(False,),
    #     description="If 'housing' appears in the patient strengths' section, count it as evidence of stable housing."
    # ),



    # PostprocessingRule(
    #     patterns=[
    #         PostprocessingPattern(lambda ent: ent.label_ in constants.PRIMARY_LABELS),
    #         PostprocessingPattern(lambda ent: ent._.is_negated is False),
    #         PostprocessingPattern(postprocessing_functions.is_followed_by,
    #                               condition_args=(":[\s]+Yes \[ \][\s]+ No \[X\]", 10, True)),
    #     ],
    #     action=postprocessing_functions.set_negated,
    #     action_args=(True,),
    #     description="A checkmarked 'No' is often cut off at the end of a line after a question."
    # ),



    # PostprocessingRule(
    #     patterns=[
    #         PostprocessingPattern(lambda ent: ent._.is_template)
    #     ],
    #     action=postprocessing_functions.set_label,
    #     action_args=("TEMPLATE_CANDIDATE",),
    #     description="Set entities which have been identified as being part of a template to 'TEMPLATE_CANDIDATE'"
    # ),

    # PostprocessingRule(patterns=[
    #     PostprocessingPattern(condition=lambda ent: ent.label_ == "EVIDENCE_OF_HOUSING"),
    #     PostprocessingPattern(condition=lambda ent: postprocessing_functions.sentence_contains(ent, "evicted"))
    #     ], action=postprocessing_functions.remove_ent,
    # name="remove_evicted_apt",
    # description="If 'evicted' is in a sentence, remove an evidence of housing entity."
    # ),

    PostprocessingRule(patterns=[
        PostprocessingPattern(lambda ent: ent.label_ == "EVIDENCE_OF_HOUSING"),
        PostprocessingPattern(lambda ent: postprocessing_functions.sentence_contains(ent, "housing options"))
        ], action=set_attribute,
        attribute="is_hypothetical", value=True,
        description="If housing is being discussed in the same sentence as 'housing options', the housing should be hypothetical."
    ),



    PostprocessingRule(
        patterns=[
            PostprocessingPattern(lambda ent: ent._.contains(r"(rental|housing) assistance", regex=True, case_insensitive=True)),
            PostprocessingPattern(lambda ent: ent.label_ == "EVIDENCE_OF_HOUSING"),
            PostprocessingPattern(postprocessing_functions.is_preceded_by, target="receive", success_value=False),
        ],
        # action=postprocessing_functions.remove_ent,
        action=postprocessing_functions.set_ignored, value=True,
        description="Consider 'rental assistance' to be 'evidence of housing' only if it is being received"
    ),

    PostprocessingRule(patterns=[
        PostprocessingPattern(lambda ent: ent.label_ == "EVIDENCE_OF_HOUSING"),
        (
            PostprocessingPattern(lambda ent: postprocessing_functions.is_modified_by_text(ent, "need")),
            PostprocessingPattern(lambda ent: ent._.section_category == "patient_needs",),
         ),
        PostprocessingPattern(postprocessing_functions.is_preceded_by, target="maintain", window=5, success_value=False),
        PostprocessingPattern(postprocessing_functions.span_contains, target="housing",),
    ],
        # action=change_label_need_housing,
        action=postprocessing_functions.set_hypothetical, value=True,
        description="If evidence of housing is modified by 'need', change to 'EVIDENCE' or 'RISK_OF_HOMELESSNESS'"
    ),

    PostprocessingRule(
        patterns=[
            PostprocessingPattern(lambda ent: ent.label_ == "EVIDENCE_OF_HOUSING"),

            PostprocessingPattern(lambda ent: ent._.section_category in ("patient_goals", "patient_needs")),
            PostprocessingPattern(postprocessing_functions.is_preceded_by, target="maintain", window=5, success_value=False),
            PostprocessingPattern(lambda ent: ent._.contains("resid|liv|maintain", regex=True, case_insensitive=True), success_value=False),
        ],
        # action=change_label_need_housing,
        action=postprocessing_functions.set_hypothetical,
        value=True,
        description="If evidence of housing occurs in the goals section, set to hypothetical"
    ),

    PostprocessingRule(
        patterns=[
            PostprocessingPattern(lambda ent: ent.label_ == "EVIDENCE_OF_HOUSING"),
            (
                PostprocessingPattern(lambda ent: ent._.section_category in ("patient_goals", "patient_needs")),
                PostprocessingPattern(postprocessing_functions.is_modified_by_text, target="goals|want",),
            ),
            (
                PostprocessingPattern(postprocessing_functions.is_preceded_by, target="maintain", window=5,
                                  success_value=True),
                PostprocessingPattern(lambda ent: ent._.contains("maintain", regex=True, case_insensitive=True),
                                  success_value=True)
            ),
        ],
        action=postprocessing_functions.set_hypothetical,
        value=False,
        description="If evidence of housing occurs in the goals section, change to not to hypothetical'"
    ),

    PostprocessingRule(patterns=[
        PostprocessingPattern(lambda ent: ent.label_ == "EVIDENCE_OF_HOUSING"),
        PostprocessingPattern(lambda ent: postprocessing_functions.is_modified_by_category(ent, "AT_RISK")),
        # PostprocessingPattern(lambda ent:not any([ent._.is_negated, ent._.is_ignored, ent._.is_historical, ent._.is_hypothetical])),
    ],
        label="RISK_OF_HOMELESSNESS",
        action=postprocessing_functions.set_label,
        description="If evidence of housing is modified by 'AT_RISK', change to 'RISK_OF_HOMELESSNESS'"
    ),

    PostprocessingRule(
        patterns=[
            PostprocessingPattern(lambda ent: ent._.is_historical is True),
            PostprocessingPattern(lambda ent: postprocessing_functions.is_modified_by_category(ent, "CURRENT")),
            PostprocessingPattern(lambda ent: postprocessing_functions.is_modified_by_category(ent, "HISTORICAL"), success_value=False),
        ],
        value=False,
        action=postprocessing_functions.set_historical,
        description="If a historical entity is modified by 'CURRENT', set 'is_historical' to False"
    ),

    PostprocessingRule(
        patterns=[
            PostprocessingPattern(lambda ent: ent.label_ == "HOMELESSNESS_HEALTHCARE_SERVICE"),
            PostprocessingPattern(postprocessing_functions.is_modified_by_text, target=r"(eligible for|accepted into|enrolled|apply|applied)"),
            PostprocessingPattern(postprocessing_functions.span_contains, target="hud[ \-/]+vash|gpd",),

        ],
        action=postprocessing_functions.set_label,
        label="EVIDENCE_OF_HOMELESSNESS",
        description="If a patient is eligible for or applying for HUD-VASH or GPD services, consider that to be evidence of homelessness."
    ),

    # This rule undoes the previous one
    PostprocessingRule(
        patterns=[
            PostprocessingPattern(lambda ent: ent.label_ == "EVIDENCE_OF_HOMELESSNESS"),
            (
                PostprocessingPattern(postprocessing_functions.is_modified_by_text, target="screen"),
                PostprocessingPattern(postprocessing_functions.is_preceded_by, target="screen", window=5),
            ),
            PostprocessingPattern(postprocessing_functions.span_contains, target="hud[ \-/]+vash",),

        ],
        action=postprocessing_functions.set_ignored,
        value=True,
        description="If a patient is being screened for HUD-VASH, ignore it"
    ),

    PostprocessingRule(
        patterns=[
            PostprocessingPattern(lambda ent: ent.label_ == "TEMPORARY_HOUSING"),
            PostprocessingPattern(postprocessing_functions.is_modified_by_text, target="screen",),

        ],
        action=postprocessing_functions.set_ignored,
        value=True,
        description="If a patient is being screened for temporary housing, ignore it."
    ),

    PostprocessingRule(
        patterns=[
            PostprocessingPattern(lambda ent: ent.label_ == "EVIDENCE_OF_HOMELESSNESS"),
            PostprocessingPattern(lambda ent:ent._.contains(r"homeless", case_insensitive=True)),
            PostprocessingPattern(lambda ent:ent._.window(5)._.contains(r"dent(al|ist)", case_insensitive=True)),

        ],
        action=postprocessing_functions.set_ignored,
        value=True,
        description="Ignore the word homelessness near 'dental', since it's often referring to a healthcare service"
    ),

    # TODO: Consider disabling this; 1/6/2024
    PostprocessingRule(
        patterns=[
            (
                PostprocessingPattern(lambda ent: ent.label_ == "VA_HOUSING"),
                # PostprocessingPattern(postprocessing_functions.span_contains, condition_args=("(hud|vash)",)),
            ),
            PostprocessingPattern(postprocessing_functions.is_modified_by_category, category="RESIDES_IN",),
        ],
        action=postprocessing_functions.set_label,
        label="EVIDENCE_OF_HOUSING",
        description="Only allow certain phrases such as 'VA Supported Housing' to count as evidence of housing"
                    " if it is modified by a phrase like 'resides in'"
    ),

    PostprocessingRule(
        patterns=[
            PostprocessingPattern(postprocessing_functions.span_contains, target=r"\b(rent|deposit)\b",),

            PostprocessingPattern(postprocessing_functions.is_preceded_by,target=r"my", success_value=False),
            PostprocessingPattern(postprocessing_functions.is_modified_by_category, category=r"PAYMENT", success_value=False),
            PostprocessingPattern(postprocessing_functions.is_preceded_by, target=r"(pay|paid)", window=5, success_value=False),
            PostprocessingPattern(postprocessing_functions.span_contains, target=r"(current on|behind [io]n|paid)", success_value=False),
                    ],
        action=postprocessing_functions.set_ignored,
        description="Only allow 'rent' or 'deposit' to be evidence of housing if it is modified by a phrase like 'paid' "
                    "or if it is 'my rent'",
    ),

    PostprocessingRule(
        patterns=[
            PostprocessingPattern(lambda ent:ent.label_ == "EVIDENCE_OF_HOMELESSNESS"),
            PostprocessingPattern(postprocessing_functions.span_contains, target=r"(car|vehicle|park|woods|street)", success_value=True),

            PostprocessingPattern(postprocessing_functions.span_contains, target=r"(live|living|sleep)", success_value=False),
            PostprocessingPattern(postprocessing_functions.is_modified_by_category, category=r"(RESIDES_IN|SLEEPS_IN)", success_value=False),
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
            PostprocessingPattern(lambda ent: ent._.section_category == "last_30_days_questionnaire"),
            PostprocessingPattern(postprocessing_functions.new_line_ends_with_zero),
        ],
        action=postprocessing_functions.set_ignored,
        value=True,
        description="In a questionnaire for the last 30 days, if the question ends with 0 ignore the entity"
    ),

    PostprocessingRule(
        patterns=[
            PostprocessingPattern(lambda ent: ent._.section_category == "referral_form"),
            PostprocessingPattern(postprocessing_functions.is_followed_by, target="None", window=2)
        ],
        action=postprocessing_functions.set_negated,
        value=True,
        description="In a templated form, if an entity is followed by 'None', negate it."
    ),

    PostprocessingRule(
        patterns=[
            PostprocessingPattern(lambda ent: ent.label_ == "EVIDENCE_OF_HOUSING"),
            PostprocessingPattern(postprocessing_functions.sentence_contains, target="open house",),
        ],
        action=postprocessing_functions.set_hypothetical,
        description="If a sentence contains 'open house', consider housing to be 'hypothetical'"
    ),

    PostprocessingRule(
        [
            PostprocessingPattern(lambda ent: ent.label_ == "EVIDENCE_OF_HOUSING"),
            PostprocessingPattern(postprocessing_functions.span_contains, target="house",),
            (
                PostprocessingPattern(postprocessing_functions.is_preceded_by, target="(his|her)", window=10),
                PostprocessingPattern(postprocessing_functions.span_contains, target="(his|her)"),
            ),
            PostprocessingPattern(callbacks.resolve_family_coreference, success_value=True)
        ],
        action=postprocessing_functions.set_ignored,
        description="Avoid phrases like 'his house' which are referring to a friend or family member."
    ),

    PostprocessingRule(
        [
            PostprocessingPattern(lambda ent: ent.label_ == "DOUBLING_UP"),
            PostprocessingPattern(contains_concept_tag, target="FAMILY",),
            PostprocessingPattern(postprocessing_functions.sentence_contains, target="stay|crash", success_value=False),
        ],
        action=postprocessing_functions.set_ignored,
        description="If a mention of staying with family/friends does not have 'stay' in the sentence, ignore it since it "
                    "might be permanent housing."

    ),
    PostprocessingRule(
        [
            PostprocessingPattern(lambda ent: ent.label_ == "EVIDENCE_OF_HOUSING"),
            PostprocessingPattern(postprocessing_functions.span_contains, target="visit",),
            PostprocessingPattern(postprocessing_functions.sentence_contains_ent_label, target_label="TEMPORARY_HOUSING",),
        ],
        action=postprocessing_functions.set_ignored, value=True,
        # action=postprocessing_functions.remove_ent,
        description="Disambiguate 'home visit' as referring to temporary housing."
    ),
    # PostprocessingRule(
    #     [
    #         PostprocessingPattern(postprocessing_functions.span_contains, condition_args=("apartment, room or house",)),
    #         PostprocessingPattern(postprocessing_functions.is_modified_by_category, condition_args=("NEGATED_EXISTENCE",), success_value=False),
    #         (
    #             PostprocessingPattern(postprocessing_functions.is_preceded_by, condition_args=("[[(]x[])]",5)),
    #             PostprocessingPattern(postprocessing_functions.is_followed_by, condition_args=(": yes",3)),
    #         ),
    #     ],
    #     action=postprocessing_functions.set_label, action_args=("EVIDENCE_OF_HOUSING",),
    #     description="If the template 'apartment room or house' is preceded by a filled in checkbox, "
    #                 "change to 'EVIDENCE_OF_HOUSING'"
    # ),

    PostprocessingRule(
        [
            PostprocessingPattern(postprocessing_functions.span_contains, target=r"(apartment|apt)",),
            PostprocessingPattern(postprocessing_functions.is_modified_by_text, target=r"appl(y|ied)",),
            PostprocessingPattern(postprocessing_functions.is_modified_by_category, category="ACCEPTED",),
        ],
        action=postprocessing_functions.set_hypothetical, value=False,
        description="If patient has applied to an apartment and been accepted, change is_hypothetical to False."
    ),

    PostprocessingRule(
        [
            PostprocessingPattern(lambda ent: ent.label_ == "EVIDENCE_OF_HOUSING"),
            PostprocessingPattern(postprocessing_functions.span_contains, target="(gpd|grant (& |and )?per diem)",),

            PostprocessingPattern(postprocessing_functions.is_modified_by_category, category="RESIDES_IN",
                                  success_value=False),
            PostprocessingPattern(postprocessing_functions.is_preceded_by, target="maintain", window=5,
                                  success_value=False),
            PostprocessingPattern(postprocessing_functions.is_modified_by_category, category="HYPOTHETICAL",
                                  success_value=False),
        ],
        action=postprocessing_functions.set_ignored, value=True,
        description="Require a modifier for 'gpd' or 'grant per diem' to be considered housing"
    ),

    PostprocessingRule(
        [
            PostprocessingPattern(lambda ent: ent.label_ == "EVIDENCE_OF_HOUSING"),
            PostprocessingPattern(lambda ent: ent.text.lower() == "permanent housing"),

            PostprocessingPattern(postprocessing_functions.is_modified_by_category, category="RESIDES_IN", success_value=False),
            PostprocessingPattern(postprocessing_functions.is_preceded_by, target="maintain", window=5, success_value=False),

            PostprocessingPattern(lambda ent:ent._.is_hypothetical is False),
        ],
        action=postprocessing_functions.set_ignored, value=True,
        description="'Permanent housing' is too vague of a term, so require it be modified by 'resides in' or preceded by 'maintain'"
    ),

    # This is the most challenging rule - causes lots of FNs but needed for lots of FPs
    PostprocessingRule(
        [
            PostprocessingPattern(lambda ent: ent.label_ == "EVIDENCE_OF_HOUSING"),
            PostprocessingPattern(lambda ent: ent.text.lower() in ("house", "apartment", "apartment complex", "apartment building", "apt")),
            PostprocessingPattern(postprocessing_functions.is_modified_by_text,
                                  target=r"(apply|applied|visit|available|look)",
                                  success_value=False),
            PostprocessingPattern(postprocessing_functions.is_modified_by_category, category="HYPOTHETICAL",
                                  success_value=False),
            PostprocessingPattern(postprocessing_functions.is_modified_by_category, category="RESIDES_IN",
                                  success_value=False),
            PostprocessingPattern(postprocessing_functions.is_modified_by_category, category="ACCEPTED",
                                  success_value=False),
            PostprocessingPattern(postprocessing_functions.is_preceded_by, target="maintain", window=5,
                                  success_value=False),
            PostprocessingPattern(postprocessing_functions.is_preceded_by, target=r"has ?(an|a)?", window=3,
                                  success_value=False),
            PostprocessingPattern(lambda ent:ent._.window(5)._.contains(r"(his|her)( own)?"),
                                  success_value=False),
            # PostprocessingPattern(lambda ent:ent._.window(5, left=True, right=False)._.contains(r"transition")),
            PostprocessingPattern(postprocessing_functions.is_modified_by_category, category="POSITIVE_HOUSING", success_value=False),
            # PostprocessingPattern(postprocessing_functions.is_preceded_by, condition_args=(["got"],3), success_value=False),
        ],
        action=postprocessing_functions.set_ignored, value=True,
        description="Require a modifier for 'house' or 'apartment' to be considered housing"
    ),

    PostprocessingRule(
        [
            PostprocessingPattern(lambda ent: ent.label_ in ("EVIDENCE_OF_HOUSING", "EVIDENCE_OF_HOMELESSNESS")),
            PostprocessingPattern(lambda ent:ent._.is_negated is False),
            PostprocessingPattern(postprocessing_functions.is_preceded_by, target="[]", window=3, regex=False),
        ],
        action=postprocessing_functions.set_ignored, value=True,
        description="Sometimes sentence splitting separates an empty checkmark from a list item"
    ),

    PostprocessingRule(
        [
            PostprocessingPattern(lambda ent: ent.label_ == "EVIDENCE_OF_HOMELESSNESS"),
            PostprocessingPattern(lambda ent: ent.text.lower() == "homelessness"),
            PostprocessingPattern(lambda ent: ent._.section_category is not None),
            PostprocessingPattern(lambda ent: ent._.section_category.upper() == "DIAGNOSIS"),
        ],
        action=postprocessing_functions.set_historical, value=True,
        description="If the exact phrase 'homelessness' occurs in the 'Diagnoses' section, mark it as historical "
                    "since it's probably not an accurate diagnosis."
    ),

    # TODO: come back to this
    # PostprocessingRule(
    #     [
    #         PostprocessingPattern(lambda ent:ent.label_ in ("EVIDENCE_OF_HOUSING",
    #                                                         # "EVIDENCE_OF_HOMELESSNESS"
    #                                                         )),
    #         PostprocessingPattern(postprocessing_functions.is_modified_by_category, condition_args=("LIST",)),
    #         PostprocessingPattern(lambda ent:ent.section_category not in ("past_medical_history", "assessment_plan", "diagnosis",
    #                                                                       "Assessment/Intake Form Question")),
    #     ],
    #     action=postprocessing_functions.set_ignored, action_args=(True,),
    #     description="Lists are problematic, so ignore instances of lists except for in certain secttions"
    # ),
    # PostprocessingRule(
    #     patterns=[
    #         PostprocessingPattern(lambda ent: ent.label_ in ["EVIDENCE_OF_HOUSING", "EVIDENCE_OF_HOMELESSNESS", "TEMPORARY_HOUSING"]),
    #         PostprocessingPattern
    #     ],
    # ),
]

