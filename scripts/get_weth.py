from scripts.helpful_scripts import get_account
from brownie import interface, config, network
from web3 import Web3

# 0.1 eth
amount = Web3.toWei(0.2, "ether")


def get_weth():
    """
    Minsts WETH by deposting ETH
    """
    account = get_account()
    weth = interface.IWeth(config["networks"][network.show_active()]["weth_token"])
    tx = weth.deposit({"from": account, "value": amount})
    tx.wait(1)
    return tx


def main():
    get_weth()
