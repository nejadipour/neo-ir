from neomodel import StructuredNode, IntegerProperty, StringProperty, RelationshipFrom


class Document(StructuredNode):
    doc_id = IntegerProperty(unique_index=True, required=True)
    title = StringProperty()
    url = StringProperty()

    terms = RelationshipFrom('src.infra.models.Term', 'src.infra.models.EXISTS_IN')
