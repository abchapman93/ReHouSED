from spacy.tokens import Span, Token, Doc
import dateutil

CONTEXT_ATTRS = {
        "NEGATED_EXISTENCE": {"is_negated": True},
        "HYPOTHETICAL": {"is_hypothetical": True},
        "AT_RISK": {"is_uncertain": True},
        "HISTORICAL": {"is_historical": True},
        "NOT_RELEVANT": {"is_ignored": True},
        "FAMILY": {"is_family": True},
    }

def set_extensions():
    from spacy.tokens import Span, Token, Doc

    Token.set_extension("concept_tag", default="", force=True)
    for (_, attr_dict) in CONTEXT_ATTRS.items():
        for (attr_name, attr_value) in attr_dict.items():
            Span.set_extension(attr_name, default=False, force=True)

    # Span.set_extension("is_experienced", default=True)
    Doc.set_extension("document_classification", default=None, force=True)
    Span.set_extension("date", getter=get_date)
    Span.set_extension("is_template", default=False)
    Span.set_extension("is_classifier", default=False)
    Span.set_extension("is_asserted", getter=lambda x: is_asserted(x), force=True)

def is_asserted(span):
    attrs = ['is_negated',
    'is_uncertain',
    'is_historical',
    'is_hypothetical',
    'is_family',
    'is_ignored',]
    for attr in attrs:
        if getattr(span._, attr):
            return False
    return True

Span.set_extension("is_asserted", getter=lambda x:is_asserted(x), force=True)

def build_nlp(model="en_core_web_sm", disable=None, add_target_rules=True, add_context_rules=True,
              use_context_window=False, max_scope=15):
    """Return a model with custom components for SSVF."""
    try:
        set_extensions()
    except ValueError:
        pass

    import spacy
    if disable is None:
        disable = ["ner"]
    if isinstance(model, str):
        nlp = spacy.load(model, disable=disable)
    else:
        nlp = model

    # Add a preprocessor
    from .resources.preprocess_rules import preprocess_rules
    from medspacy.preprocess import Preprocessor
    from .tokenizer import ssvf_tokenizer
    preprocessor = Preprocessor(ssvf_tokenizer(nlp))
    preprocessor.add(preprocess_rules)
    nlp.tokenizer = preprocessor

    # Concept tagger

    from medspacy.target_matcher import ConceptTagger, TargetRule
    from .resources import concept_tag_rules
    concept_tagger = ConceptTagger(nlp)
    concept_tagger.add(concept_tag_rules.rules)
    concept_tag_rules = []
    import os
    with open(os.path.join(os.path.abspath(__file__), "../resources/concept_tag_phrases.txt")) as f:
        for line in f.read().splitlines():
            phrase, label = line.split("\t")
            # print(phrase, label)
            concept_tag_rules.append(TargetRule(phrase, label))
    concept_tagger.add(concept_tag_rules)
    nlp.add_pipe(concept_tagger)

    # Add a target matcher
    from medspacy.target_matcher import TargetMatcher

    target_matcher = TargetMatcher(nlp)
    if add_target_rules:
        from .resources.ssvf_rules import ssvf_rules
        target_matcher.add(ssvf_rules.rules)
    nlp.add_pipe(target_matcher)

    # Add cycontext
    from medspacy.context import ConTextComponent
    context = ConTextComponent(nlp, rules=None, add_attrs=CONTEXT_ATTRS, remove_overlapping_modifiers=True,
                               use_context_window=use_context_window, max_scope=max_scope)
    if add_context_rules:
        from src.nlp.resources.context_rules import context_rules
        context.add(context_rules)
    nlp.add_pipe(context)



    # Add a sectionizer
    from medspacy.section_detection import Sectionizer
    from pathlib import Path
    # SECTION_RULES_FILEPATH = os.path.join(
    #     Path(__file__).resolve().parents[1], "resources", "section_patterns.jsonl"
    # )
    SECTION_RULES_FILEPATH = ""
    # print(SECTION_RULES_FILEPATH)
    # from src.nlp.resources import section_rules
    from medspacy.section_detection import section_patterns_to_rules
    section_rules = []
    import json
    with open(SECTION_RULES_FILEPATH) as f:
        for line in f:
            section_rules.append(json.loads(line))
    section_attrs = {
        "problem_list": {"is_historical": True},
        "past_medical_history": {"is_historical": True},
        "patient_education": {"is_ignored": True},
    }
    sectionizer = Sectionizer(nlp, rules=None, add_attrs=section_attrs, max_scope=300)
    sectionizer.add(section_patterns_to_rules(section_rules))

    from .resources.section_rules import section_rules
    sectionizer.add(section_rules)

    nlp.add_pipe(sectionizer)

    # Add a PostProcessor
    from medspacy.postprocess import Postprocessor
    from .resources import postprocess_rules
    postprocessor = Postprocessor()
    postprocessor.add(postprocess_rules.rules)

    nlp.add_pipe(postprocessor)

    from src.nlp.ssvf_component import SSVFDocumentClassifier

    nlp.add_pipe(SSVFDocumentClassifier())

    return nlp

