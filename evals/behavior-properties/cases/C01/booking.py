from dataclasses import dataclass

@dataclass(frozen=True)
class Receipt:
    customer: str
    accepted: bool

class TicketDesk:
    def __init__(self):
        self.owner = None

    def reserve(self, customer, request_id):
        raise NotImplementedError('reservation is not implemented')
