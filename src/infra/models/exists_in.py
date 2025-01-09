from neomodel import StructuredRel, IntegerProperty, ArrayProperty, BooleanProperty


class ExistsIn(StructuredRel):
    term_frequency = IntegerProperty(required=True)
    positions = ArrayProperty(base_property=IntegerProperty(), required=True)
    is_champion = BooleanProperty(default=False)
