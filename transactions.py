#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
from base import new_response
from database import Transaction, Wallet


@new_response
def transc_h(update, context, data, user, text, btns):
    a3days_ago = datetime.datetime.now() - datetime.timedelta(days=3)

    wlts = Wallet.select().where(Wallet.owner_id == user.chat_id)
    wlts = [wlt.id for wlt in wlts]

    txns = Transaction.select().where(
        (Transaction.wallet_id << wlts) & (Transaction.time > a3days_ago)
    ).order_by(Transaction.time)

    txt = '<code>'

    for txn in txns:
        wlt = Wallet.get(Wallet.id == txn.wallet_id)

        time = txn.time.strftime('%d.%m.%Y %H:%M')
        in_out = '+' if txn.to.lower() == wlt.address.lower() else '-'

        txt += f"{in_out} {txn.amount} {txn.token} {time}\n"

    txt += '</code>'

    context.bot.send_message(user.chat_id, txt)
