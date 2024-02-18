import medspacy.target_matcher
from spacy.tokens import Span
import os
import json
from pathlib import Path

from .resources import callbacks

from medspacy.target_matcher import TargetRule
from medspacy.context import ConTextRule
from medspacy.section_detection import SectionRule
from medspacy.preprocess import PreprocessingRule

RESOURCES_FOLDER = os.path.join(Path(__file__).resolve().parents[0],
                                "resources",)

CONTEXT_ATTRS = {
        "NEGATED_EXISTENCE": {"is_negated": True},
        "HYPOTHETICAL": {"is_hypothetical": True},
        "AT_RISK": {"is_uncertain": True},
        "HISTORICAL": {"is_historical": True},
        "NOT_RELEVANT": {"is_ignored": True},
        "FAMILY": {"is_family": True},
    }

SECTION_ATTRS = {
        "problem_list": {"is_historical": True},
        "past_medical_history": {"is_historical": True},
        "patient_education": {"is_ignored": True},
    }

RULE_CLASSES = {
    "concept_tagger": TargetRule,
    "target_matcher": TargetRule,
    "context": ConTextRule,
    "sectionizer": SectionRule,
    "preprocessor": PreprocessingRule
}

def get_project_folder(directory=True):
    import os
    cwd = os.getcwd()
    cwd_split = cwd.split("\\")
    if directory:
        return "\\".join(cwd_split[:2])
    return cwd_split[1]

def set_extensions():
    from spacy.tokens import Span, Token, Doc

    Token.set_extension("concept_tag", default="", force=True)
    for (_, attr_dict) in CONTEXT_ATTRS.items():
        for (attr_name, attr_value) in attr_dict.items():
            Span.set_extension(attr_name, default=False, force=True)

    # Span.set_extension("is_experienced", default=True)
    Doc.set_extension("document_classification", default=None, force=True)
    Span.set_extension("is_template", default=False)
    Span.set_extension("is_classifier", default=False)
    Span.set_extension("literal", getter=get_literal)
    Span.set_extension("is_asserted", getter=lambda x: is_asserted(x), force=True)

def get_literal(span):
    rule = span._.target_rule
    if rule is None:
        return
    literal = rule.literal
    if literal.lower() == span.text.lower():
        return
    return literal

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
              resources_dir=None,
              cfg_file=None,
              max_scope=15,
              **kwargs):
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

    # Add custom medspaCy components
    # Concept tagger
    concept_tagger = nlp.add_pipe("medspacy_concept_tagger")
    target_matcher = nlp.add_pipe("medspacy_target_matcher")
    context = nlp.add_pipe("medspacy_context",
                           config=dict(rules=None, span_attrs=CONTEXT_ATTRS,
                                    prune_on_target_overlap=True,
                                max_scope=max_scope))
    sectionizer = nlp.add_pipe("medspacy_sectionizer",
                               config=dict(rules=None, span_attrs=SECTION_ATTRS, max_section_length=300))

    # Add a PostProcessor
    from .resources import postprocess_rules
    postprocessor = nlp.add_pipe("rehoused_postprocessor")
    postprocessor.add(postprocess_rules.rules)

    # Document classifier
    from .rehoused_document_classifier import RehousedDocumentClassifier
    nlp.add_pipe("rehoused_document_classifier")

    nlp = add_rules_from_cfg(nlp, cfg_file, resources_dir)

    return nlp


def add_rules_from_cfg(nlp, cfg_file=None, resources_dir=None):
    rules = load_rules_from_cfg(cfg_file, resources_dir)

    for (name, component_rules) in rules.items():
        try:
            # NOTE: This is a bit strange, but it prevents changing lots of references in code
            # to prefix with "medspacy_" when it is only needed here.
            pipe_name = name
            if name in ['concept_tagger', 'context', 'target_matcher', 'sectionizer', ]:
                pipe_name = 'medspacy_' + name
                if pipe_name not in nlp.pipe_names:
                    component = nlp.add_pipe(pipe_name)
                else:
                    component = nlp.get_pipe(pipe_name)
        except KeyError:
            raise ValueError("Invalid component:", name)
        component.add(component_rules)



    return nlp

def load_rules_from_cfg(cfg_file=None, resources_dir=None):
    if resources_dir is None:
        resources_dir = RESOURCES_FOLDER
    if cfg_file is None:
        cfg_file = os.path.join(resources_dir, "configs", "rehoused_v1_config.json")
    if not os.path.exists(cfg_file):
        cfg_file2 = os.path.join(resources_dir, "configs", cfg_file)
        if os.path.exists(cfg_file2):
            cfg_file = cfg_file2
        else:
            raise FileNotFoundError(f"Invalid config filename or filepath: '{cfg_file}'")
    cfg = load_cfg_file(cfg_file)


    rules = _load_cfg_rules(cfg, resources_dir)
    return rules

