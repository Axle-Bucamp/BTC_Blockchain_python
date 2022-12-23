from __future__ import annotations  # PEP 563: Postponed Evaluation of Annotations

from ctypes import Union
from dataclasses import dataclass  # https://docs.python.org/3/library/dataclasses.html I like these a lot

from sha import sha256


@dataclass
class TxIn:
    prev_tx: bytes  # prev transaction ID: hash256 of prev tx contents
    prev_index: int  # UTXO output index in the transaction
    script_sig: Script = None  # unlocking script, Script class coming a bit later below
    sequence: int = 0xffffffff  # originally intended for "high frequency trades", with locktime

    def encode(self, script_override=None):
        out = []
        out += [self.prev_tx[::-1]]  # little endian vs big endian encodings... sigh
        out += [encode_int(self.prev_index, 4)]

        if script_override is None:
            # None = just use the actual script
            out += [self.script_sig.encode()]
        elif script_override is True:
            # True = override the script with the script_pubkey of the associated input
            out += [self.prev_tx_script_pubkey.encode()]
        elif script_override is False:
            # False = override with an empty script
            out += [Script([]).encode()]
        else:
            raise ValueError("script_override must be one of None|True|False")

        out += [encode_int(self.sequence, 4)]
        return b''.join(out)


@dataclass
class TxOut:
    amount: int  # in units of satoshi (1e-8 of a bitcoin)
    script_pubkey: Script = None  # locking script

    def encode(self):
        out = []
        out += [encode_int(self.amount, 8)]
        out += [self.script_pubkey.encode()]
        return b''.join(out)


def encode_int(i, nbytes, encoding='little'):
    """ encode integer i into nbytes bytes using a given byte ordering """
    return i.to_bytes(nbytes, encoding)


def encode_varint(i):
    """ encode a (possibly but rarely large) integer into bytes with a super simple compression scheme """
    if i < 0xfd:
        return bytes([i])
    elif i < 0x10000:
        return b'\xfd' + encode_int(i, 2)
    elif i < 0x100000000:
        return b'\xfe' + encode_int(i, 4)
    elif i < 0x10000000000000000:
        return b'\xff' + encode_int(i, 8)
    else:
        raise ValueError("integer too large: %d" % (i, ))


@dataclass
class Script:
    cmds: list[Union[int, bytes]]

    def encode(self):
        out = []
        for cmd in self.cmds:
            if isinstance(cmd, int):
                # an int is just an opcode, encode as a single byte
                out += [encode_int(cmd, 1)]
            elif isinstance(cmd, bytes):
                # bytes represent an element, encode its length and then content
                length = len(cmd)
                assert length < 75  # any longer than this requires a bit of tedious handling that we'll skip here
                out += [encode_int(length, 1), cmd]

        ret = b''.join(out)
        return encode_varint(len(ret)) + ret


@dataclass
class Tx:
    version: int
    tx_ins: list[TxIn]
    tx_outs: list[TxOut]
    locktime: int = 0

    def encode(self, sig_index=-1) -> bytes:
        """
        Encode this transaction as bytes.
        If sig_index is given then return the modified transaction
        encoding of this tx with respect to the single input index.
        This result then constitutes the "message" that gets signed
        by the aspiring transactor of this input.
        """
        out = []
        # encode metadata
        out += [encode_int(self.version, 4)]
        # encode inputs
        out += [encode_varint(len(self.tx_ins))]
        if sig_index == -1:
            # we are just serializing a fully formed transaction
            out += [tx_in.encode() for tx_in in self.tx_ins]
        else:
            # used when crafting digital signature for a specific input index
            out += [tx_in.encode(script_override=(sig_index == i))
                    for i, tx_in in enumerate(self.tx_ins)]
        # encode outputs
        out += [encode_varint(len(self.tx_outs))]
        out += [tx_out.encode() for tx_out in self.tx_outs]
        # encode... other metadata
        out += [encode_int(self.locktime, 4)]
        out += [encode_int(1, 4) if sig_index != -1 else b'']  # 1 = SIGHASH_ALL
        return b''.join(out)

    def id(self) -> str:
        return sha256(sha256(self.encode()))[::-1].hex()  # little/big endian conventions require byte order swap


if __name__ == "__main__":
    tx_in = TxIn(
        prev_tx=bytes.fromhex('46325085c89fb98a4b7ceee44eac9b955f09e1ddc86d8dad3dfdcba46b4d36b2'),
        prev_index=1,
        script_sig=None,  # this field will have the digital signature, to be inserted later
    )

    tx_out1 = TxOut(
        amount=50000  # we will send this 50,000 sat to our target wallet
    )
    tx_out2 = TxOut(
        amount=47500  # back to us
    )

    print(tx_in)
    print(tx_out1)
    print(tx_out2)
