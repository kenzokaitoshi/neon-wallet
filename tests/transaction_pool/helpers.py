"""helpers test module transaction pool"""
import ecdsa
from neon_wallet.transaction.coins.coin_transaction import (
    CoinTransaction as Transaction,
)
from neon_wallet.transaction.coins.tx_in import TxIn
from neon_wallet.transaction.coins.tx_out import TxOut
from tests.helpers_data import tx_out_1


private_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
public_key = private_key.get_verifying_key()

# Convert the public key to a hex string for the address
address = public_key.to_string().hex()


def tx_pool_seeder() -> Transaction:
    """seeder"""
    # Create a transaction input that references this unspent output
    tx_in = TxIn("12345", 0, "")

    # Create a new transaction that contains this transaction entry
    # and an arbitrary transaction output
    _tx = Transaction(
        [tx_in],
        [
            TxOut(
                tx_out_1,
                60,
            )
        ],
    )

    # Sign the transaction entry with the private key and id of
    # the transaction
    tx_in.signature = private_key.sign(bytes.fromhex(_tx.id)).hex()

    return _tx
