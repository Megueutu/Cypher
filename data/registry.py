import json
from pathlib import Path
from typing import Optional, Union

from src.domain.dataset import Dataset, BaseType, Category, FileFormat
from src.domain.models.registry import Registry

DATA_PATH     = Path("data/analysis")
REGISTRY_PATH = Path("data/registry.json")

def _infer_basetype(filename: str) -> BaseType:
    return BaseType.EXAMPLE if ".example." in filename else BaseType.ORIGINAL

def _load_registry() -> Registry:
    with open(REGISTRY_PATH, "r", encoding="utf-8") as file:
        return json.load(file)

def get_datasets(
        base_category: Optional[Union[Category, list[Category]]] = None,
        basetype: Optional[BaseType] = None,
    ) -> list[Dataset]:
    
    registry = _load_registry()

    if base_category is None:
        categories = list(Category)
    elif isinstance(base_category, Category):
        categories = [base_category]
    elif isinstance(base_category, list) and all(isinstance(category, Category) for category in base_category):
        categories = base_category
    else:
        raise TypeError("base_category must be a Category, a list of Category, or None")

    datasets: list[Dataset] = []
    for category in categories:
        files = registry["datasets"].get(category.value, [])

        for item in files:
            inferred_basetype: BaseType = _infer_basetype(item["file"])

            if basetype is not None and inferred_basetype != basetype:
                continue

            dataset: Dataset = Dataset(item["file"], category, inferred_basetype, FileFormat(item["format"]))
            datasets.append(dataset)

    return datasets

def resolve_path(dataset: Dataset) -> Path:
    path: Path = (DATA_PATH / dataset.category.value / dataset.filename)

    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")

    return path
