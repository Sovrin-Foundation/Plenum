import pytest

from collections import OrderedDict
from plenum.common.messages.fields import NonNegativeNumberField, \
    LedgerIdField, IterableField, NonEmptyStringField, \
    TimestampField, HexField
from plenum.common.types import PrePrepare

EXPECTED_ORDERED_FIELDS = OrderedDict([
    ("instId", NonNegativeNumberField),
    ("viewNo", NonNegativeNumberField),
    ("ppSeqNo", NonNegativeNumberField),
    ("ppTime", TimestampField),
    ("reqIdr", IterableField),
    ("discarded", NonNegativeNumberField),
    ("digest", NonEmptyStringField),
    ("ledgerId", LedgerIdField),
    ("stateRootHash", HexField),
    ("txnRootHash", HexField),
])


def test_hash_expected_type():
    assert PrePrepare.typename == "PREPREPARE"


def test_has_expected_fields():
    actual_field_names = OrderedDict(PrePrepare.schema).keys()
    assert actual_field_names == EXPECTED_ORDERED_FIELDS.keys()


def test_has_expected_validators():
    schema = dict(PrePrepare.schema)
    for field, validator in EXPECTED_ORDERED_FIELDS.items():
        assert isinstance(schema[field], validator)
