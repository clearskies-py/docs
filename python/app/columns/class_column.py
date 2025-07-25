from __future__ import annotations
from typing import overload, Self, TYPE_CHECKING

import clearskies

if TYPE_CHECKING:
    from clearskies import Model

class Class(clearskies.Column):
    is_writeable = clearskies.configs.boolean.Boolean(default=False)
    _descriptor_config_map = None

    def __init__(self):
        super().__init__()

    @overload
    def __get__(self, instance: None, cls: type[Model]) -> Self:
        pass

    @overload
    def __get__(self, instance: Model, cls: type[Model]) -> type:
        pass

    def __get__(self, instance, cls):
        return super().__get__(instance, cls)

    def __set__(self, instance: Model, value: type) -> None:
        instance._next_data[self.name] = value

    def from_backend(self, value):
        return value

    def to_backend(self, data: dict[str, Any]) -> dict[str, Any]:
        if self.name not in data:
            return data
        return {**data, self.name: data[self.name]}
