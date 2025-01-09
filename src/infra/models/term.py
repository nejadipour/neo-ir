from neomodel import StructuredNode, StringProperty, IntegerProperty, RelationshipTo


class Term(StructuredNode):
    value = StringProperty(unique_index=True, required=True)
    document_frequency = IntegerProperty(default=0)

    documents = RelationshipTo('src.infra.models.Document', 'src.infra.models.EXISTS_IN')
