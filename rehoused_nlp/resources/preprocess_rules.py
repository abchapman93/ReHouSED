from medspacy.preprocess import PreprocessingRule
import re

preprocess_rules = [
    PreprocessingRule("[^\s]+\.(org|com|gov)", " ", desc="Remove simple URLs", ignorecase=True),
]