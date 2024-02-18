from medspacy.postprocess import postprocessing_functions
import re
"""This module contains callback functions to be used in spaCy's matcher classes."""

def get_next_non_ws_tokens(token, window=1):
    next_tokens = []
    for next_token in token.doc[token.i+1:]:
        if next_token.is_space is False:
            next_tokens.append(next_token)
        if len(next_tokens) == window:
            return next_tokens
    return next_tokens

def disambiguate_question_mark(matcher, doc, i, matches):
    """Sentences ending in a question mark are often templates which shouldn't be considered
    positive evidence. However, if it's followed by either a 'Yes' or a 'No', we may
    want to use it as either a positive modifier or a negation modifier.
    """
    match_id, start, end = matches[i]

    span = doc[start:end]
    next_span = get_next_non_ws_tokens(span[-1], 5)
    next_words = {token.text.lower() for token in next_span}

    yes_words = {"yes", "y"}
    no_words = {"no", "n"}
    if yes_words.intersection(next_words):
        # Check if both yes and no are in the span, in which case we don't want to do anything
        if no_words.intersection(next_words):
            return
        # Otherwise, we'll consider this to be positive by removing it
        # TODO: May want to add explicit positive modifiers
        matches.pop(i)
        return

def ignore_current_sentence(matcher, doc, i, matches):
    """Ignore the entire sentence of a match.
    """
    match_id, start, end = matches[i]
    sent = doc[start].sent
    for token in sent:
        token._.ignore = True

def ignore_next_sentence(matcher, doc, i, matches):
    """Ignore the entire next sentence following a match.
    """
    match_id, start, end = matches[i]
    sent = doc[start].sent
    next_sent = get_following_sent(sent)
    if next_sent is None:
        return
    for token in next_sent:
        token._.ignore = True

def visit_on_match(matcher, doc, i, matches):
    """The phrase 'Visit' can be used to visit a potential residence,
    but is more commonly used as 'Visit the veteran in his home', or 'home visit'.
    """
    match_id, start, end = matches[i]
    span = doc[start:end]
    if postprocessing_functions.is_preceded_by(span, r"home"):
        matches.pop(i)
        return
    if postprocessing_functions.is_followed_by(span, [r"veteran", r"his", r"her", "location"]):
        matches.pop(i)
        return

def preceded_by_was(matcher, doc, i, matches):
    match_id, start, end = matches[i]
    span = doc[start:end]
    if not postprocessing_functions.is_preceded_by(span, "was", window=5):
        matches.pop(i)
        return
def his_her_home(matcher, doc, i, matches):
    match_id, start, end = matches[i]
    span = doc[start:end]
    window = span._.window(5, right=False)
    # print("Here", len(matches))
    if not window._.contains(["veteran", "patient", "pt"], regex=False, case_insensitive=True):
        matches.pop(i)

def furnished_home(matcher, doc, i, matches):

    match_id, start, end = matches[i]
    span = doc[start:end]
    window = span._.window(5)
    # print("Here", len(matches))
    if not window._.contains(["furniture", "furnish"], case_insensitive=True):
        matches.pop(i)
        # print(len(matches))
        # print(doc[matches[i][1]:matches[i][2]])


# TODO: Eventually move question/answer functions into a separate module
def parse_question_response_next_word_homeless(matcher, doc, i, matches):
    parse_question_response_next_word(matcher, doc, i, matches, "EVIDENCE_OF_HOMELESSNESS")

def parse_question_response_next_word_housing(matcher, doc, i, matches):
    parse_question_response_next_word(matcher, doc, i, matches, "EVIDENCE_OF_HOUSING")

