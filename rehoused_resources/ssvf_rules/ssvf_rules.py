from .evidence_of_homelessness import homeless_rules
from .evidence_of_housing import housing_rules
from .temporary_housing import temporary_housing_rules
from .risk_of_homelessness import risk_of_homelessness_rules
from .doubling_up import doubling_up_rules
from .template import template_rules

from .other import other_rules

rules = (homeless_rules + housing_rules + temporary_housing_rules
         + risk_of_homelessness_rules + doubling_up_rules
        + template_rules
         + other_rules
         )