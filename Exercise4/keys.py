from bitcoin import SelectParams
from bitcoin.wallet import CBitcoinSecret, P2PKHBitcoinAddress
from bitcoin.core import x

SelectParams('testnet')

######################################################################
# 
# TODO: Fill this in with address secret key for BTC testnet3
#
# Create address in Base58 with keygen.py
# Send coins at https://coinfaucet.eu/en/btc-testnet/

# Only to be imported by alice.py
# Alice should have coins!!
alice_secret_key_BTC = CBitcoinSecret(
    'cSxgWbnZfP45no9MWbgVgdQd2P9N5HMBrYWaTBFXKoJYwcDtwRzp')

# Only to be imported by bob.py
bob_secret_key_BTC = CBitcoinSecret(
    'cU9GryQaTNxQWEH6rQf9pMhMqXnhPUfaK1hkuJXmNUTjxdzffxdC')

######################################################################
#
# TODO: Fill this in with address secret key for BCY testnet
#
# Create address in hex with
# curl -X POST https://api.blockcypher.com/v1/bcy/test/addrs?token=$YOURTOKEN
#
# Send coins with
# curl -d '{"address": "BCY_ADDRESS", "amount": 1000000}' https://api.blockcypher.com/v1/bcy/test/faucet?token=<YOURTOKEN>

# Only to be imported by alice.py
alice_secret_key_BCY = CBitcoinSecret.from_secret_bytes(
    x('4ad708479216e51c6e26a665873945f3568d4955ce7eb1375e26a001d4e9120e'))

# Only to be imported by bob.py
# Bob should have coins!!
bob_secret_key_BCY = CBitcoinSecret.from_secret_bytes(
    x('fc11c46fb5ff17f0209f353b37edb2abdf93140e3bfaba19b94b5d86e363239b'))

# Can be imported by alice.py or bob.py
alice_public_key_BTC = alice_secret_key_BTC.pub
alice_address_BTC = P2PKHBitcoinAddress.from_pubkey(alice_public_key_BTC)

bob_public_key_BTC = bob_secret_key_BTC.pub
bob_address_BTC = P2PKHBitcoinAddress.from_pubkey(bob_public_key_BTC)

alice_public_key_BCY = alice_secret_key_BCY.pub
alice_address_BCY = P2PKHBitcoinAddress.from_pubkey(alice_public_key_BCY)

bob_public_key_BCY = bob_secret_key_BCY.pub
bob_address_BCY = P2PKHBitcoinAddress.from_pubkey(bob_public_key_BCY)