def parse_question_response_next_word(matcher, doc, i, matches, label="EVIDENCE_OF_HOMELESSNESS"):
    """Check if the answer  to a question is in a predetermined list
    of positive and negative responses. If there is a recognized
    response, add an entity with the appropriate attributes set.

    Example:
        "Is the veteran currently homeless? No" -> EVIDENCE_OF_HOMELESSNESS, is_experienced = False
    """
    _, start, end = matches[i]
    span = doc[start:end]
    next_token = get_following_token(span)
    if next_token is None:
        return
    positive_responses = ["yes", "y"]
    negative_responses = ["no", "n"]

    if next_token.text.lower() in positive_responses:
        add_ent(doc, next_token.i, next_token.i + 1, label)
    # elif next_token.text.lower() in negative_responses:
    #     add_ent(doc, next_token.i, next_token.i + 1, label, {"is_experienced": False,
    #                                                                               "ssvf_rule": None,  # TODO
    #                                                                               })

def parse_question_response_checkmark_right_yes(matcher, doc, i, matches):
    """Removes a match if a span is NOT followed by 'Yes [X]'
    Will return True for:
        Veteran Meets Homeless Criteria: Yes [X] No []
    Will return False for:
        Veteran Meets Homeless Criteria: Yes [] No []
    """
    match_id, start, end = matches[i]
    answer = parse_question_response_checkmark_right(doc[start:end])
    print(doc[start:end])
    print(answer)
    if answer == False:
        matches.pop(i)
    else:
        return

def parse_question_response_checkmark_right_not_yes(matcher, doc, i, matches):
    """Removes a match if a span is followed by 'Yes [X]' """
    match_id, start, end = matches[i]
    answer = parse_question_response_checkmark_right(doc[start:end])

    if answer == True:

        matches.pop(i)
    else:
        return


def parse_question_response_checkmark_right(span):
    """Returns True if the following span does not contain a positive
    answer in the form of: 'Yes [X]'"""

    start_token = span[0]
    next_newline = get_next_token_w_newline(start_token, max_scope=30)

    if next_newline is None or next_newline.i + 1 - span.end > 4:
        following_span = get_following_span(span, 4)
    else:
        scope_end = next_newline.i + 1
        following_span = span.doc[span.end:scope_end]
    if re.search(r"Yes \[[Xx]\]", following_span.text):
        return True
    else:
        return False

def parse_who_wil_vet_live_with(matcher, doc, i, matches):
    "Remove an 'EVIDENCE_OF_HOUSING' match if it is not followed by 'alone'."
    match_id, start, end = matches.pop(i)
    # Get the next non-whitespace
    while True:
        end += 1
        try:
            answer_token = doc[end-1]
        except IndexError:
            return
        if not answer_token.is_space:
            break


    if answer_token.text.lower() == "alone":
        matches.insert(i, (match_id, start, end))
    return

def add_ent(doc, start, end, label, attributes=None):
    from spacy.tokens.span import Span
    span = Span(doc, start, end, label)
    if attributes is not None:
        for (name, value) in attributes.items():
            setattr(span._, name, value)
    doc.ents += (span,)

def get_following_span(span, window=1):
    """Get the next span following a Span."""
    return span.doc[span.end:span.end+window]

def get_following_sent(span):
    """Get the next sentence following a Span."""
    try:
        return span.doc[span.end].sent
    except IndexError:
        return None

def get_following_token(span):
    """Get the next non-whitespace token following a Span."""
    doc = span.doc
    i = span.end
    while True:
        try:
            next_token = doc[i]
        except IndexError:
            return None
        if next_token.is_space:
            i += 1
        else:
            return next_token

# TODO: Move this to a postprocessing rule
def disambiguate_housing(matcher, doc, i, matches):
    """The phrase 'housing' is often used in too broad or hypothetical of a sense
    but it occasionally does mean a veteran's true housing. This function will
    remove a match if it is not found to pass tests checking whether it is a true
    housing mention.
    """
    match_id, start, end = matches[i]
    span = doc[start:end]
    # Check if words about keep housing are in the sentence
    preceding_sent = span.sent[:span.start]
    preceding_tokens = [token.text.lower() for token in preceding_sent]
    # for word in ["maintain", "keep", "sustain", "need", "find"]:
    for word in ["maintain", "keep", "sustain", "need", "find"]:
        if word in preceding_tokens:
            return


    matches.pop(i)

