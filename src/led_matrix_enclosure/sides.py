from copy import copy
from enum import Enum
from argparse import (
    Action,
    ArgumentParser,
    _ActionsContainer,  # pyright: ignore[reportPrivateUsage]
    ArgumentTypeError,
    Namespace,
)
from typing import Self, Any, final, override
from collections.abc import Sequence


class Side(Enum):
    LEFT = "left"
    RIGHT = "right"
    BACK = "back"
    FRONT = "front"

    @property
    def is_horizontal(self) -> bool:
        """Whether the side is horizontal (X-axis)."""
        return self in (Side.LEFT, Side.RIGHT)

    @property
    def is_start(self) -> bool:
        """Whether the side is a start side (left or front)."""
        return self in (Side.LEFT, Side.FRONT)

    @property
    def opposite(self) -> "Side":
        """Opposite side."""
        match self:
            case Side.LEFT:
                return Side.RIGHT
            case Side.RIGHT:
                return Side.LEFT
            case Side.BACK:
                return Side.FRONT
            case Side.FRONT:
                return Side.BACK

    @override
    def __str__(self) -> str:
        return self.value


class SideAction(Action):
    def __init__(
        self,
        option_strings: Sequence[str],
        dest: str,
        default: bool,
        help: str | None = None,
        metavar: str | None = None,
    ) -> None:
        super().__init__(
            option_strings,
            dest,
            nargs="+",
            default=SideDict(default=default),
            help=help,
            metavar=metavar,
        )

    @override
    def __call__(
        self,
        parser: ArgumentParser,
        namespace: Namespace,
        values: str | Sequence[Any] | None = None,  # pyright: ignore[reportExplicitAny]
        option_string: str | None = None,
    ) -> None:
        if not hasattr(namespace, self.dest):
            setattr(
                namespace,
                self.dest,
                self.default,  # pyright: ignore[reportAny]
            )

        sides: SideDict = getattr(namespace, self.dest)

        if values is None:
            return

        if isinstance(values, str):
            values = [values]

        for value in values:  # pyright: ignore[reportAny]
            try:
                side = Side(value)
                sides[side] = not sides.default
            except ValueError:
                raise ArgumentTypeError(
                    f"Invalid side: {value}. Valid values are: {[side.value for side in Side]}"
                )


@final
class SideDict(dict[Side, bool]):
    def __init__(
        self,
        front: bool | None = None,
        back: bool | None = None,
        left: bool | None = None,
        right: bool | None = None,
        default: bool = True,
    ) -> None:
        super().__init__(
            {
                Side.FRONT: default if front is None else front,
                Side.BACK: default if back is None else back,
                Side.LEFT: default if left is None else left,
                Side.RIGHT: default if right is None else right,
            }
        )
        self.default = default

    @classmethod
    def add_cli_argument(
        cls,
        container: _ActionsContainer,
        name_or_flags: str,
        metavar: str = "SIDE",
        dest: str | None = None,
        default: bool = True,
        help: str | None = None,
    ) -> None:
        _ = container.add_argument(
            name_or_flags,
            metavar=metavar,
            action=SideAction,
            dest=dest,
            help=help,
            default=default,
        )

    @classmethod
    def from_cli_arguments(cls, arguments: Namespace) -> Self:
        return cls(
            front=arguments.front,  # pyright: ignore[reportAny]
            back=arguments.back,  # pyright: ignore[reportAny]
            left=arguments.left,  # pyright: ignore[reportAny]
            right=arguments.right,  # pyright: ignore[reportAny]
        )

    @override
    def __str__(self) -> str:
        return (
            " ".join(side.value for side, value in self.items() if value)
            if any(self.values())
            else "none"
        )

    def __invert__(self) -> "SideDict":
        return SideDict(
            front=not self[Side.FRONT],
            back=not self[Side.BACK],
            left=not self[Side.LEFT],
            right=not self[Side.RIGHT],
            default=not self.default,
        )

    def get_adjacents(self, side: Side) -> tuple[Side, ...]:
        """Get adjacent sides."""
        match side:
            case Side.LEFT:
                candidates = (Side.BACK, Side.FRONT)
            case Side.RIGHT:
                candidates = (Side.BACK, Side.FRONT)
            case Side.FRONT:
                candidates = (Side.LEFT, Side.RIGHT)
            case Side.BACK:
                candidates = (Side.LEFT, Side.RIGHT)

        return tuple(side for side in candidates if self[side])

    def has_opposite(self, side: Side) -> bool:
        """Whether the side has an opposite side."""
        return self[side.opposite]

    @property
    def horizontal(self) -> tuple[Side, ...]:
        """Horizontal sides (X-axis)."""
        return tuple(
            side for side, has_side in self.items() if has_side and side.is_horizontal
        )

    @property
    def vertical(self) -> tuple[Side, ...]:
        """Vertical sides (Y-axis)."""
        return tuple(
            side
            for side, has_side in self.items()
            if has_side and not side.is_horizontal
        )

    def __add__(self, side: Side) -> "SideDict":
        new_dict = copy(self)
        new_dict[side] = True
        return new_dict

    def __sub__(self, side: Side) -> "SideDict":
        new_dict = copy(self)
        new_dict[side] = False
        return new_dict
