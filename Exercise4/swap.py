import time
import alice
import bob

# 作者：Max Spero

# 在这个任务中，我们将实现两方（Alice和Bob）之间的跨链原子交换。
# Alice在BTC Testnet3（标准比特币测试网）上拥有比特币。
# Bob在BCY Testnet（Blockcypher的比特币测试网）上拥有比特币。
# 他们希望安全地交换各自的币，这不能通过简单的交易来实现，因为它们位于不同的区块链上。

# 这种方法也适用于其他加密货币和代币，例如交换n个比特币和m个莱特币。

# 这里的想法是围绕一个只有一方（Alice）知道的秘密x设置交易。在这些交易中，只有H(x)将被公开，x将保持秘密。

# 交易将以这样的方式设置，一旦x被揭示，双方都可以赎回对方发送的币。

# 如果x从未被揭示，双方都可以安全地收回他们的原始币，无需对方的帮助。

# BTC Testnet3

# Alice ----> UTXO ----> Bob（带有x）
#               |
#               |
#               V
#             Alice（48小时后）

# BCY Testnet

# Bob ----> UTXO ----> Alice（带有x）
#               |
#               |
#               V
#              Bob（24小时后）

# 针对您的地址配置

# TODO：填写所有这些字段

alice_txid_to_spend = "69da08c74b53204fbb7e27dfb0b63c3cf16405e4cf7a08dd149b7a138a4c0be9"
alice_utxo_index = 1
alice_amount_to_send = 0.001

bob_txid_to_spend = "018e196ba39da688aaa7a417de29c44941745dc6fe68e00b9b655cd065906f6c"
bob_utxo_index = 1
bob_amount_to_send = 0.0009

# 获取每个区块链的当前区块高度（用于锁定时间）并将其放入swap.py：

# 从以下网址获取BTC Testnet3的当前区块高度（'height'参数）：curl https://api.blockcypher.com/v1/btc/test3
btc_test3_chain_height = 2539195

# 从以下网址获取BCY Testnet的当前区块高度（'height'参数）：curl https://api.blockcypher.com/v1/bcy/test
bcy_test_chain_height = 1074553

# Alice/Bob必须等待多长时间才能收回他们的币
# alice_locktime必须大于bob_locktime
alice_locktime = 5
bob_locktime = 3

tx_fee = 0.0001

broadcast_transactions = True
alice_redeems = True

# 读取以下函数。

# 这里无需实现任何内容，但它概述了Alice和Bob如何进行跨链原子交换。
# 您将运行swap.py来测试您的代码。

def atomic_swap(broadcast_transactions=False, alice_redeems=True):
    # Alice公开她秘密x的哈希值，但不公开秘密本身
    hash_of_secret = alice.hash_of_secret()

    # Alice创建一个由Bob（带有x）或Bob和Alice一起赎回的交易
    alice_swap_tx, alice_swap_scriptPubKey = alice.alice_swap_tx(
        alice_txid_to_spend,
        alice_utxo_index,
        alice_amount_to_send - tx_fee,
    )

    # Alice创建一个时间锁交易以将币退还给自己
    alice_return_coins_tx = alice.return_coins_tx(
        alice_amount_to_send - (2 * tx_fee),
        alice_swap_tx,
        btc_test3_chain_height + alice_locktime,
        alice_swap_scriptPubKey,
    )

    # Alice要求Bob签署她的交易
    bob_signature_BTC = bob.sign_BTC(alice_return_coins_tx, alice_swap_scriptPubKey)

    # Alice仅在Bob签署此交易后才广播第一笔交易
    if broadcast_transactions:
        alice.broadcast_BTC(alice_swap_tx)

    # 同样的情况发生，角色互换
    bob_swap_tx, bob_swap_scriptPubKey = bob.bob_swap_tx(
        bob_txid_to_spend,
        bob_utxo_index,
        bob_amount_to_send - tx_fee,
        hash_of_secret,
    )
    bob_return_coins_tx = bob.return_coins_tx(
        bob_amount_to_send - (2 * tx_fee),
        bob_swap_tx,
        bcy_test_chain_height + bob_locktime,
    )

    alice_signature_BCY = alice.sign_BCY(bob_return_coins_tx, bob_swap_scriptPubKey)

    if broadcast_transactions:
        bob.broadcast_BCY(bob_swap_tx)

    if broadcast_transactions:
        print('休眠20分钟以等待交易确认...')
        time.sleep(60 * 20)

    if alice_redeems:
        # Alice赎回她的币，公开x（它现在在区块链上）
        alice_redeem_tx, alice_secret_x = alice.redeem_swap(
            bob_amount_to_send - (2 * tx_fee),
            bob_swap_tx,
            bob_swap_scriptPubKey,
        )
        if broadcast_transactions:
            alice.broadcast_BCY(alice_redeem_tx)

        # 一旦x被揭示，Bob也可以赎回他的币
        bob_redeem_tx = bob.redeem_swap(
            alice_amount_to_send - (2 * tx_fee),
            alice_swap_tx,
            alice_swap_scriptPubKey,
            alice_secret_x,
        )
        if broadcast_transactions:
            bob.broadcast_BTC(bob_redeem_tx)
    else:
        # Bob和Alice可以在指定的时间后收回他们的原始币
        completed_bob_return_tx = bob.complete_return_tx(
            bob_return_coins_tx,
            bob_swap_scriptPubKey,
            alice_signature_BCY,
        )
        completed_alice_return_tx = alice.complete_return_tx(
            alice_return_coins_tx,
            alice_swap_scriptPubKey,
            bob_signature_BTC,
        )
        if broadcast_transactions:
            print('休眠bob_locktime区块以等待锁定时间...')
            time.sleep(10 * 60 * bob_locktime)
            bob.broadcast_BCY(completed_bob_return_tx)

            print('休眠alice_locktime区块以等待锁定时间...')
            time.sleep(10 * 60 * max(alice_locktime - bob_locktime, 0))
            alice.broadcast_BTC(completed_alice_return_tx)

if __name__ == '__main__':
    atomic_swap(broadcast_transactions, alice_redeems)