def disambiguate_question_mark(matcher, doc, i, matches):
    """Sentences ending in a question mark are often templates which shouldn't be considered
    positive evidence. However, if it's followed by either a 'Yes' or a 'No', we may
    want to use it as either a positive modifier or a negation modifier.
    """
    match_id, start, end = matches[i]

    span = doc[start:end]
    next_span = get_next_non_ws_tokens(span[-1], 5)
    next_words = {token.text.lower() for token in next_span}

    yes_words = {"yes", "y"}
    no_words = {"no", "n"}
    if yes_words.intersection(next_words):
        # Check if both yes and no are in the span, in which case we don't want to do anything
        if no_words.intersection(next_words):
            return
        # Otherwise, we'll consider this to be positive by removing it
        # TODO: May want to add explicit positive modifiers
        matches.pop(i)
        return

    # if no_words.intersection(next_words):
    #     # Consider this to be negation
    #     matches.pop(i)
    #     matches.insert(i, (doc.vocab.strings["NEGATED_EXISTENCE"], start, end))
    #     return


def get_next_non_ws_tokens(token, window=1):
    next_tokens = []
    for next_token in token.doc[token.i+1:]:
        if next_token.is_space is False:
            next_tokens.append(next_token)
        if len(next_tokens) == window:
            return next_tokens
    return next_tokens



def resolve_family_coreference(span):
    """See if a span containing a pronoun is preceded by a family member.
    IF it is not, remove the match.
    """
    sent = span.sent
    for token in span.doc[sent.start:span.start]:
        if token._.concept_tag == "FAMILY":
            return True
    return False

def resolve_family_coreference_true(matcher, doc, i, matches):
    """See if a span containing a pronoun is preceded by a family member.
    IF it is not, remove the match.
    """
    match_id, start, end = matches[i]
    span = doc[start:end]
    if not resolve_family_coreference(span):
        matches.pop(i)

def resolve_family_coreference_false(matcher, doc, i, matches):
    """See if a span containing a pronoun is preceded by a family member.
    IF it is, remove the match.
    """
    match_id, start, end = matches[i]
    span = doc[start:end]
    if resolve_family_coreference(span):
        matches.pop(i)


def contains_rent(matcher, doc, i, matches):
    match_id, start, end = matches[i]
    span = doc[start:end]

    rent_terms = ["rent", "mortgage"]
    sent = span.sent
    if not postprocessing_functions.sentence_contains(sent, rent_terms):
        matches.pop(i)
        return

def permanent_housing_program(matcher, doc, i, matches):
    """'Permanent housing' is sometimes used as a general term, not saying the pt actually has it."""
    match_id, start, end = matches[i]
    span = doc[start:end]

    terms = ["program"]
    sent = span.sent
    if postprocessing_functions.is_followed_by(sent, terms, 2):
        matches.pop(i)
        return

def followed_by_issues(matcher, doc, i, matches):
    """'does not have housing' should be considered unstable housing,
    but 'does not have housing issues' should not be.
    """
    match_id, start, end = matches[i]
    span = doc[start:end]

    terms = ["issues", "problems", "issue", "problem"]

    if postprocessing_functions.is_followed_by(span, terms, 2):
        matches.pop(i)
        return

def stay_in_homeless_location(matcher, doc, i, matches):
    """Extract certain mentions of homelessness such as 'vehicle' and 'park'
    only if they're preceded by phrases such as 'staying in' or 'sleeping in'."""
    match_id, start, end = matches[i]
    span = doc[start:end]
    preceding_start = max(span.sent.start-10, 0)
    preceding_span = doc[preceding_start:start]
    # print(span, preceding_span)
    if postprocessing_functions.span_contains(span, "[hm]otel"):
        return
    for token in preceding_span:
        # print(token, token._.concept_tag)
        if token._.concept_tag == "RESIDES":

            return
    matches.pop(i)

