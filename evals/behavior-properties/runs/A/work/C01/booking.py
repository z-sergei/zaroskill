from dataclasses import dataclass

@dataclass(frozen=True)
class Receipt:
    customer: str
    accepted: bool

class TicketDesk:
    def __init__(self):
        self.owner = None
        self._receipts = {}

    def reserve(self, customer, request_id):
        if request_id in self._receipts:
            receipt = self._receipts[request_id]
            if receipt.customer != customer:
                raise ValueError("request_id belongs to another customer")
            return receipt
        accepted = self.owner is None
        if accepted:
            self.owner = customer
        receipt = Receipt(customer, accepted)
        self._receipts[request_id] = receipt
        return receipt
