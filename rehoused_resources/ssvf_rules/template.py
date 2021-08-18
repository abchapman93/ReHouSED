from medspacy.ner import TargetRule
from .. import callbacks

template_rules = [
# Templates

    # Headers
    TargetRule("Housing:", "HEADER"),
    TargetRule("Plan:", "HEADER"),
    TargetRule("Homelessness:", "HEADER"),
    TargetRule("SKILLS NEEDED TO MAINTAIN PERMANENT HOUSING:", "HEADER"),
]