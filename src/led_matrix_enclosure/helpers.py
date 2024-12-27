from typing import cast

from build123d import Compound


def get_compound_child(compound: Compound, label: str) -> Compound:
    for child in cast(tuple[Compound, ...], compound.children):
        if child.label == label:
            return child

    raise ValueError(f"Child with label {label} not found in compound")
