"""module transactions"""
# Define a function that returns the transaction id
# of a transaction
import hashlib
from typing import Any, List

# Import the collections module to count the occurrences of elements
import collections

# Import ecdsa module for ECDSA signing and verification
import ecdsa
from neon_wallet.transaction.coins.coin_transaction import (
    CoinTransaction as Transaction,
)
from neon_wallet.transaction.coins.tx_in import TxIn
from neon_wallet.transaction.coins.tx_out import TxOut
from neon_wallet.transaction.coins.unspent_tx_out import UnspentTxOut

COINBASE_AMOUNT: float = 50


def get_transaction_id(transaction: Transaction) -> str:
    """get transaction id"""
    # Extract list of transaction entries from transaction
    tx_ins = transaction.tx_ins
    # Concatenate the identifiers and indices of the outputs of
    # transaction of transaction entries
    for tx_in in tx_ins:
        tx_ = "".join(tx_in.tx_out_id + str(tx_in.tx_out_index))
    tx_in_content = "".join(tx_)
    print("tx_: ", tx_in_content)
    # Extract list of transaction outputs from transaction
    tx_outs = transaction.tx_outs
    # Concatenate addresses and amounts from transaction outputs
    tx_out_content = "".join(
        [tx_out.address + str(tx_out.amount) for tx_out in tx_outs]
    )

    # Hash content of transaction inputs and outputs
    # with SHA256 and convert it to hex string
    tx_in_out = tx_in_content + tx_out_content
    return hashlib.sha256((tx_in_out).encode()).hexdigest()


# Define a function that commits a transaction based on unspent
# transaction outputs
def validate_transaction(
    transaction: Transaction, a_unspent_tx_outs: List[UnspentTxOut]
) -> bool:
    """validate transaction"""
    # Check if transaction structure is valid
    print("test test: ", is_valid_transaction_structure(transaction))
    if not is_valid_transaction_structure(transaction):
        return False

    # Check if all transaction inputs are valid
    has_valid_tx_ins = all(
        [
            validate_tx_in(txIn, transaction, a_unspent_tx_outs)
            for txIn in transaction.tx_ins
        ]
    )

    if not has_valid_tx_ins:
        print("some of the txIns are invalid in tx: " + transaction.id)
        return False

    # Calculate sum of amounts of transaction inputs
    tx_ins_list = transaction.tx_ins
    total_tx_in_values = sum(
        [get_tx_in_amount(txIn, a_unspent_tx_outs) for txIn in tx_ins_list]
    )

    # Calculate sum of transaction output amounts
    total_tx_out_values = sum([txOut.amount for txOut in transaction.tx_outs])
    # Check if sums are equal
    if total_tx_out_values != total_tx_in_values:
        _id = transaction.id
        print(f"totalTxOutValues != totalTxInValues in tx: {_id}")
        return False

    return True


# Define a function that validates a transaction input against
# unspent transaction outputs
def validate_tx_in(
    tx_in: TxIn,
    transaction: Transaction,
    a_unspent_tx_outs: List[UnspentTxOut],
) -> bool:
    """validate transaction in"""
    # Find the unspent transaction output that
    # matches transaction input
    referenced_utx_out = next(
        (
            uTxO
            for uTxO in a_unspent_tx_outs
            if (uTxO.tx_out_id == tx_in.tx_out_id)
            and (uTxO.tx_out_index == tx_in.tx_out_index)
        ),
        None,
    )
    if referenced_utx_out is None:
        print("referenced txOut not found: " + str(tx_in))
        return False

    # Extract address from unspent transaction output
    address = referenced_utx_out.address
    print("ref address", address)

    return True


