from dataclasses import dataclass

from build123d import Shape

from led_matrix_enclosure.sides import Side


Corner2D = (
    tuple[Side.BACK, Side.LEFT]
    | tuple[Side.BACK, Side.RIGHT]
    | tuple[Side.RIGHT, Side.BACK]
    | tuple[Side.RIGHT, Side.FRONT]
    | tuple[Side.FRONT, Side.LEFT]
    | tuple[Side.FRONT, Side.RIGHT]
    | tuple[Side.LEFT, Side.FRONT]
    | tuple[Side.LEFT, Side.BACK]
)


TWO_DIMENSIONAL_CORNERS: tuple[Corner2D, Corner2D, Corner2D, Corner2D] = (
    (Side.FRONT, Side.LEFT),
    (Side.FRONT, Side.RIGHT),
    (Side.BACK, Side.LEFT),
    (Side.BACK, Side.RIGHT),
)


@dataclass
class Corner2DPredicate:
    corner: Corner2D

    def __call__(self, shape: Shape) -> bool:
        center_x, center_y, _ = shape.center().to_tuple()

        match self.corner:
            case (Side.FRONT, Side.LEFT) | (Side.LEFT, Side.FRONT):
                return center_x == 0 and center_y == 0
            case (Side.FRONT, Side.RIGHT) | (Side.RIGHT, Side.FRONT):
                return center_x > 0 and center_y == 0
            case (Side.BACK, Side.LEFT) | (Side.LEFT, Side.BACK):
                return center_x == 0 and center_y > 0
            case (Side.BACK, Side.RIGHT) | (Side.RIGHT, Side.BACK):
                return center_x > 0 and center_y > 0
