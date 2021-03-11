#!/usr/bin/env python
# -*- coding: utf-8 -*-
from base import keybs
from handlers import (
    start,
    help_h,
    to_main,
    to_do_h,
)
from wallets import (
    wallets_h,
    getwallet,
    addwallet_ch,
    delwallet,
    balances_h,
)

from transactions import transc_h

#
command_handlers = {
    # 'command': handler_func,
    'start': start,
    'help': help_h
}

conversation_handlers = [
    # test_ch
    addwallet_ch
]

button_handlers = {
    # 'btn_name': handler_func,
    # 'show help': help_h,
    keybs['to_main'][0][0]: wallets_h,
    keybs['to_main'][0][1]: balances_h,
    keybs['to_main'][1][0]: transc_h,
    keybs['to_main'][1][1]: help_h,

    keybs['back']: to_main
}

callback_handlers = {
    # 'pattern': handler_func,
    'getwallet_': getwallet,
    'delwallet_': delwallet,
    'backtomain': to_main
}
