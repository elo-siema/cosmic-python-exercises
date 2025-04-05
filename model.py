from dataclasses import dataclass
from datetime import date

class AllocationError(ValueError):
    pass

@dataclass(frozen=True)
class OrderLine:
    sku: str
    qty: int

@dataclass(frozen=True)
class Order:
    order_ref: str
    lines: list[OrderLine]

class Batch:
    ref: str
    sku: str
    available_qty: int
    eta: date | None

    def __init__(self, ref: str, sku: str, qty: int, eta: date | None):
        self.ref = ref
        self.sku = sku
        self.available_qty = qty
        self.eta = eta

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Batch):
            return False
        return self.ref == value.ref

    def __hash__(self) -> int:
        return hash(self.ref)

    def __gt__(self, value: object) -> bool:
        if not isinstance(value, Batch):
            raise TypeError
        if self.eta is None:
            return False
        if value.eta is None:
            return True
        return self.eta > value.eta

    @property
    def in_warehouse(self):
        return self.eta is None

    def can_allocate(self, line: OrderLine):
        return self.sku == line.sku and self.available_qty >= line.qty

    def allocate(self, line: OrderLine):
        if self.can_allocate(line):
            self.available_qty -= line.qty
        else:
            raise AllocationError(f"Could not allocate {line.sku}")

def allocate(line: OrderLine, batches: list[Batch]):
    filtered = [batch for batch in batches if batch.can_allocate(line)]
    sorted_batches = sorted(filtered)

    if not sorted_batches:
        raise AllocationError(f"Could not allocate {line.sku}")

    sorted_batches[0].allocate(line)
