"""transaction pool module it will make it possible to manage a set of
    transactions waiting to be included in a node of the transaction network.
    Each node in the network has its own transaction pool, which can vary
    depending on the node's rules and settings."""

import copy
from typing import Any, List

from neon_wallet.transaction.coins.coin_transaction import (
    CoinTransaction as Transaction,
)
from neon_wallet.transaction.coins.transactions import validate_transaction
from neon_wallet.transaction.coins.tx_in import TxIn
from neon_wallet.transaction.coins.unspent_tx_out import UnspentTxOut


class TransactionPool:
    """TransactionPool class"""

    transaction_pool: List[Transaction] = []

    # Define function to obtain the pool of transaction
    def get_transaction_pool(self) -> List[Transaction]:
        """get transaction pool"""
        # Return a deep copy of the transaction pool
        return copy.deepcopy(self.transaction_pool)

    # Define a function to add a transaction to the transaction pool
    def add_to_transaction_pool(
        self, _tx: Transaction, unspent_tx_outs: List[UnspentTxOut]
    ) -> None:
        """add to transactionPool"""
        # Check if transaction is valid with unspent outputs
        if not validate_transaction(_tx, unspent_tx_outs):
            # Throw an exception if the transaction is invalid
            raise ValueError("Trying to add invalid tx to pool")

        # Check if transaction is valid for transaction pool
        if not self.is_valid_tx_for_pool(_tx, self.transaction_pool):
            # Throw an exception if the transaction is invalid for the pool
            raise ValueError("Trying to add invalid tx to pool")

        # Display a message with the transaction added to the pool
        print(f"adding to txPool: {_tx}")

        # Add transaction to transaction pool
        self.transaction_pool.append(_tx)

    def is_valid_tx_for_pool(
        self, _tx: Transaction, at_transaction_pool: List[Transaction]
    ) -> bool:
        """is valid tx for pool"""
        tx_pool_ins: List[TxIn] = self.get_tx_pool_ins(at_transaction_pool)

        def is_equal_tx_out_index(tx_in: TxIn, tx_pool_in: TxIn) -> bool:
            return tx_in.tx_out_index == tx_pool_in.tx_out_index

        def is_equal_tx_out_id(tx_in: TxIn, tx_pool_in: TxIn) -> bool:
            return tx_in.tx_out_id == tx_pool_in.tx_out_id

        # Define a function to check if a transaction input
        # is contained in a list of transaction entries
        def contains_tx_in(tx_ins: List[TxIn], tx_in: TxIn) -> Any:
            # Use the filter function to find the entry of
            # corresponding transaction in the list
            return next(
                filter(
                    lambda tx_pool_in: is_equal_tx_out_index(tx_in, tx_pool_in)
                    and is_equal_tx_out_id(tx_in, tx_pool_in),
                    tx_ins,
                ),
                None,
            )

        for tx_in in _tx.tx_ins:
            if contains_tx_in(tx_pool_ins, tx_in):
                print("txIn already found in the txPool")
                return False

        return True

    # Define a function to get all transaction inputs
    # of a transaction pool
    def get_tx_pool_ins(
        self,
        a_transaction_pool: List[Transaction],
    ) -> List[TxIn]:
        """get transaction PoolIns"""
        # Use list comprehension to extract entries Transaction
        # of each transaction
        return [txIn for tx in a_transaction_pool for txIn in tx.tx_ins]

    # Define a function to check if a transaction input
    # exists in a list of unspent outputs
    def has_tx_in(
        self,
        tx_in: TxIn,
        unspent_tx_outs: List[UnspentTxOut],
    ) -> bool:
        """has tx in"""
        # Use filter function to find unspent output
        # corresponding to transaction input
        found_tx_in = next(
            filter(
                lambda uTxO: uTxO.tx_out_id == tx_in.tx_out_id
                and uTxO.tx_out_index == tx_in.tx_out_index,
                unspent_tx_outs,
            ),
            None,
        )
        # Return True if unspent output exists, False otherwise
        return found_tx_in is not None

    # Define a function to update the transaction pool
    # with unspent outputs
    def update_transaction_pool(
        self,
        unspent_tx_outs: List[UnspentTxOut],
    ) -> None:
        """update transactionPool"""
        # Create an empty list to store invalid transactions
        invalid_txs = []
        # Browse transactions from the transaction pool
        for _tx in self.transaction_pool:
            # Loop through the entries of each transaction
            for tx_in in _tx.tx_ins:
                # Check if input exists in unspent outputs
                if not self.has_tx_in(tx_in, unspent_tx_outs):
                    # Add the transaction to the list of transactions
                    # invalid
                    invalid_txs.append(_tx)
                    # Break out of inner loop
                    break
        # Check if list of invalid transactions is not empty
        if len(invalid_txs) > 0:
            # Display a message with invalid transactions at
            # remove from pool
            error_msg = "removing the following transactions from txPool"
            print(f"{error_msg}: {invalid_txs}")
            # Remove invalid transactions from transaction pool
            self.transaction_pool = [
                tx for tx in self.transaction_pool if tx not in invalid_txs
            ]
