from __future__ import annotations  # PEP 563: Postponed Evaluation of Annotations

from dataclasses import dataclass  # https://docs.python.org/3/library/dataclasses.html I like these a lot

from Point import Point


@dataclass
class Generator:
    """
    A generator over a curve: an initial point and the (pre-computed) order
    """
    G: Point  # a generator point on the curve
    n: int  # the order of the generating point, so 0*G = n*G = INF


if __name__ == "__main__":
    from Curve import Curve

    bitcoin_curve = Curve(
        p=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F,
        a=0x0000000000000000000000000000000000000000000000000000000000000000,  # a = 0
        b=0x0000000000000000000000000000000000000000000000000000000000000007,  # b = 7
    )

    G = Point(
        bitcoin_curve,
        x=0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
        y=0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8,
    )

    bitcoin_gen = Generator(
        G=G,
        # the order of G is known and can be mathematically derived
        n=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141,
    )

    # secret_key = random.randrange(1, bitcoin_gen.n) # this is how you _would_ do it
    secret_key = int.from_bytes(b'Andrej is cool :P', 'big')  # this is how I will do it for reproducibility
    assert 1 <= secret_key < bitcoin_gen.n
    print(secret_key)
