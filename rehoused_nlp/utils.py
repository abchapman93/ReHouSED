from spacy.tokens import Span

import os
from pathlib import Path

RESOURCES_DIR = os.path.join(
    Path(__file__).resolve().parents[0], "resources"
)

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

    # Token.set_extension("concept_tag", default="", force=True)
    for (_, attr_dict) in CONTEXT_ATTRS.items():
        for (attr_name, attr_value) in attr_dict.items():
            Span.set_extension(attr_name, default=False, force=True)

    # Span.set_extension("is_experienced", default=True)
    Doc.set_extension("document_classification", default=None, force=True)
    Span.set_extension("is_template", default=False, force=True)
    Span.set_extension("is_classifier", default=False, force=True)
    Span.set_extension("is_ignored", default=False, force=True)
    Span.set_extension("is_asserted", getter=lambda x: is_asserted(x), force=True)

    Token.set_extension("ignore", default=False, force=True)

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

def build_nlp(model="en_core_web_sm", disable=None,
              rules="default",
              add_target_rules=True, add_context_rules=True,
              max_scope=15):
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
    from rehoused_nlp.resources.preprocess_rules import preprocess_rules
    from medspacy.preprocess import Preprocessor
    from .tokenizer import ssvf_tokenizer
    preprocessor = Preprocessor(ssvf_tokenizer(nlp))
    preprocessor.add(preprocess_rules)
    nlp.tokenizer = preprocessor

    # Concept tagger

    from medspacy.target_matcher import ConceptTagger
    from rehoused_nlp.resources import concept_tag_rules
    concept_tagger = nlp.add_pipe("medspacy_concept_tagger")
    concept_tagger.add(concept_tag_rules.rules)
    concept_tag_rules = []
    concept_tagger.add(concept_tag_rules)


    # Add a target matcher
    from medspacy.target_matcher import TargetMatcher

    target_matcher = nlp.add_pipe("medspacy_target_matcher")
    if add_target_rules:
        from rehoused_nlp.resources.target_rules import target_rules
        target_matcher.add(target_rules.rules)

    # Add ConText
    context = nlp.add_pipe("medspacy_context",
                           config=dict(rules=rules, add_attrs=CONTEXT_ATTRS,
                                    max_scope=max_scope))

    if add_context_rules:
        from rehoused_nlp.resources.context_rules import context_rules
        context.add(context_rules)



    # Add a sectionizer
    from medspacy.section_detection import Sectionizer
    # SECTION_RULES_FILEPATH = os.path.join(
    #     Path(__file__).resolve().parents[1], "resources", "section_patterns.jsonl"
    # )
    # print(SECTION_RULES_FILEPATH)
    # from src.nlp.resources import section_rules

    section_attrs = {
        "problem_list": {"is_historical": True},
        "past_medical_history": {"is_historical": True},
        "patient_education": {"is_ignored": True},
    }
    sectionizer = nlp.add_pipe("medspacy_sectionizer",
                               config=dict(rules=rules, add_attrs=section_attrs, max_scope=300))


    from rehoused_nlp.resources.section_rules import section_rules
    sectionizer.add(section_rules)

    # Add a PostProcessor
    from medspacy.postprocess import Postprocessor
    from rehoused_nlp.resources import postprocess_rules



    postprocessor = nlp.add_pipe("medspacy_postprocessor")
    postprocessor.add(postprocess_rules.rules)

    from .ssvf_component import SSVFDocumentClassifier
    nlp.add_pipe("document_classifier")

    return nlp

def visualize_doc_classification(doc, doc_id=None, jupyter=True, colors=None):
    from medspacy.visualization import visualize_ent
    html = ""
    if doc_id is not None:
        html += f"<h3>Document ID: {doc_id}</h3>"
    html += f"<h3>Document Classification: {doc._.document_classification}</h3>"
    html += visualize_ent(doc, jupyter=False, colors=colors)

    if jupyter is True:
        from IPython.display import display, HTML
        display(HTML(html))
    else:
        return html
