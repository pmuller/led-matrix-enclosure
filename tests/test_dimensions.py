import pytest

from led_matrix_enclosure.dimensions import (
    Dimension2D,
    Dimension3D,
    Object2D,
    Position2D,
)


@pytest.mark.parametrize(
    ("spec", "expected"),
    [
        ("10x20", Dimension2D(10, 20)),
        ("1.2x3.4", Dimension2D(1.2, 3.4)),
    ],
)
def test_dimension_2d__parse(spec: str, expected: Dimension2D) -> None:
    assert Dimension2D.parse(spec) == expected


@pytest.mark.parametrize(
    ("dimension", "expected"),
    [
        (Dimension2D(10, 20), "10x20"),
        (Dimension2D(1.2, 3.4), "1.2x3.4"),
    ],
)
def test_dimension_2d__str(dimension: Dimension2D, expected: str) -> None:
    assert str(dimension) == expected


def test_dimension_2d__hash() -> None:
    # Just validate that it is hashable.
    # Not sure how to test this better without copy/pasting the implementation.
    assert {Dimension2D(1, 2): True} == {Dimension2D(1, 2): True}


def test_dimension_2d__neg() -> None:
    assert -Dimension2D(10, 20) == Dimension2D(-10, -20)


@pytest.mark.parametrize(
    ("spec", "expected"),
    [
        ("10x20x30", Dimension3D(10, 20, 30)),
        ("1.2x3.4x5.6", Dimension3D(1.2, 3.4, 5.6)),
    ],
)
def test_dimension_3d__parse(spec: str, expected: Dimension3D) -> None:
    assert Dimension3D.parse(spec) == expected


@pytest.mark.parametrize(
    ("dimension", "expected"),
    [
        (Dimension3D(10, 20, 30), "10x20x30"),
        (Dimension3D(1.2, 3.4, 5.6), "1.2x3.4x5.6"),
    ],
)
def test_dimension_3d__str(dimension: Dimension3D, expected: str) -> None:
    assert str(dimension) == expected


def test_dimension_3d__to_2d() -> None:
    assert Dimension3D(10, 20, 30).to_2d() == Dimension2D(10, 20)


@pytest.mark.parametrize(
    ("position_2d", "other", "expected"),
    [
        (Position2D(10, 20), Dimension2D(10, 20), Position2D(20, 40)),
        (Position2D(10, 20), Position2D(10, 20), Position2D(20, 40)),
        (Position2D(10, 20), 10, Position2D(20, 30)),
    ],
)
def test_position_2d__add(
    position_2d: Position2D,
    other: Position2D | Dimension2D | int | float,
    expected: Position2D,
) -> None:
    assert position_2d + other == expected


def test_position_2d__neg() -> None:
    assert -Position2D(10, 20) == Position2D(-10, -20)


@pytest.mark.parametrize(
    ("position_2d", "other", "expected"),
    [
        (Position2D(10, 20), Dimension2D(10, 20), Position2D(0, 0)),
        (Position2D(10, 20), Position2D(10, 20), Position2D(0, 0)),
        (Position2D(10, 20), 10, Position2D(0, 10)),
    ],
)
def test_position_2d__sub(
    position_2d: Position2D,
    other: Position2D | Dimension2D | int | float,
    expected: Position2D,
) -> None:
    assert position_2d - other == expected


def test_object_2d__corners() -> None:
    assert Object2D(Dimension2D(10, 20), Position2D(10, 20)).corners == (
        Position2D(10, 20),
        Position2D(20, 20),
        Position2D(20, 40),
        Position2D(10, 40),
    )


@pytest.mark.parametrize(
    ("position", "expected"),
    [
        (Position2D(15, 30), True),
        (Position2D(0, 0), False),
        ((15, 30), True),
        ((0, 0), False),
    ],
)
def test_object_2d__contains(
    position: Position2D | tuple[float, float],
    expected: bool,
) -> None:
    assert (
        position
        in Object2D(
            Dimension2D(10, 20),
            Position2D(10, 20),
        )
    ) is expected


def test_object_2d__overlaps() -> None:
    assert Object2D(Dimension2D(10, 20), Position2D(10, 20)).overlaps(
        Object2D(Dimension2D(20, 20), Position2D(20, 20))
    )
    assert not Object2D(Dimension2D(10, 20), Position2D(10, 20)).overlaps(
        Object2D(Dimension2D(20, 20), Position2D(21, 20))
    )


def test_object_2d__add() -> None:
    assert Object2D(
        Dimension2D(10, 20),
        Position2D(10, 20),
    ) + (10, 20) == Object2D(Dimension2D(10, 20), Position2D(20, 40))


def test_object_2d__sub() -> None:
    assert Object2D(
        Dimension2D(10, 20),
        Position2D(10, 20),
    ) - (10, 20) == Object2D(Dimension2D(10, 20), Position2D(0, 0))