# Define a function that checks if the structure of a transaction is valid
def is_valid_transaction_structure(transaction: Transaction) -> bool:
    """check if is valid transaction structure"""
    # Check if transaction id is a string
    if not isinstance(transaction.id, str):
        print("transactionId missing")
        return False

    # Check if transaction inputs are a list
    if not isinstance(transaction.tx_ins, list):
        print("invalid txIns type in transaction")
        return False

    # Check if all transaction inputs have a valid structure
    _tx_ins = transaction.tx_ins
    if not all([is_valid_tx_in_structure(txIn) for txIn in _tx_ins]):
        return False

    # Check if transaction outputs are a list
    if not isinstance(transaction.tx_outs, list):
        print("invalid txOuts type in transaction")
        return False

    # Check if all transaction outputs have a valid structure
    _tx = [is_valid_tx_out_structure(txOut) for txOut in transaction.tx_outs]
    if not all(_tx):
        return False

    return True


def is_valid_tx_in_structure(tx_in: TxIn) -> bool:
    """check if valid tx in structure"""
    if tx_in is None:
        print("txIn is null")
        return False
    elif not isinstance(tx_in.signature, str):
        print("invalid signature type in txIn")
        return False
    elif not isinstance(tx_in.tx_out_id, str):
        print("invalid txOutId type in txIn")
        return False
    elif not isinstance(tx_in.tx_out_index, int):
        print("invalid txOutIndex type in txIn")
        return False
    else:
        return True


def is_valid_tx_out_structure(tx_out: TxOut) -> bool:
    """is valid tx out structure"""
    if tx_out is None:
        print("txOut is null")
        return False
    elif not isinstance(tx_out.address, str):
        print("invalid address type in txOut")
        return False
    elif not is_valid_address(tx_out.address):
        print("invalid TxOut address")
        return False
    elif not isinstance(tx_out.amount, float):
        print("invalid amount type in txOut")
        return False
    else:
        return True


# Define a function that checks if an address is valid
def is_valid_address(address: str) -> bool:
    """is valid address"""
    # Check if address length is 130 characters
    if len(address) != 130:
        print(address)
        print("invalid public key length")
        return False
    # Check if the address contains only hexadecimal characters
    elif not address.isalnum():
        print("public key must contain only hex characters")
        return False
    # Check if the address starts with 04
    elif not address.startswith("04"):
        print("public key must start with 04")
        return False
    return True


# Define a function that returns the amount of a
# transaction input based on the outputs of
# unspent transaction
def get_tx_in_amount(
    tx_in: TxIn,
    a_unspent_tx_outs: List[UnspentTxOut],
) -> float:
    """get transaction Amount in"""
    return float(
        find_unspent_tx_out(
            tx_in.tx_out_id,
            tx_in.tx_out_index,
            a_unspent_tx_outs,
        ).amount
    )


# Define a function that finds transaction output
# unspent which corresponds to an identifier and an index
# transaction
def find_unspent_tx_out(
    transaction_id: str, index: int, a_unspent_tx_outs: List[UnspentTxOut]
) -> Any:
    """find unspent Tx out"""
    return next(
        (
            uTxO
            for uTxO in a_unspent_tx_outs
            if uTxO.tx_out_id == transaction_id and uTxO.tx_out_index == index
        ),
        None,
    )


# Define a function to check if a list of txIns has duplicates
def has_duplicates(tx_ins: List[TxIn]) -> Any:
    """check if txIns list has duplicates"""
    # Create a dictionary that counts the number of times
    # a txIn appears in the list
    groups = collections.Counter(
        txIn.tx_out_id + str(txIn.tx_out_index) for txIn in tx_ins
    )
    # Iterate through the dictionary and show txIns that
    # appear more than once
    for key, value in groups.items():
        if value > 1:
            print("duplicate txIn: " + key)
            return True
    # If no txIn appears more than once, return False
    return False


# Define a function to convert a number to hexadecimal
def to_hex_string(byte_array: List[Any]) -> str:
    """convert to hex"""
    # Define a function to convert a byte array to
    # a hexadecimal string
    # Create an empty list to store hexadecimal characters
    hex_list = []
    # Step through the byte array
    for byte in byte_array:
        # Apply a binary mask to keep only the
        # 8 low bits
        byte = byte & 0xFF
        # Convert byte to hexadecimal and add a zero
        # in front if necessary
        hex_char = hex(byte)[2:].zfill(2)
        # Add hexadecimal character to list
        hex_list.append(hex_char)
    # Join hex characters into a single string
    # and return it
    return "".join(hex_list)


