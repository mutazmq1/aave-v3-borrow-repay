from socket import LOCAL_PEERCRED
from brownie import network, config, accounts
from web3 import Web3


FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork", "mainnet-fork-dev", "arbitrum-fork"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = [
    "development",
    "ganache-local",
    "mainnet-fork",
    "arbitrum-fork",
]


def get_account(index=None, id=None):

    if index:
        return accounts[index]

    if id:
        return accounts.load(id)

    active_netowrk = network.show_active()
    if (
        active_netowrk in LOCAL_BLOCKCHAIN_ENVIRONMENTS
        or active_netowrk in FORKED_LOCAL_ENVIRONMENTS
    ):
        return accounts[0]

    return accounts.add(config["wallets"]["from_key"])
