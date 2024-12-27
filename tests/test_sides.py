from led_matrix_enclosure.sides import Side, SideDict


def test_side__is_horizontal() -> None:
    assert Side.LEFT.is_horizontal is True
    assert Side.RIGHT.is_horizontal is True
    assert Side.FRONT.is_horizontal is False
    assert Side.BACK.is_horizontal is False


def test_side__is_start() -> None:
    assert Side.LEFT.is_start is True
    assert Side.RIGHT.is_start is False
    assert Side.FRONT.is_start is True
    assert Side.BACK.is_start is False


def test_side__opposite() -> None:
    assert Side.LEFT.opposite is Side.RIGHT
    assert Side.RIGHT.opposite is Side.LEFT
    assert Side.FRONT.opposite is Side.BACK
    assert Side.BACK.opposite is Side.FRONT


def test_side__str() -> None:
    assert str(Side.LEFT) == "left"
    assert str(Side.RIGHT) == "right"
    assert str(Side.FRONT) == "front"
    assert str(Side.BACK) == "back"


def test_side_dict__default() -> None:
    assert SideDict(left=False) == {
        Side.FRONT: True,
        Side.BACK: True,
        Side.LEFT: False,
        Side.RIGHT: True,
    }


def test_side_dict__default__true() -> None:
    assert SideDict(default=True) == {
        Side.FRONT: True,
        Side.BACK: True,
        Side.LEFT: True,
        Side.RIGHT: True,
    }


def test_side_dict__default__false() -> None:
    assert SideDict(default=False) == {
        Side.FRONT: False,
        Side.BACK: False,
        Side.LEFT: False,
        Side.RIGHT: False,
    }


def test_side_dict__invert() -> None:
    assert ~SideDict(right=False) == {
        Side.FRONT: False,
        Side.BACK: False,
        Side.LEFT: False,
        Side.RIGHT: True,
    }


def test_side_dict__str() -> None:
    assert str(SideDict(left=False)) == "front back right"
    assert str(SideDict(left=True)) == "front back left right"
    assert str(SideDict(left=True, default=False)) == "left"


def test_side_dict__get_adjacents() -> None:
    assert SideDict().get_adjacents(Side.LEFT) == (Side.BACK, Side.FRONT)
    assert SideDict().get_adjacents(Side.RIGHT) == (Side.BACK, Side.FRONT)
    assert SideDict().get_adjacents(Side.FRONT) == (Side.LEFT, Side.RIGHT)
    assert SideDict().get_adjacents(Side.BACK) == (Side.LEFT, Side.RIGHT)
    assert SideDict(left=False, front=False).get_adjacents(Side.LEFT) == (Side.BACK,)
    assert SideDict(back=False, front=False).get_adjacents(Side.LEFT) == ()
    assert SideDict(default=False).get_adjacents(Side.LEFT) == ()
    assert SideDict(default=False).get_adjacents(Side.RIGHT) == ()
    assert SideDict(default=False).get_adjacents(Side.FRONT) == ()
    assert SideDict(default=False).get_adjacents(Side.BACK) == ()


def test_side_dict__has_opposite() -> None:
    assert SideDict().has_opposite(Side.LEFT) is True
    assert SideDict().has_opposite(Side.RIGHT) is True
    assert SideDict().has_opposite(Side.FRONT) is True
    assert SideDict().has_opposite(Side.BACK) is True
    assert SideDict(default=False).has_opposite(Side.LEFT) is False
    assert SideDict(default=False).has_opposite(Side.RIGHT) is False
    assert SideDict(default=False).has_opposite(Side.FRONT) is False
    assert SideDict(default=False).has_opposite(Side.BACK) is False


def test_side_dict__horizontal() -> None:
    assert SideDict().horizontal == (Side.LEFT, Side.RIGHT)
    assert SideDict(left=False).horizontal == (Side.RIGHT,)
    assert SideDict(right=False).horizontal == (Side.LEFT,)
    assert SideDict(default=False).horizontal == ()


def test_side_dict__vertical() -> None:
    assert SideDict().vertical == (Side.FRONT, Side.BACK)
    assert SideDict(front=False).vertical == (Side.BACK,)
    assert SideDict(back=False).vertical == (Side.FRONT,)
    assert SideDict(default=False).vertical == ()


def test_side_dict__add() -> None:
    assert SideDict(default=False) + Side.LEFT == SideDict(left=True, default=False)
    assert SideDict(default=False) + Side.RIGHT == SideDict(right=True, default=False)
    assert SideDict(default=False) + Side.FRONT == SideDict(front=True, default=False)
    assert SideDict(default=False) + Side.BACK == SideDict(back=True, default=False)

    side_dict = SideDict(default=False)
    side_dict += Side.LEFT
    assert side_dict == SideDict(left=True, default=False)


def test_side_dict__sub() -> None:
    assert SideDict(default=True) - Side.LEFT == SideDict(left=False, default=True)
    assert SideDict(default=True) - Side.RIGHT == SideDict(right=False, default=True)
    assert SideDict(default=True) - Side.FRONT == SideDict(front=False, default=True)
    assert SideDict(default=True) - Side.BACK == SideDict(back=False, default=True)

    side_dict = SideDict(default=True)
    side_dict -= Side.LEFT
    assert side_dict == SideDict(left=False, default=True)
