from dataclasses import MISSING, dataclass, fields


@dataclass(eq=False, kw_only=True)
class Entity[EntityId]:
    """Base class for domain objects that have identity."""

    id: EntityId

    def __post_init__(self) -> None:
        """Materialize static defaults replaced by SQLAlchemy instrumentation."""

        for declared_field in fields(self):
            if not declared_field.init and declared_field.default is not MISSING:
                setattr(self, declared_field.name, declared_field.default)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash((self.__class__, self.id))
