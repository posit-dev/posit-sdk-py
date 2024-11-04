from typing import Dict, List, Tuple, TypeVar, Union

# Implemented in https://github.com/posit-dev/py-shiny/blob/415ced034e6c500adda524abb7579731c32088b5/shiny/types.py#L357-L386
# Table from: https://github.com/python/cpython/blob/df1eec3dae3b1eddff819fd70f58b03b3fbd0eda/Lib/json/encoder.py#L77-L95
# +-------------------+---------------+
# | Python            | JSON          |
# +===================+===============+
# | dict              | object        |
# +-------------------+---------------+
# | list, tuple       | array         |
# +-------------------+---------------+
# | str               | string        |
# +-------------------+---------------+
# | int, float        | number        |
# +-------------------+---------------+
# | True              | true          |
# +-------------------+---------------+
# | False             | false         |
# +-------------------+---------------+
# | None              | null          |
# +-------------------+---------------+
Jsonifiable = Union[
    str,
    int,
    float,
    bool,
    None,
    List["Jsonifiable"],
    Tuple["Jsonifiable", ...],
    "JsonifiableDict",
]

JsonifiableT = TypeVar("JsonifiableT", bound="Jsonifiable")
JsonifiableDict = Dict[str, Jsonifiable]
JsonifiableList = List[JsonifiableT]

ResponseAttrs = Dict[str, Jsonifiable]
