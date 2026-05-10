from decimal import ROUND_HALF_UP, Decimal
from datetime import datetime
from enum import Enum


class TransactionType(Enum):
    PURCHASE = "PURCHASE"
    TOP_UP = "TOP_UP"
    EDIT = "EDIT"
    GAMBLE = "GAMBLE"


class LostSnackReason(Enum):
    STOLEN = 1
    EXPIRED = 2
    DAMAGED = 3


def transactionTypeToPresentableString(transactionType: TransactionType) -> str:
    if transactionType == TransactionType.PURCHASE:
        return "Purchase"
    if transactionType == TransactionType.TOP_UP:
        return "Top-up"
    if transactionType == TransactionType.EDIT:
        return "Edit"
    if transactionType == TransactionType.GAMBLE:
        return "Gamble"
    return "Unknown"


TWODECIMALS = Decimal("0.00")


class Credits(Decimal):
    """A custom Decimal that always stays at 2 decimal places."""

    def __new__(cls, value):
        quantized = Decimal(value).quantize(TWODECIMALS, rounding=ROUND_HALF_UP)
        return super().__new__(cls, str(quantized))

    def _as_credits(self, value):
        return Credits(value)

    def __add__(self, other):
        return self._as_credits(Decimal(self) + Decimal(other))

    def __radd__(self, other):
        return self._as_credits(Decimal(other) + Decimal(self))

    def __sub__(self, other):
        return self._as_credits(Decimal(self) - Decimal(other))

    def __rsub__(self, other):
        return self._as_credits(Decimal(other) - Decimal(self))

    def __mul__(self, other):
        return self._as_credits(Decimal(self) * Decimal(other))

    def __rmul__(self, other):
        return self._as_credits(Decimal(other) * Decimal(self))

    def __truediv__(self, other):
        result = (Decimal(self) / Decimal(other)).quantize(
            TWODECIMALS, rounding=ROUND_HALF_UP
        )
        return Credits(result)

    def __rtruediv__(self, other):
        result = (Decimal(other) / Decimal(self)).quantize(
            TWODECIMALS, rounding=ROUND_HALF_UP
        )
        return Credits(result)

    def __neg__(self):
        return self._as_credits(-Decimal(self))

    def __pos__(self):
        return self._as_credits(+Decimal(self))

    def __abs__(self):
        return self._as_credits(abs(Decimal(self)))

    def __floordiv__(self, other):
        result = (Decimal(self) // Decimal(other)).quantize(
            TWODECIMALS, rounding=ROUND_HALF_UP
        )
        return Credits(result)

    def __rfloordiv__(self, other):
        result = (Decimal(other) // Decimal(self)).quantize(
            TWODECIMALS, rounding=ROUND_HALF_UP
        )
        return Credits(result)

    def __mod__(self, other):
        result = (Decimal(self) % Decimal(other)).quantize(
            TWODECIMALS, rounding=ROUND_HALF_UP
        )
        return Credits(result)

    def __rmod__(self, other):
        result = (Decimal(other) % Decimal(self)).quantize(
            TWODECIMALS, rounding=ROUND_HALF_UP
        )
        return Credits(result)

    def to_hundredths(self) -> int:
        return int((Decimal(self) * 100).to_integral_value(rounding=ROUND_HALF_UP))

    @classmethod
    def from_hundredths(cls, hundredths: int) -> "Credits":
        return cls(hundredths / 100)


class UserData:
    def __init__(self, patronId, firstName, lastName, employeeID, totalCredits):
        assert isinstance(patronId, int)
        assert isinstance(firstName, str)
        assert isinstance(lastName, str)
        assert isinstance(employeeID, str)
        assert isinstance(totalCredits, Credits)
        self.patronId: int = patronId
        self.firstName: str = firstName
        self.lastName: str = lastName
        self.employeeID: str = employeeID
        self.totalCredits: Credits = totalCredits


class SnackData:
    def __init__(
        self,
        snackId: int,
        snackName: str,
        quantity: int,
        imageID: str,
        pricePerItem: Credits,
    ):
        assert isinstance(snackId, int)
        assert isinstance(snackName, str)
        assert isinstance(quantity, int)
        assert isinstance(imageID, str)
        assert isinstance(pricePerItem, Credits)
        self.snackId: int = snackId
        self.snackName: str = snackName
        self.quantity: int = quantity
        self.imageID: str = imageID
        self.pricePerItem: Credits = pricePerItem


class HistoryData:
    def __init__(
        self,
        transactionId: int,
        transactionType: TransactionType,
        transactionDate: datetime,
        amountBeforeTransaction: Credits,
        amountAfterTransaction: Credits,
        transactionItems: list[SnackData],
    ):
        assert isinstance(transactionId, int)
        assert isinstance(transactionType, TransactionType)
        assert isinstance(transactionDate, datetime)
        assert isinstance(amountBeforeTransaction, Credits)
        assert isinstance(amountAfterTransaction, Credits)
        assert isinstance(transactionItems, list)
        self.transactionId: int = transactionId
        self.transactionType: TransactionType = transactionType
        self.transactionDate: datetime = transactionDate
        self.amountBeforeTransaction: Credits = amountBeforeTransaction
        self.amountAfterTransaction: Credits = amountAfterTransaction
        self.transactionItems: list[SnackData] = transactionItems
