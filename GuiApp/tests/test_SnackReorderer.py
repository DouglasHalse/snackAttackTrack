import pytest

from database import SnackData
from snackReorderer import SnackReorderer

# Fixtures are counted as redefine-outer-name
# pylint: disable=redefined-outer-name


@pytest.fixture
def snacks():
    return [
        SnackData(
            snackId=1,
            snackName="snack1",
            quantity=1,
            imageID="image1",
            pricePerItem=1.0,
        ),
        SnackData(
            snackId=2,
            snackName="snack2",
            quantity=2,
            imageID="image2",
            pricePerItem=2.0,
        ),
        SnackData(
            snackId=3,
            snackName="snack3",
            quantity=3,
            imageID="image3",
            pricePerItem=3.0,
        ),
    ]


def test_reorder_snacks_complete_guide(snacks):
    guide_list = ["snack3", "snack1", "snack2"]
    SnackReorderer.reorder_snacks_based_on_guide_list(snacks, guide_list)
    assert [snack.snackName for snack in snacks] == ["snack3", "snack1", "snack2"]


def test_reorder_snacks_partial_guide(snacks):
    guide_list = ["snack2", "snack3"]
    SnackReorderer.reorder_snacks_based_on_guide_list(snacks, guide_list)
    assert [snack.snackName for snack in snacks] == ["snack2", "snack3", "snack1"]


def test_reorder_snacks_extra_items_in_guide(snacks):
    guide_list = ["snack3", "snack4", "snack1"]
    SnackReorderer.reorder_snacks_based_on_guide_list(snacks, guide_list)
    assert [snack.snackName for snack in snacks] == ["snack3", "snack1", "snack2"]


def test_reorder_snacks_empty_guide(snacks):
    guide_list = []
    SnackReorderer.reorder_snacks_based_on_guide_list(snacks, guide_list)
    assert [snack.snackName for snack in snacks] == ["snack1", "snack2", "snack3"]


def test_reorder_snacks_empty_snacks_list():
    snacks = []
    guide_list = ["snack1", "snack2"]
    SnackReorderer.reorder_snacks_based_on_guide_list(snacks, guide_list)
    assert not snacks
