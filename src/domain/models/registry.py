from typing import TypedDict

class RegistryItem(TypedDict):
    id: str
    file: str
    format: str

class Registry(TypedDict):
    datasets: dict[str, list[RegistryItem]]