from __future__ import annotations  # PEP 563: Postponed Evaluation of Annotations
import time  # necessary componant
from cryptos import *


class Blockchain:
    # coder en receiver et simuler un reseau P2P
    blocks: Block

    # the way to record the first transaction
    def __init__(self):
        self.blocks = Block(nounce=0, hhash="", timestamp=time.time(), transactions=[])
        self.current_difficulty = 1
        self.prefix = "0" * self.current_difficulty

    def record(self, details, timestamp=None):
        timestamp = timestamp or time.time()
        prev_hash = ""
        if self.blocks.transactions:
            prev_hash = self.blocks.transactions[-1][2]

        new_hash = bhash(timestamp, details, prev_hash)
        self.blocks.transactions.append((timestamp, details, new_hash))

    def add_new_block(self, block):
        # check nounce and hash
        if block.hash.startswith(self.prefix)\
                and str(sha256(bytes(str(sha256(bytes(self.blocks.hash, 'utf-8')).hex())
                                     + str(block.nounce), 'utf-8')).hex()) == block.hash:
            self.blocks = block


def verify_bc(blockchain):
    prev = blockchain.blocks.transactions[0]
    for transaction in blockchain.blocks.transactions[1:]:
        new_hash = bhash(transaction[0], transaction[1], prev[2])
        if transaction[2] != new_hash:
            return False
        prev = transaction
        # add a wallet check part
    return True


def bhash(timestamp, details, prev_hash):
    # token = json.dumps([timestamp, details, prev_hash])
    bstring = str(timestamp) + str(details) + str(prev_hash)
    return sha256(bytes(bstring, 'utf-8')).hex()


if __name__ == "__main__":
    from bcTools.Curve import Curve
    from bcTools.ElepticPoint import ElepticPoint
    from bcTools.PublicKey import PublicKey
    from bcTools.Signature import *
    from bcTools.Tx import *
    from bcTools.sha import sha256
    from bcTools.Block import Block

    secret_key = int.from_bytes(b"ceci est une private key", 'big')  # this is how I will do it for reproducibility
    # secp256k1 uses a = 0, b = 7, so we're dealing with the curve y^2 = x^3 + 7 (mod p)
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

    # efficiently calculate our actual public key!
    bitcoin_gen = Generator(
        G=G,
        # the order of G is known and can be mathematically derived
        n=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141,
    )

    assert 1 <= secret_key < bitcoin_gen.n
    public_key = secret_key * G
    print(f"x: {public_key.x}\ny: {public_key.y}")
    print("Verify the public key is on the curve: ", (public_key.y ** 2 - public_key.x ** 3 - 7) % bitcoin_curve.p == 0)

    address = PublicKey.from_point(public_key).address(net='test', compressed=True)
    print("Our first Bitcoin identity:")
    print("1. secret key: ", secret_key)
    print("2. public key: ", (public_key.x, public_key.y))
    print("3. Bitcoin address: ", address)

    print("Hexadecimal version: ", PublicKey.from_point(public_key).encode(compressed=True, hash160=True).hex())

    secret_key2 = int.from_bytes(b"Andrej's Super Secret 2nd Wallet",
                                 'big')  # or just random.randrange(1, bitcoin_gen.n)
    assert 1 <= secret_key2 < bitcoin_gen.n  # check it's valid
    public_key2 = secret_key2 * G
    address2 = PublicKey.from_point(public_key2).address(net='test', compressed=True)

    print("Our second Bitcoin identity:")
    print("1. secret key: ", secret_key2)
    print("2. public key: ", (public_key2.x, public_key2.y))
    print("3. Bitcoin address: ", address2)

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

    # the first output will go to our 2nd wallet
    out1_pkb_hash = PublicKey.from_point(public_key2).encode(compressed=True, hash160=True)
    out1_script = Script([118, 169, out1_pkb_hash, 136, 172])  # OP_DUP, OP_HASH160, <hash>, OP_EQUALVERIFY, OP_CHECKSIG
    print("from 1 to 2 TX", out1_script.encode().hex())

    # the second output will go back to us
    out2_pkb_hash = PublicKey.from_point(public_key).encode(compressed=True, hash160=True)
    out2_script = Script([118, 169, out2_pkb_hash, 136, 172])
    print("from 2 to 1 Tx", out2_script.encode().hex())

    # save the key to Tx
    tx_out1.script_pubkey = out1_script
    tx_out2.script_pubkey = out2_script

    # using TX class instead
    tx = Tx(
        version=1,
        tx_ins=[tx_in],
        tx_outs=[tx_out1, tx_out2],
    )

    print(tx)
    source_script = Script(
        [118, 169, out2_pkb_hash, 136, 172])  # OP_DUP, OP_HASH160, <hash>, OP_EQUALVERIFY, OP_CHECKSIG
    print("recall out2_pkb_hash is just raw bytes of the hash of public_key: ", out2_pkb_hash.hex())
    print(source_script.encode().hex())  # we can get the bytes of the script_pubkey now

    # monkey patch this into the input of the transaction we are trying sign and construct
    tx_in.prev_tx_script_pubkey = source_script

    # get the "message" we need to digitally sign!!
    message = tx.encode(sig_index=0)
    print("encrypted message: ", message.hex())

    random.seed(int.from_bytes(sha256(message), 'big'))  # see note below
    sig = sign(secret_key, message, bitcoin_gen)
    print("Signature du contrat: ", sig)
    sig_bytes = sig.encode()
    print("Signature to byte:", sig_bytes.hex())

    # Append 1 (= SIGHASH_ALL), indicating this DER signature we created encoded "ALL" of the tx (by far most common)
    sig_bytes_and_type = sig_bytes + b'\x01'

    # Encode the public key into bytes. Notice we use hash160=False so we are revealing the full public key to
    # Blockchain
    pubkey_bytes = PublicKey.from_point(public_key).encode(compressed=True, hash160=False)

    # Create a lightweight Script that just encodes those two things!
    script_sig = Script([sig_bytes_and_type, pubkey_bytes])
    tx_in.script_sig = script_sig

    print("id de la transaction: ", tx.id())  # once this transaction goes through, this will be its id

    # todo: ajout d'une gestion de block
    # implémentation d'une preuve ou d'une simulation de preuve
    # implementation d'une blockchain simulant le P2P (broadcast le dernier block etc)

    print("_" * 10)
    first_blockchain = Blockchain()
    print(tx.encode())
    first_blockchain.record(details=tx.encode())
    first_blockchain.record(details=tx.encode())
    first_blockchain.record(details=tx.encode())
    print(first_blockchain.blocks.transactions)

    print("blockchain transactions have valide hash:", verify_bc(first_blockchain))

    print("actual nounce is", first_blockchain.blocks.nounce)
    second_block = Block()
    second_block.proof_of_work(first_blockchain.blocks.hash, difficulty=1, start=0, end=1000, step=1)
    if second_block.nounce != 0:
        first_blockchain.add_new_block(second_block)

    print("actual nounce is", first_blockchain.blocks.nounce)
    print("actual hash is", first_blockchain.blocks.hash)

    print("decoding a transaction", deserialize(tx.encode().hex()))
    # implementer les outils de la bibliothèque : https://github.com/primal100/pybitcointools
    # de manière à le convertir dans notre format ou travailler sur pybitcointools directement

