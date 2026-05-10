from GuiApp.app_types import Credits


def test_creation_and_str():
    c = Credits(12.345)
    assert isinstance(c, Credits)
    assert str(c) == "12.35" or float(c) == 12.35


def test_addition_and_subtraction():
    a = Credits("1.23")
    b = Credits("2.34")
    assert a + b == Credits("3.57")
    assert b - a == Credits("1.11")


def test_multiplication_and_division():
    a = Credits("10.00")
    b = Credits("3.00")
    assert a * b == Credits("30.00")
    assert a / b == Credits("3.33")


def test_rounding_on_division():
    assert Credits(37) / 3 == Credits("12.33")


def test_sum_returns_credits():
    values = [Credits("1.10"), Credits("2.20")]
    total = sum(values, Credits(0))
    assert isinstance(total, Credits)
    assert total == Credits("3.30")


def test_to_and_from_hundredths():
    c = Credits("12.34")
    assert c.to_hundredths() == 1234
    assert Credits.from_hundredths(1234) == Credits("12.34")


def test_negation():
    assert -Credits("5.50") == Credits("-5.50")
    assert -Credits("-3.00") == Credits("3.00")
    assert isinstance(-Credits("1.00"), Credits)


def test_pos():
    assert +Credits("7.77") == Credits("7.77")
    assert isinstance(+Credits("1.00"), Credits)


def test_abs():
    assert abs(Credits("-4.00")) == Credits("4.00")
    assert abs(Credits("4.00")) == Credits("4.00")
    assert isinstance(abs(Credits("-1.00")), Credits)


def test_floordiv():
    assert Credits("10.00") // Credits("3.00") == Credits("3.00")
    assert Credits("5.50") // Credits("2.00") == Credits("2.00")
    assert isinstance(Credits("10.00") // Credits("3.00"), Credits)


def test_rfloordiv():
    assert 10 // Credits("3.00") == Credits("3.00")
    assert isinstance(10 // Credits("3.00"), Credits)


def test_mod():
    assert Credits("10.00") % Credits("3.00") == Credits("1.00")
    assert Credits("10.50") % Credits("3.00") == Credits("1.50")
    assert isinstance(Credits("10.00") % Credits("3.00"), Credits)


def test_rmod():
    assert 10 % Credits("3.00") == Credits("1.00")
    assert isinstance(10 % Credits("3.00"), Credits)
