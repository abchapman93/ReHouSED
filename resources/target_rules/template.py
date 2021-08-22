from medspacy.ner import TargetRule
from .. import callbacks

template_rules = [

    # Headers
    TargetRule("Housing:", "HEADER"),
    TargetRule("Plan:", "HEADER"),
    TargetRule("Homelessness:", "HEADER"),
]