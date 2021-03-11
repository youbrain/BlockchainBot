#!/usr/bin/env python
# -*- coding: utf-8 -*-

from base import new_response
from database import Transaction, Wallet


@new_response
def transc_h(update, context, data, user, text, btns):
    wlts = Wallet.select().where(Wallet.owner_id == user.chat_id)
    wlts = [wlt.id for wlt in wlts]

    txns = Transaction.select().where(
        Transaction.wallet_id << wlts
    ).order_by(Transaction.time).limit(10)

    txt = '<code>'

    for txn in txns:
        wlt = Wallet.get(Wallet.id == txn.wallet_id)

        time = txn.time.strftime('%d.%m.%Y')
        in_out = '+' if txn.to == wlt.address else '-'

        txt += f"{in_out} {txn.amount} {txn.token} {time}\n"

    txt += '</code>'

    context.bot.send_message(user.chat_id, txt)