def questionnaire_0_match(matcher, doc, i, matches):
    """Matches a questinnaire answer starting with a lettered bullet and ending in 0, followed by a new line.
    If it matches, this will expand that match to include everything up to that new line. Otherwise, it will remove it.
    """
    match_id, start, end = matches.pop(i)
    start_token = doc[start]
    if not start_newline(start_token):
        return
    next_newline = get_next_token_w_newline(start_token, max_scope=15)
    if next_newline is None:
        return
    if "0" in next_newline.text:
        new_end = next_newline.i + 1
    elif "0" in doc[next_newline.i-1].text:
        new_end = next_newline.i
    else:
        return
    matches.insert(i, (match_id, start, new_end))

def blank_line_checkmark_match(matcher, doc, i, matches):
    """Matches a questinnaire answer starting with a lettered bullet and ending in 0, followed by a new line.
    If it matches, this will expand that match to include everything up to that new line. Otherwise, it will remove it.
    """
    match_id, start, end = matches.pop(i)
    start_token = doc[start]
    if not start_newline(start_token):
        return

    next_newline = get_next_token_w_newline(start_token, max_scope=30)

    if next_newline is None:
        return
    try:
        new_end = next_newline.i + 1
    except:
        return

    matches.insert(i, (match_id, start, new_end))

def start_newline(token):
    i = token.i
    if i == 0:
        return True

    while i != 0:
        preceding_token = token.doc[token.i - 1]
        # If it is a whitespace, check if it contains a newline
        # Otherwise, keep moving left until we hit a newline
        if preceding_token.is_space:
            if "\n" in preceding_token.text_with_ws or "\r" in preceding_token.text_with_ws:
                return True
        else:
            if preceding_token.text_with_ws.endswith("\n"):
                return True
            if preceding_token.text_with_ws.endswith("\r"):
                return True
            return False
        i -= 1
    return False


def get_next_token_w_newline(start_token, max_scope=None):
    j = 1
    while True:
        if max_scope is not None and j > max_scope:
            return None
        try:
            token = start_token.doc[start_token.i+j]
        except IndexError:
            return None
        if "\n" in token.text_with_ws:
            return token
        j += 1

def on_modifies_pay(target, modifier, span_between):
    """For the modifiers 'not pay' or 'late', check that valid target terms such as 'rent' or 'bill' are being modified."""
    for term in ["bill", "rent", "mortgage"]:
        if term in target.text.lower():
            return True
    return False

def on_modifies_housing_plan(target, modifier, span_between):
    """For the modifier 'not pay', check that valid target terms such as 'rent' or 'bill' are being modified."""
    if target.text.lower().endswith("housing"):
        return True
    return False

def has_chosen(target, modifier, span_between):
    "Only allow the phrase 'has chosen' to modify phrases like 'apartment'."
    if re.search("apartment|apt", target.text.lower()):
        return True
    return False

def contact_with(target, modifier, span_between):
    "Disambiguate phrases like 'made contact with apartment complex'"
    if not re.search(r"landlord|complex|manager", target.text.lower()):
        return False
    return True

def hopes_on_modifies(target, modifier, span_between):
    "Use hope as a hypothetical modifier, but avoid excluding phrases like 'hopes he likes his new apartment.'"
    if span_between._.contains("like|enjoy"):
        return False
    return True

def resides_in_on_modifies(target, modifier, span_between):
    """Be careful with the normalized phrase 'resides in' and do some additonal checks."""
    # print(target, modifier)
    if (modifier._.contains(r"stay(s|ed|ing)? in", case_insensitive=True)
            and target._.contains(r"(apartment|apt)", case_insensitive=True)):
        return False
    return True

