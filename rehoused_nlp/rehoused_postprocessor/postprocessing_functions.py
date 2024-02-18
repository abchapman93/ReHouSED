"""This module contains functions to be used both as action and condition functions
for postprocessing patterns.
"""
import re
# Condition functions

def is_negated(span):
    """Return True if a span is marked as negated by cycontext."""
    return span._.is_negated

def is_uncertain(span):
    """Return True if a span is marked as uncertain by cycontext."""
    return span._.is_uncertain

def is_historical(span):
    """Return True if a span is marked as historical by cycontext."""
    return span._.is_historical

def is_hypothetical(span):
    """Return True if a span is marked as hypothetical by cycontext."""
    return span._.is_hypothetical

def is_family(span):
    """Return True if a span is marked as family by cycontext."""
    return span._.is_family

def is_modified_by_category(span, category, regex=True):
    """Returns True if a span is modified by a cycontext TagObject
    modifier with a certain category. Case insensitive.
    """
    for modifier in span._.modifiers:

        modifier_category = modifier.category.upper()
        if text_contains(modifier_category, category, regex) is True:
            return True
    return False

def is_modified_by_text(span, target, regex=True):
    """Returns True if a span is modified by a cycontext TabObject
    modifier with a certain text.
    """
    for modifier in span._.modifiers:
        modifier_span = span.doc[modifier.modifier_span[0]:modifier.modifier_span[1]]
        if span_contains(modifier_span, target, regex):
            return True
    return False


    # if regex is True:
    #     import re
    #     for modifier in span._.modifiers:
    #         if re.search(text, modifier.span.text.lower(), re.IGNORECASE):
    #             return True
    #
    # else:
    #     for modifier in span._.modifiers:
    #         if modifier.span.text.upper() == text.upper():
    #             return True
    # return False

def is_preceded_by(ent, target, window=1, regex=True):
    """Check if an entity is preceded by a target word within a certain window.
    Case-insensitive.
    If any phrases in target are more than one token long, this may not capture it
    if window is smaller than the number of tokens.
    ent (Span):  A spaCy Span
    target (str or iterable): Either a single string or iterable of strings.
        If an iterable, will return True if any of the strings are in the window
        preceding ent.
    """
    start = max((0, ent.start-window))
    preceding_span = ent.doc[start: ent.start]
    return span_contains(preceding_span, target, regex)
    # preceding_string = " ".join([token.text.lower() for token in preceding_span])
    # preceding_string = preceding_span.text_with_ws
    #
    # if isinstance(target, str):
    #     return target.lower() in preceding_string
    # for string in target:
    #     if string.lower() in preceding_string:
    #         return True
    # return False


def is_followed_by(ent, target, window=1, regex=True):
    """Check if an entity is followed by a target word within a certain window.
    Case-insensitive.
    If any phrases in target are more than one token long, this may not capture it
    if window is smaller than the number of tokens.
    ent (Span):  A spaCy Span
    target (str or iterable): Either a single string or iterable of strings.
        If an iterable, will return True if any of the strings are in the window
        following ent.
    """
    following_span = ent.doc[ent.end: ent.end+window]
    return span_contains(following_span, target, regex)
    # following_string = " ".join([token.text.lower() for token in following_span])
    # if isinstance(target, str):
    #     return target.lower() in following_string
    # for string in target:
    #     if string.lower() in following_string:
    #         return True
    # return False

def span_contains(span, target, regex=True):
    text = span.text.lower()
    return text_contains(text, target, regex)

def text_contains(text, target, regex=True):
    if regex is True:
        func = lambda x: re.search(x, text.lower(), re.IGNORECASE) is not None
    else:
        func = lambda x: x.lower() in text.lower()

    if isinstance(target, str):
        return func(target)

    # If it's an iterable, check if any of the strings are in sent
    for string in target:
        # print(string)
        # print(func(string))
        # print()
        if func(string):
            return True
    return False

def ent_contains(ent, target, regex=True):
    """Check if an entity occurs in the same sentence as another span of text.
    ent (Span): A spaCy Span
    target (str or iterable): Either a single string or iterable of strings.
        If an iterable, will return True if any of the strings are a substring
        of ent.sent.
    Case insensitive.
    """
    return span_contains(ent, target, regex)


def sentence_contains(ent, target, regex=True):
    """Check if an entity occurs in the same sentence as another span of text.
    ent (Span): A spaCy Span
    target (str or iterable): Either a single string or iterable of strings.
        If an iterable, will return True if any of the strings are a substring
        of ent.sent.
    Case insensitive.
    """
    return span_contains(ent.sent, target, regex)

def sentence_contains_ent_label(ent, target_label):
    """Check if the sentence containing an ent also includes an entity with the target_label
    """
    ents = ent.sent.ents
    ent_labels = {ent.label_ for ent in ents}
    return target_label in ent_labels

# Action funcs

def remove_ent(ent, i):
    """Remove an entity at position [i] from doc.ents."""
    ent.doc.ents = ent.doc.ents[:i] + ent.doc.ents[i+1:]


def set_label(ent, i, label):
    """Create a copy of the entity with a new label."""
    from spacy.tokens import Span
    new_ent = Span(ent.doc, ent.start, ent.end, label=label)
    # Copy any additional attributes
    # NOTE: This may not be complete and should be used with caution
    for (attr, values) in ent._.__dict__["_extensions"].items():
        setattr(new_ent._, attr, values[0])
    new_ent._.modifiers = ent._.modifiers
    if len(ent.doc.ents) == 1:
        ent.doc.ents = (new_ent,)
    else:
        try:
            ent.doc.ents = ent.doc.ents[:i] + (new_ent,) + ent.doc.ents[i+1:]
        except ValueError: # Overlaps with another entity - debug later
            pass



def set_negated(ent, i, value=True):
    ent._.is_negated = value

def set_historical(ent, i, value=True):
    ent._.is_historical = value

def set_ignored(ent, i, value=True):
    ent._.is_ignored = value

def set_hypothetical(ent, i, value=True):
    ent._.is_hypothetical = value

def new_line_ends_with_zero(ent):
    text = ent.sent.text_with_ws
    if re.search("0\n", text):
        return True
    return False

def contains_concept_tag(span, tag):
    for token in span:
        if token._.concept_tag == tag:
            return True
    return False