def prune_overlapping_matches(matches, strategy="longest"):
    if strategy != "longest":
        raise NotImplementedError()

    # Make a copy and sort
    unpruned = sorted(matches, key=lambda x: (x[1], x[2]))
    pruned = []
    num_matches = len(matches)
    if num_matches == 0:
        return matches
    curr_match = unpruned.pop(0)

    while True:
        if len(unpruned) == 0:
            pruned.append(curr_match)
            break
        next_match = unpruned.pop(0)

        # Check if they overlap
        if overlaps(curr_match, next_match):
            # Choose the larger span
            longer_span = max(curr_match, next_match, key=lambda x: (x[2] - x[1]))
            pruned.append(longer_span)
            if len(unpruned) == 0:
                break
            curr_match = unpruned.pop(0)
        else:
            pruned.append(curr_match)
            curr_match = next_match
    # Recursive base point
    if len(pruned) == num_matches:
        return pruned
    # Recursive function call
    else:
        return prune_overlapping_matches(pruned)

def overlaps(a, b):
    if _span_overlaps(a, b) or _span_overlaps(b, a):
        return True
    return False

def _span_overlaps(a, b):
    _, a_start, a_end = a
    _, b_start, b_end = b
    if a_start >= b_start and a_start < b_end:
        return True
    if a_end > b_start and a_end <= b_end:
        return True
    return False

def matches_to_spans(doc, matches, set_label=True):
    spans = []
    for (rule_id, start, end) in matches:
        if set_label:
            label = doc.vocab.strings[rule_id]
        else:
            label = None
        spans.append(Span(doc, start=start, end=end, label=label))
    return spans

def get_ents_datas_docs(docs_metadatas):
    ents_data = []
    for (doc, metadata) in docs_metadatas:
        ents_data += get_ents_datas_doc(doc, metadata)
    return ents_data

def get_ents_datas_doc(doc, metadata):
    ents_data = []
    for ent in doc.ents:
        data = {"span": ent,
               "text": ent.text,
                "lower": ent.lower_,
               "label": ent.label_,
                "sent": ent.sent.text,
                "is_negated": ent._.is_negated,
                "is_hypothetical": ent._.is_hypothetical,
                "is_historical": ent._.is_uncertain,
                "section_title": ent._.section_title,
               "modifiers": "|".join(sorted(mod.span.text for mod in ent._.modifiers)),
                "normalized_phrase": ent._.target_rule.literal if ent._.target_rule is not None else ent.lower_,
               }
        data.update(metadata)
        ents_data.append(data)
    return ents_data

def get_date(span):
    """If a span is modified by a 'DATE' modifier, parse it to get the actual date value."""
    for mod in span._.modifiers:
        if mod.category == "DATE":
            try:
                return dateutil.parser.parse(mod.span.text)
            except:
                return mod.span.text
    return None

def calculate_rehoused(df,
                       window_size=30,
                       patient_col="pt_id",
                       time_col="time_to_index",
                       doc_class_col="document_classification"):
    """Calculate the NLP-derived ReHouSED score for a cohort of patients.
    Args:
        df (pandas.DataFrame): A DataFrame with at least the 3 columns corresponding to
            `patient_col`, `time_col`, and `doc_class_col`
        window_size (int): The size of fixed time windows over which to aggregate document classifications.
            Default 30
        patient_col (str): Column for patient identifiers over which to group by.
            Default 'pt_id'
        time_col (str): Column containing the number of days to the index date for each document.
            Default 'time_to_index'
        doc_class_col (str): Column containing NLP-derived document classifications.
            Default 'document_classification'
    Returns: DataFrame where each row corresponds to a single patient time interval
    """
    df = df[[patient_col, time_col, doc_class_col]]
    # Filter out unknown documents
    df = df[df[doc_class_col] != "UNKNOWN"]

    # First, group each document into a discrete time interval
    df["time_window"] = df[time_col] // window_size

    # Next, pivot to patient and time window
    rehoused = df.pivot_table(index=[patient_col, "time_window"], columns=[doc_class_col], aggfunc=len, fill_value=0)
    # Selected the single level
    rehoused = rehoused[time_col]

    rehoused["total_documents"] = rehoused["STABLY_HOUSED"] + rehoused["UNSTABLY_HOUSED"]
    rehoused["rehoused"] = rehoused["STABLY_HOUSED"] / rehoused["total_documents"]

    # Now flatten
    rehoused = rehoused.sort_values([patient_col, "time_window"]).reset_index()
    rehoused.columns = rehoused.columns.rename(None)

    return rehoused
