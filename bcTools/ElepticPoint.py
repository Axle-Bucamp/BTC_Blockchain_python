from Point import Point


def extended_euclidean_algorithm(a, b):
    """
    Returns (gcd, x, y) s.t. a * x + b * y == gcd
    This function implements the extended Euclidean
    algorithm and runs in O(log b) in the worst case,
    taken from Wikipedia.
    """
    old_r, r = a, b
    old_s, s = 1, 0
    old_t, t = 0, 1
    while r != 0:
        quotient = old_r // r
        old_r, r = r, old_r - quotient * r
        old_s, s = s, old_s - quotient * s
        old_t, t = t, old_t - quotient * t
    return old_r, old_s, old_t


def inv(n, p):
    """ returns modular multiplicate inverse m s.t. (n * m) % p == 1 """
    gcd, x, y = extended_euclidean_algorithm(n, p)  # pylint: disable=unused-variable
    return x % p


class ElepticPoint(Point):

    def __add__(self, other):
        # handle special case of P + 0 = 0 + P = 0
        INF = ElepticPoint(None, None, None)  # special point at "infinity", kind of like a zero

        if self == INF:
            return other
        if other == INF:
            return self
        # handle special case of P + (-P) = 0
        if self.x == other.x and self.y != other.y:
            return INF
        # compute the "slope"
        if self.x == other.x:  # (self.y = other.y is guaranteed too per above check)
            m = (3 * self.x ** 2 + self.curve.a) * inv(2 * self.y, self.curve.p)
        else:
            m = (self.y - other.y) * inv(self.x - other.x, self.curve.p)
        # compute the new point
        rx = (m ** 2 - self.x - other.x) % self.curve.p
        ry = (-(m * (rx - self.x) + self.y)) % self.curve.p
        return ElepticPoint(self.curve, rx, ry)

    def __rmul__(self, k: int):
        assert isinstance(k, int) and k >= 0
        INF = ElepticPoint(None, None, None)  # special point at "infinity", kind of like a zero
        result = INF
        append = self
        while k:
            if k & 1:
                result += append
            append += append
            k >>= 1
        return result


if __name__ == "__main__":
    # if our secret key was the integer 1, then our public key would just be G:
    from Curve import Curve

    bitcoin_curve = Curve(
        p=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F,
        a=0x0000000000000000000000000000000000000000000000000000000000000000,  # a = 0
        b=0x0000000000000000000000000000000000000000000000000000000000000007,  # b = 7
    )

    G = ElepticPoint(
        bitcoin_curve,
        x=0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
        y=0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8,
    )

    sk = 1
    pk = G
    print(f" secret key: {sk}\n public key: {(pk.x, pk.y)}")
    print("Verify the public key is on the curve: ", (pk.y ** 2 - pk.x ** 3 - 7) % bitcoin_curve.p == 0)
    # if it was 2, the public key is G + G:
    sk = 2
    pk = G + G
    print(f" secret key: {sk}\n public key: {(pk.x, pk.y)}")
    print("Verify the public key is on the curve: ", (pk.y ** 2 - pk.x ** 3 - 7) % bitcoin_curve.p == 0)
    # etc.:
    sk = 3
    pk = G + G + G
    print(f" secret key: {sk}\n public key: {(pk.x, pk.y)}")
    print("Verify the public key is on the curve: ", (pk.y ** 2 - pk.x ** 3 - 7) % bitcoin_curve.p == 0)

    print("Rmul test:")
    # "verify" correctness
    print("G == 1 * G:", G == 1 * G)
    print("G + G == 2 * G:", G + G == 2 * G)
    print("G + G + G == 3 * G:", G + G + G == 3 * G)
