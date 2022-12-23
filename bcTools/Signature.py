from __future__ import annotations  # PEP 563: Postponed Evaluation of Annotations

import random
from dataclasses import dataclass  # https://docs.python.org/3/library/dataclasses.html I like these a lot

from ElepticPoint import inv
from Generator import Generator
from sha import sha256
from ElepticPoint import ElepticPoint


@dataclass
class Signature:
    r: int
    s: int

    def encode(self) -> bytes:
        """ return the DER encoding of this signature """

        def dern(n):
            nb = n.to_bytes(32, byteorder='big')
            nb = nb.lstrip(b'\x00')  # strip leading zeros
            nb = (b'\x00' if nb[0] >= 0x80 else b'') + nb  # preprend 0x00 if first byte >= 0x80
            return nb

        rb = dern(self.r)
        sb = dern(self.s)
        content = b''.join([bytes([0x02, len(rb)]), rb, bytes([0x02, len(sb)]), sb])
        frame = b''.join([bytes([0x30, len(content)]), content])
        return frame


def sign(secret_key: int, message: bytes, bitcoin_gen: Generator) -> Signature:

    # the order of the elliptic curve used in bitcoin
    n = bitcoin_gen.n

    # double hash the message and convert to integer
    z = int.from_bytes(sha256(sha256(message)), 'big')

    # generate a new secret/public key pair at random
    sk = random.randrange(1, n)
    P = sk * bitcoin_gen.G

    # calculate the signature
    r = P.x
    s = inv(sk, n) * (z + secret_key * r) % n
    if s > n / 2:
        s = n - s

    sig = Signature(r, s)
    return sig


def verify(public_key: ElepticPoint, message: bytes, sig: Signature) -> bool:
    # just a stub for reference on how a signature would be verified in terms of the API
    # we don't need to verify any signatures to craft a transaction, but we would if we were mining
    pass


if __name__ == "__main__":
    # to do
    pass
