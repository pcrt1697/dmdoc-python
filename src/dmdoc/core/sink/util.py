from dmdoc.core.sink.model import DataModel, EntityReference


def get_reverse_references(id_entity: str, data_model: DataModel):
    """ Find all entities that reference the provided entity """

    references: dict[str, list[EntityReference]] = {}
    for entity in data_model.entities:
        if not entity.references:
            continue
        current_references = []
        for reference in entity.references:
            if reference.id_entity == id_entity:
                current_references.append(reference)
        if current_references:
            references[entity.id] = current_references
    return references


def get_python_class_id(python_class: type):
    return f"{python_class.__module__}.{python_class.__name__}"
