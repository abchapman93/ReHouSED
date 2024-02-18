from medspacy.preprocess import PreprocessingRule
import re

preprocess_rules = [\
    # PreprocessingRule(r"([a-z])([\s]{2,})([a-z])")),
    PreprocessingRule(r"([a-z])([\r\n\s]{2,})([a-z])",
                      repl=lambda match: match.group(1) + " " + match.group(3),
                      flags=re.UNICODE,
                      desc="Replace carriage returns in the middle of sentences with a single space"),
    PreprocessingRule(r"\[X \]|\[ X\]", "[X] ",
                     desc="Normalize filled-in check box and insert space after to allow tokenizinng"),
    PreprocessingRule(r"\[\s+\][\s]+", "[] ",
                     desc="Normalize empty check box and insert space after to allow tokenizinng"),
    PreprocessingRule(r"\( \([\s]+", "() ",
                     desc="Normalize empty check box and insert space after to allow tokenizinng"),

    PreprocessingRule(r"([a-zA-Z,]) ?([\n\r]){1,}([a-z])",

                 repl=lambda match: match.group(1) + " " + match.group(3),
                flags=re.UNICODE,
                 desc="Eliminate carriage returns in the middle of a sentence."),

    PreprocessingRule(r"\r\n", "\n", desc="Replace carriage returns with a single new line"),
    PreprocessingRule(r"([A-Za-z][0-9]{2}\.[0-9]{1,3})(,)",
                     lambda match: match.group(1) + " " + match.group(2),
                     desc="Lists of ICD-9/10 codes are thrown off by commas"),
    PreprocessingRule(r"[^\s]+\.(org|com|gov)",  " ", desc="Remove simple URLs"),
    PreprocessingRule(r"\"", desc="Remove quotations from text."), # TODO: This may be too destructive
    PreprocessingRule(r"house hold", "household"),

]