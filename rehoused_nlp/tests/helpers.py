def find_ents(doc, label, n=None):
    targets = []
    for ent in doc.ents:
        if ent.label_ == label:
            targets.append(ent)
            if n is not None and len(targets) == n:
                break
    return targets

def _test_label_texts(nlp, label_texts, attrs=None):
    failed = []
    for label, texts in label_texts.items():
        for text in texts:
            rslts = _test_label_text(nlp, text, label, 1, attrs)
            if rslts != []:
                failed.append(rslts)
    assert failed == [], failed

def _test_label_text(nlp, text, label, n_ents=1, attrs=None):
    doc = nlp(text)
    failed = []
    ents = find_ents(doc, label, 1)
    if len(ents) == 0:
        return [text, None, label, attrs, None]
    for ent in ents:
        if attrs is not None:
            actual_attrs = {attr: getattr(ent._, attr) for attr in attrs}
            if actual_attrs != attrs:
                failed.append([text, ent, label, attrs, actual_attrs])

    return failed