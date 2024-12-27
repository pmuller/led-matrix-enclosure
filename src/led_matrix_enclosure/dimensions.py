from dataclasses import dataclass
from typing import TypeAlias, override, Self


XYLike: TypeAlias = (
    "Dimension2D | Position2D | int | float | tuple[float, float] | tuple[int, int]"
)


def _normalize_xy_like_value(value: XYLike) -> tuple[float, float] | tuple[int, int]:
    match value:
        case Dimension2D():
            return value.length, value.width
        case Position2D():
            return value.x, value.y
        case int() | float():
            return value, value
        case tuple():
            return value


@dataclass
class Dimension2D:
    #: 2D size, on the X axis
    length: float
    #: 2D size, on the Y axis
    width: float

    @override
    def __hash__(self) -> int:
        return hash((self.length, self.width))

    @classmethod
    def parse(cls, spec: str) -> Self:
        """Parses a 2 dimensional dimension from a string.

        The string should be in the format of `LENGTHxWIDTH`.
        """
        length, width = spec.split("x")
        return cls(length=float(length), width=float(width))

    @override
    def __str__(self) -> str:
        return f"{self.length}x{self.width}"

    def __neg__(self) -> "Dimension2D":
        return Dimension2D(length=-self.length, width=-self.width)


@dataclass
class Dimension3D:
    #: 3D size, on the X axis
    length: float
    #: 3D size, on the Y axis
    width: float
    #: 3D size, on the Z axis
    height: float

    @classmethod
    def parse(cls, spec: str) -> Self:
        """Parses a 3 dimensional dimension from a string.

        The string should be in the format of `LENGTHxWIDTHxHEIGHT`.
        """
        length, width, height = spec.split("x")
        return cls(length=float(length), width=float(width), height=float(height))

    @override
    def __str__(self) -> str:
        return f"{self.length}x{self.width}x{self.height}"

    def to_2d(self) -> Dimension2D:
        """
        Returns a 2D dimension, by dropping the height.
        """
        return Dimension2D(length=self.length, width=self.width)


@dataclass
class Position2D:
    #: X position
    x: float
    #: Y position
    y: float

    def __neg__(self) -> "Position2D":
        return Position2D(x=-self.x, y=-self.y)

    def __add__(self, other: XYLike) -> "Position2D":
        x, y = _normalize_xy_like_value(other)
        return Position2D(x=self.x + x, y=self.y + y)

    def __sub__(self, other: XYLike) -> "Position2D":
        x, y = _normalize_xy_like_value(other)
        return Position2D(x=self.x - x, y=self.y - y)


@dataclass
class Object2D:
    #: Dimensions of the object
    dimensions: Dimension2D
    #: Position of the object, relative to the top left corner of its parent
    position: Position2D

    @property
    def corners(self) -> tuple[Position2D, Position2D, Position2D, Position2D]:
        return (
            # Top left corner
            self.position,
            # Top right corner
            self.position + Dimension2D(self.dimensions.length, 0),
            # Bottom right corner
            self.position + self.dimensions,
            # Bottom left corner
            self.position + Dimension2D(0, self.dimensions.width),
        )

    def __contains__(self, position: Position2D | tuple[float, float]) -> bool:
        match position:
            case Position2D():
                x = position.x
                y = position.y
            case tuple():
                x, y = position

        return (
            self.position.x <= x <= self.position.x + self.dimensions.length
            and self.position.y <= y <= self.position.y + self.dimensions.width
        )

    def overlaps(self, other: Self) -> bool:
        return any(corner in other for corner in self.corners)

    def __add__(self, other: XYLike) -> "Object2D":
        return Object2D(self.dimensions, self.position + other)

    def __sub__(self, other: XYLike) -> "Object2D":
        return Object2D(self.dimensions, self.position - other)