# Define a function to sign a txIn with a key private
# and a list of UnspentTxOuts
def sign_tx_in(
    transaction: Transaction,
    tx_in_index: int,
    private_key: str,
    a_unspent_tx_outs: List[UnspentTxOut],
) -> Any:
    """sign tx in"""
    # Get the txIn to sign
    tx_in = transaction.tx_ins[tx_in_index]

    # Get the id of the transaction to sign
    data_to_sign = transaction.id

    # Find the UnspentTxOut which corresponds to the txIn
    ref_unspent_tx_out = find_unspent_tx_out(
        tx_in.tx_out_id, tx_in.tx_out_index, a_unspent_tx_outs
    )

    # If the UnspentTxOut does not exist, throw an exception
    if ref_unspent_tx_out is None:
        print("could not find referenced txOut")
        raise ValueError("could not find referenced txOut")

    # Get the UnspentTxOut address
    referenced_address = ref_unspent_tx_out.address

    # Verify that the public key derived from the private key
    # corresponds to the address of the UnspentTxOut
    if get_public_key(private_key) != referenced_address:
        print(
            "trying to sign an input with private"
            + " key that does not match the address that is referenced in txIn"
        )
        raise ValueError()

    # Create an ecdsa key from the private key in hexadecimal
    key = ecdsa.SigningKey.from_string(
        bytes.fromhex(private_key), curve=ecdsa.SECP256k1
    )

    # Sign the data with the key and return the signature
    # in hexadecimal
    signature = to_hex_string(key.sign(data_to_sign.encode()))
    return signature


# Define a function to get the public key from
# of the private key
def get_public_key(a_private_key: str) -> Any:
    """get public key"""
    private_key_bytes = bytes.fromhex(a_private_key)

    # Appliquer la fonction de multiplication scalaire
    # sur la courbe secp256k1
    curve = ecdsa.SECP256k1
    private_key_point = ecdsa.util.string_to_number(private_key_bytes)
    public_key_point = curve.generator * private_key_point

    # Convertir les coordonnées x et y en octets
    _x = public_key_point.x()
    _y = public_key_point.y()
    x_bytes = _x.to_bytes(32, "big")
    y_bytes = _y.to_bytes(32, "big")

    # Concaténer les octets de x et y avec le préfixe 04
    prefix = b"\x04"
    public_key_bytes = prefix + x_bytes + y_bytes

    # Convertir les octets de la clé publique en hexadécimal
    return public_key_bytes.hex()


# Define a function to update the list of UnspentTxOuts
# from a list of transactions
def update_unspent_tx_outs(
    a_transactions: List[Transaction],
    a_unspent_tx_outs: List[UnspentTxOut],
) -> List[UnspentTxOut]:
    """update unspent tx outs"""
    # Create a new list of UnspentTxOuts from txOuts
    # of transactions
    new_unspent_tx_outs = []
    for _t in a_transactions:
        for index, tx_out in enumerate(_t.tx_outs):
            new_unspent_tx_outs.append(
                UnspentTxOut(_t.id, index, tx_out.address, tx_out.amount)
            )

    # Create a list of consumed UnspentTxOuts from txIns
    # of transactions
    consumed_tx_outs = []
    for _t in a_transactions:
        for tx_in in _t.tx_ins:
            consumed_tx_outs.append(
                UnspentTxOut(tx_in.tx_out_id, tx_in.tx_out_index, "", 0)
            )

    # Filter the list of existing UnspentTxOuts by removing
    # those that are consumed
    resulting_unspent_tx_outs = []
    for u_txo in a_unspent_tx_outs:
        if not find_unspent_tx_out(
            u_txo.tx_out_id, u_txo.tx_out_index, consumed_tx_outs
        ):
            resulting_unspent_tx_outs.append(u_txo)

    # Add the new UnspentTxOuts to the resulting list
    resulting_unspent_tx_outs.extend(new_unspent_tx_outs)

    return resulting_unspent_tx_outs