def load_cfg_file(filepath):
    import json
    with open(filepath) as f:
        cfg = json.loads(f.read())

    return cfg

def _load_cfg_rules(cfg, resources_dir):
    rules = dict()
    for component, filepaths in cfg["resources"][0].items():
        if component not in RULE_CLASSES:
            raise ValueError(f"Invalid component name {component} in config. "
                             f"Please add custom logic to add these rules to your pipeline. "
                             f"Valid options are: {RULE_CLASSES.keys()}")
        rule_cls = RULE_CLASSES[component]
        rules[component] = []
        for filepath in filepaths:
            abspath = os.path.abspath(os.path.join(resources_dir, filepath))
            # Instead of using default medspaCy serialization, load using custom function
            # so we can add on_match callbacks and disable particular rules
            with open(abspath) as f:
                rule_dicts = [d for d in list(json.load(f).values())[0] if d.get("disabled") is not True]

            rules[component] += [load_rehoused_rule(rule_dict, rule_cls) for rule_dict in rule_dicts]
    return rules

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
                "lower": ent.text.lower(),
               "label": ent.label_,
                "sent": ent.sent.text,
                "is_negated": ent._.is_negated,
                "is_hypothetical": ent._.is_hypothetical,
                "is_historical": ent._.is_uncertain,
                "section_title": ent._.section_title,
               "modifiers": "|".join(sorted(mod.span.text for mod in ent._.modifiers)),
                "normalized_phrase": ent._.target_rule.literal if ent._.target_rule is not None else ent.text.lower(),
               }
        data.update(metadata)
        ents_data.append(data)
    return ents_data

def rehoused_rule_to_dict(rule):
    """Serialize a medspaCy rule to a dict while keeping
    attributes not supported by default medspaCy serialization.
    """
    rule_dict = rule.to_dict()
    if (on_match := rule.on_match) is not None:
        rule_dict["on_match"] = on_match.__name__
    return rule_dict

def add_rehoused_rules_from_dicts(rule_dicts, component):
    if isinstance(component, (medspacy.target_matcher.TargetRule,
                              medspacy.target_matcher.concept_tagger.ConceptTagger)
                  ):
        cls = TargetRule
    elif isinstance(component, medspacy.context.ConText):
        cls = ConTextRule
    elif isinstance(component, medspacy.section_detection.Sectionizer):
        cls = SectionRule
    else:
        raise TypeError("component must be one of the classes TargetRule, Concept Tagger,"
                        " ConText, or Sectionizer, not", type(component))
    rules = []
    for d in rule_dicts:
        if not d.get("disabled", False):
            rules.append(load_rehoused_rule(d, cls))
    component.add(rules)

def load_rehoused_rule(rule_dict, cls):
    """Load a TargetRule, ConTextRule, or SectionRule
    while adding additional functionality not offered by
    native medspaCy (i.e., serialized callback functions).
    Arguments:
        rule_dict: A dictionary representing a serialized rule.
            Can contain a key/value pair `on_match` that should
            correspond to a function defined in resources.utils
            Can  also contain a "disabled" key/value, in which case
            the rule will not be added.
        cls: The class that the rule should be loaded as.
            e.g., TargetRule, ConTextRule, SectionRule
    Returns:
        A rule of type cls
    """
    if cls not in (TargetRule, ConTextRule, SectionRule):
        raise TypeError("Need valid medspaCy rule type, not", str(cls))
    if (on_match := rule_dict.get("on_match")) is not None:
        rule_dict = {k: v for (k, v) in rule_dict.items() if k not in ("on_match",)}
        rule = from_dict(cls, rule_dict)
        try:
            func = getattr(callbacks, on_match)
        except AttributeError:
            raise ValueError("Invalid callback function name:", on_match)
        rule.on_match = func
    else:
        rule = from_dict(cls, rule_dict)
    return rule

def from_dict(cls, rule_dict) :
    """
    Reads a dictionary into a TargetRule, ConTextRule, or SectionRule.
    A custom version of the medspaCy class method that is less restrictive.

    Args:
        cls: The class of the rule to convert
        rule_dict: The dictionary to convert.

    Returns:
        The ConTextRule created from the dictionary.
    """
    rule = cls(**rule_dict)
    return rule

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
