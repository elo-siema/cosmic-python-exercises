from datetime import date, timedelta
import pytest
from model import Batch, OrderLine, allocate

# from model import ...

today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)


def test_allocating_to_a_batch_reduces_the_available_quantity():
    batch = Batch("batch-001", "SMALL-FORK", 20, eta=today)
    line = OrderLine("SMALL-FORK", 2)
    batch.allocate(line)

    assert batch.available_qty == 18


def test_can_allocate_if_available_greater_than_required():
    batch = Batch("batch-001", "SMALL-FORK", 20, eta=today)
    line = OrderLine("SMALL-FORK", 2)

    assert batch.can_allocate(line)


def test_cannot_allocate_if_available_smaller_than_required():
    batch = Batch("batch-001", "SMALL-FORK", 20, eta=today)
    line = OrderLine("SMALL-FORK", 21)

    assert not batch.can_allocate(line)


def test_can_allocate_if_available_equal_to_required():
    batch = Batch("batch-001", "SMALL-FORK", 20, eta=today)
    line = OrderLine("SMALL-FORK", 20)

    assert batch.can_allocate(line)


def test_prefers_warehouse_batches_to_shipments():
    warehouse_batch = Batch("batch-001", "SMALL-FORK", 20, eta=None)
    shipment_batch = Batch("batch-002", "SMALL-FORK", 20, eta=tomorrow)

    line = OrderLine("SMALL-FORK", 2)

    allocate(line, [warehouse_batch, shipment_batch])

    assert warehouse_batch.available_qty == 18
    assert shipment_batch.available_qty == 20


def test_prefers_earlier_batches():
    earliest = Batch("batch-001", "SMALL-FORK", 20, eta=today)
    middle = Batch("batch-002", "SMALL-FORK", 20, eta=tomorrow)
    latest = Batch("batch-003", "SMALL-FORK", 20, eta=later)

    line = OrderLine("SMALL-FORK", 2)

    allocate(line, [earliest, middle, latest])

    assert earliest.available_qty == 18
    assert latest.available_qty == 20
    assert middle.available_qty == 20
