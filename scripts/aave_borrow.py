from re import L
from scripts.helpful_scripts import get_account
from scripts.get_weth import get_weth
from brownie import interface, config, network
from web3 import Web3

# 0.1 eth
amount = Web3.toWei(0.1, "ether")


def main():
    account = get_account()
    erc20_address = config["networks"][network.show_active()]["weth_token"]
    if network.show_active() == "arbitrum-fork":
        get_weth()

    aave_pool = get_pool()
    approve_erc20(amount, aave_pool.address, erc20_address, account)
    print("Depositing to Aave...")
    tx = aave_pool.supply(erc20_address, amount, account.address, 0, {"from": account})
    tx.wait(1)
    print(f"Deposited {amount} eth!")
    collateral, borrowable_eth, total_debt = get_brrowable_data(aave_pool, account)

    import pdb

    pdb.set_trace()

    dai_eth_price = resolve_price_feed()
    amount_to_borrow = (1 / dai_eth_price) * (borrowable_eth * 0.95)
    print(f"Amount to borrow {amount_to_borrow} DAI")
    dai_token = config["networks"][network.show_active()]["dai_token"]

    borrow_tx = aave_pool.borrow(
        dai_token,
        Web3.toWei(amount_to_borrow, "ether"),
        2,
        0,
        account.address,
        {"from": account.address},
    )
    borrow_tx.wait(1)
    print(f"Borrowed {amount_to_borrow}")
    get_brrowable_data(aave_pool, account)

    repay_all(amount, aave_pool, account)


def repay_all(amount, pool, account):
    dai_token = config["networks"][network.show_active()]["dai_token"]
    approve_erc20(Web3.toWei(amount, "ether"), pool, dai_token, account)
    repay_tx = pool.repay(dai_token, amount, 2, account.address, {"from": account})
    repay_tx.wait(1)
    print("Repaid!")


# Arbitrum doesn't have dai/eth price feed.
def resolve_price_feed():
    if network.show_active() == "mainnet-fork":
        latest_price = get_asset_price(
            config["networks"][network.show_active()]["dai_eth_price_feed"]
        )
        converted_latest_price = Web3.fromWei(latest_price, "ether")
        print(f"The DAI/ETH price is {converted_latest_price}")
        return float(converted_latest_price)
    else:  # Arbitrum in my case
        dai_usd_price_feed = config["networks"][network.show_active()][
            "dai_usd_price_feed"
        ]
        eth_usd_price_feed = config["networks"][network.show_active()][
            "eth_usd_price_feed"
        ]

        dai_usd_price = get_asset_price(dai_usd_price_feed)
        eth_usd_price = get_asset_price(eth_usd_price_feed)
        latest_price = float(dai_usd_price) / float(eth_usd_price)
        print(f"The DAI/ETH price is {latest_price}")
        return latest_price


def get_asset_price(price_feed_address):
    price_feed = interface.AggregatorV3Interface(price_feed_address)
    latest_price = price_feed.latestRoundData()[1]
    return latest_price


def approve_erc20(amount, spender, erc20_address, account):
    print("Approving ERC20 token...")
    erc20 = interface.IERC20(erc20_address)
    tx = erc20.approve(spender, amount, {"from": account})
    tx.wait(1)
    print("Approved!")
    return tx


def get_brrowable_data(pool, account):
    (
        totalCollateralBase,
        totalDebtBase,
        availableBorrowsBase,
        currentLiquidationThreshold,
        ltv,
        healthFactor,
    ) = pool.getUserAccountData(account.address)

    # Ave v3 pulls the decimals from chainlink
    """
    availableBorrowsBase = Web3.fromWei(availableBorrowsBase, "ether")
    totalCollateralBase = Web3.fromWei(totalCollateralBase, "ether")
    totalDebtBase = Web3.fromWei(totalDebtBase, "ether")
    """

    print(f"You have {totalCollateralBase} worth of Eth deposited.")
    print(f"You can borrow {availableBorrowsBase} worth of Eth.")
    print(f"You have {totalDebtBase} worth of Eth borrowed.")

    return (
        float(totalCollateralBase),
        float(availableBorrowsBase),
        float(totalDebtBase),
    )


def get_pool():
    aave_pool_addressess_provider_address = config["networks"][network.show_active()][
        "aave_pool_addressess_provider"
    ]
    aave_pool_addressess_provider = interface.IPoolAddressesProvider(
        aave_pool_addressess_provider_address
    )
    aave_pool_address = aave_pool_addressess_provider.getPool()

    aave_pool = interface.IPool(aave_pool_address)

    return aave_pool
