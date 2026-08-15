from dataclasses import dataclass
from enum import Enum

class BaseType(Enum):
    ORIGINAL = "original"
    EXAMPLE  = "examples"

class Category(Enum):
    DICTIONARY = "dictionary"
    SEQUENCE   = "sequence"
    PATTERN    = "pattern"
    BLACKLIST  = "blacklist"

class FileFormat(Enum):
    TXT     = "txt"
    CSV     = "csv"
    JSON    = "json"
    XML     = "xml"
    PARQUET = "parquet"

@dataclass
class Dataset:
    filename:   str
    category:   Category
    basetype:   BaseType
    fileformat: FileFormat