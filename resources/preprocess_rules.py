from medspacy.preprocess import PreprocessingRule
import re

preprocess_rules = [
    PreprocessingRule(re.compile("[^\s]+\.(org|com|gov)", re.IGNORECASE), " ", desc="Remove simple URLs"),
]