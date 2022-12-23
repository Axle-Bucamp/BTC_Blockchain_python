from ElepticPoint import ElepticPoint
from ripemd import ripemd160
from sha import sha256


class PublicKey(ElepticPoint):
    """
    The public key is just a Point on a Curve, but has some additional specific
    encoding / decoding functionality that this class implements.
    """

    @classmethod
    def from_point(cls, pt: ElepticPoint):
        """ promote a Point to be a PublicKey """
        return cls(pt.curve, pt.x, pt.y)

    def encode(self, compressed, hash160=False):
        """ return the SEC bytes encoding of the public key Point """
        # calculate the bytes
        if compressed:
            # (x,y) is very redundant. Because y^2 = x^3 + 7,
            # we can just encode x, and then y = +/- sqrt(x^3 + 7),
            # so we need one more bit to encode whether it was the + or the -
            # but because this is modular arithmetic there is no +/-, instead
            # it can be shown that one y will always be even and the other odd.
            prefix = b'\x02' if self.y % 2 == 0 else b'\x03'
            pkb = prefix + self.x.to_bytes(32, 'big')
        else:
            pkb = b'\x04' + self.x.to_bytes(32, 'big') + self.y.to_bytes(32, 'big')
        # hash if desired
        return ripemd160(sha256(pkb)) if hash160 else pkb

    def address(self, net: str, compressed: bool) -> str:
        """ return the associated bitcoin address for this public key as string """
        # encode the public key into bytes and hash to get the payload
        pkb_hash = self.encode(compressed=compressed, hash160=True)
        # add version byte (0x00 for Main Network, or 0x6f for Test Network)
        version = {'main': b'\x00', 'test': b'\x6f'}
        ver_pkb_hash = version[net] + pkb_hash
        # calculate the checksum
        checksum = sha256(sha256(ver_pkb_hash))[:4]
        # append to form the full 25-byte binary Bitcoin Address
        byte_address = ver_pkb_hash + checksum
        # finally b58 encode the result
        b58check_address = b58encode(byte_address)
        return b58check_address


def b58encode(b: bytes) -> str:
    alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    assert len(b) == 25  # version is 1 byte, pkb_hash 20 bytes, checksum 4 bytes
    n = int.from_bytes(b, 'big')
    chars = []
    while n:
        n, i = divmod(n, 58)
        chars.append(alphabet[i])
    # special case handle the leading 0 bytes... ¯\_(ツ)_/¯
    num_leading_zeros = len(b) - len(b.lstrip(b'\x00'))
    res = num_leading_zeros * alphabet[0] + ''.join(reversed(chars))
    return res


if __name__ == "__main__":
    from Curve import Curve
    from ElepticPoint import ElepticPoint

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

    lol_secret_key = 1
    lol_public_key = lol_secret_key * G
    lol_address = PublicKey.from_point(lol_public_key).address(net='test', compressed=True)
    print(lol_address)
