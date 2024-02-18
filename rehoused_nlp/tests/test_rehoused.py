from ..utils import build_nlp
from spacy.tokens import Span

nlp = build_nlp()

def test_doc():
    doc = nlp("This is a text.")