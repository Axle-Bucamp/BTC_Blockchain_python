from __future__ import annotations  # PEP 563: Postponed Evaluation of Annotations
from sha import sha256


class Block:
    nouce: int
    hash: str
    timestamp: float
    transactions: list
    verificationTX: list

    def __init__(self, nounce=0, hhash="", timestamp=0, transactions=None):
        self.nounce = nounce
        self.hash = hhash
        self.timestamp = timestamp
        self.transactions = transactions
        self.verificationTX = []

        if not self.transactions:
            self.transactions = []

    def proof_of_work(self, message, difficulty=1, start=0, end=1000, step=0):
        assert difficulty >= 1
        prefix = '0' * difficulty
        for i in range(start, end, step):
            digest = str(sha256(bytes(str(sha256(bytes(message, 'utf-8')).hex()) + str(i), 'utf-8')).hex())
            if digest.startswith(prefix):
                self.nounce = i
                self.hash = digest

    def register_transaction(self):
        for tx in self.verificationTX:
            # verify, add a way to verify tx by consensus via client class vote or something
            # faire une classe à part permettant le consensus de chaque transaction par system de vote
            # ainsi qu'une fonction de vérification (somme, adresse, public_key)
            self.transactions.append(tx)
