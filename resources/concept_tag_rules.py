from medspacy.target_matcher import TargetRule

rules = [
    TargetRule(literal="apartment", category="RESIDENCE",
               pattern=[{'IS_TITLE': True, 'OP': '+'}, {'LOWER': {'REGEX': 'apartment'}}],
               ),
    TargetRule(literal="<RESIDES>", category="RESIDES", pattern=[{'LEMMA': {'IN': ['reside', 'stay', 'live', 'sleep']}},
                                                                 {'LOWER': {'IN': ['in', 'at']}, 'OP': '?'}],
               attributes=None),
    TargetRule(literal="move in", category="RESIDES", pattern=[{'LEMMA': 'move'}, {'LOWER': 'in'}],
               ),
    TargetRule(literal="current living situation:", category="RESIDES"),
    TargetRule(literal="veteran", category="PATIENT",
               pattern=[{'LOWER': {'REGEX': '^vet(eran)?'}}, {'LOWER': "'s", 'OP': '?'}],
               ),
    TargetRule(literal="patient", category="PATIENT",
               pattern=[{'LOWER': {'IN': ['patient', 'pt', 'pt.']}}, {'LOWER': "'s", 'OP': '?'}],
               ),
    TargetRule(literal="patient", category="PATIENT", pattern=[{'LOWER': {'IN': ['my', 'me']}}],
               ),
    TargetRule(literal="<DET> job", category="EMPLOYMENT", pattern=[{'POS': 'DET'}, {'LOWER': 'job'}],
               ),
    TargetRule(literal="...Homeless", category="HOMELESSNESS", pattern=[{'LOWER': {'REGEX': 'homeless'}}],
               attributes=None),
    TargetRule(literal="father", category="FAMILY"),
    TargetRule(literal="fathers", category="FAMILY"),
    TargetRule(literal="girlfriend", category="FAMILY"),
    TargetRule(literal="boyfriend", category="FAMILY"),
    TargetRule(literal="fiance", category="FAMILY"),
    TargetRule(literal="fiancee", category="FAMILY"),
    TargetRule(literal="mother", category="FAMILY"),
    TargetRule(literal="mothers", category="FAMILY"),
    TargetRule(literal="brother", category="FAMILY"),
    TargetRule(literal="brothers", category="FAMILY"),
    TargetRule(literal="sister", category="FAMILY"),
    TargetRule(literal="sisters", category="FAMILY"),
    TargetRule(literal="friend", category="FAMILY"),
    TargetRule(literal="buddy", category="FAMILY"),
    TargetRule(literal="buddies", category="FAMILY"),
    TargetRule(literal="friends", category="FAMILY"),
    TargetRule(literal="daughter", category="FAMILY"),
    TargetRule(literal="daughters", category="FAMILY"),
    TargetRule(literal="son", category="FAMILY"),
    TargetRule(literal="sons", category="FAMILY"),
    TargetRule(literal="grandson", category="FAMILY"),
    TargetRule(literal="grandsons", category="FAMILY"),
    TargetRule(literal="grandparent", category="FAMILY"),
    TargetRule(literal="grandparents", category="FAMILY"),
    TargetRule(literal="grandfather", category="FAMILY"),
    TargetRule(literal="grandfathers", category="FAMILY"),
    TargetRule(literal="grandmother", category="FAMILY"),
    TargetRule(literal="grandmothers", category="FAMILY"),
    TargetRule(literal="granddaughter", category="FAMILY"),
    TargetRule(literal="granddaughters", category="FAMILY"),
    TargetRule(literal="relative", category="FAMILY"),
    TargetRule(literal="relatives", category="FAMILY"),
    TargetRule(literal="non relative", category="FAMILY"),
    TargetRule(literal="non relatives", category="FAMILY"),
    TargetRule(literal="non-relative", category="FAMILY"),
    TargetRule(literal="non-relatives", category="FAMILY"),
    TargetRule(literal="niece", category="FAMILY"),
    TargetRule(literal="nieces", category="FAMILY"),
    TargetRule(literal="nephew", category="FAMILY"),
    TargetRule(literal="nephews", category="FAMILY"),
    TargetRule(literal="uncle", category="FAMILY"),
    TargetRule(literal="uncles", category="FAMILY"),
    TargetRule(literal="aunt", category="FAMILY"),
    TargetRule(literal="aunts", category="FAMILY"),
    TargetRule(literal="parent", category="FAMILY"),
    TargetRule(literal="parents", category="FAMILY"),
    TargetRule(literal="homeless shelter", category="TEMPORARY_HOUSING"),
    TargetRule(literal="homeless shelters", category="TEMPORARY_HOUSING"),
    TargetRule(literal="shelter", category="TEMPORARY_HOUSING"),
    TargetRule(literal="shelters", category="TEMPORARY_HOUSING"),
    TargetRule(literal="YMCA", category="TEMPORARY_HOUSING"),
    TargetRule(literal="Salvation Army", category="TEMPORARY_HOUSING"),
    TargetRule(literal="the streets", category="HOMELESS_LOCATION"),
    TargetRule(literal="the street", category="HOMELESS_LOCATION"),
    TargetRule(literal="motel", category="HOMELESS_LOCATION"),
    TargetRule(literal="motels", category="HOMELESS_LOCATION"),
    TargetRule(literal="hotel", category="HOMELESS_LOCATION"),
    TargetRule(literal="park", category="HOMELESS_LOCATION"),
    TargetRule(literal="parks", category="HOMELESS_LOCATION"),
    TargetRule(literal="hotels", category="HOMELESS_LOCATION"),
    TargetRule(literal="woods", category="HOMELESS_LOCATION"),
    TargetRule(literal="car", category="HOMELESS_LOCATION"),
    TargetRule(literal="vehicle", category="HOMELESS_LOCATION"),
    TargetRule(literal="literally homeless", category="HOMELESSNESS"),
    TargetRule(literal="house", category="RESIDENCE"),
    TargetRule(literal="housing", category="RESIDENCE"),
    TargetRule(literal="home", category="RESIDENCE"),
    TargetRule(literal="apt", category="RESIDENCE"),
    TargetRule(literal="apt.", category="RESIDENCE"),
    TargetRule(literal="apartment", category="RESIDENCE"),
    TargetRule(literal="condo", category="RESIDENCE"),
    TargetRule(literal="stable housing", category="RESIDENCE"),
    TargetRule(literal="unit", category="RESIDENCE"),
    TargetRule(literal="place", category="RESIDENCE")

]