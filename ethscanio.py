#!/usr/bin/env python
# -*- coding: utf-8 -*-
from requests import get
import json
from base import evars


def get_eth_balance(address, token='USDT'):
    if token == 'USDT':
        contract = '0xdac17f958d2ee523a2206206994597c13d831ec7'
    else:
        contract = '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48'

    url = 'https://api.etherscan.io/api?module=account&action=tokenbalance'
    url += '&contractaddress=' + contract
    url += '&address=' + address
    url += '&tag=latest&apikey=' + evars['ethscanio_api_key']

    resp = get(url)

    jsn = json.loads(resp.text)
    res = jsn.get('result')
    try:
        return float(res[:-6] + '.' + res[-6:-5])
    except ValueError:
        return 0


def get_trc_balance(address):
    url = "https://apilist.tronscan.org/api/account"
    payload = {
        "address": address,
    }
    res = get(url, params=payload)
    trc20token_balances = json.loads(res.text)["trc20token_balances"]

    for token in trc20token_balances:
        if token['tokenAbbr'] == 'USDT':
            return float(token['balance'][:-6] + '.' + token['balance'][-6:-5])
    return 0


if __name__ == '__main__':
    # '''
    print(
        get_eth_balance(
            '0x5b6ca60084b57cd0b0aad9dfd9e4028038768a03',
            '0xdac17f958d2ee523a2206206994597c13d831ec7'  # usdt
            # '0x39b04dbc4b4302e9c7f84d275755cf042898ceae',
            # '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48'  # usdc
        )
    )
    # '''
    # print(get_trc_balance('TXapQNRb5ZAssLsVDgDTBGEC8XNQPbXMaA'))
