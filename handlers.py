#!/usr/bin/env python
# -*- coding: utf-8 -*-
from telegram import ReplyKeyboardMarkup
from time import sleep

import ethscanio
from database import User, Destination, Wallet, Transaction
from base import new_response, txts  # , keybs


def start(update, context):
    try:
        user = User.get_or_none(User.chat_id == update.message.chat.id)
        if not user:
            # txt = update.message.text.split()
            # if len(txt) > 1:
            #     referal_code = update.message.text.replace('/start ', '')
            user = User.create(
                chat_id=update.message.chat.id,
                first_name=update.message.chat.first_name,
                last_name=update.message.chat.last_name,
                username=update.message.chat.username,
                language=update.effective_user.language_code
            )
            user.save()
            Destination(user_id=user.chat_id,
                        chat_ids=str(user.chat_id)).save()

        to_main(update, context)
    except:
        pass


@new_response
def to_main(update, context, data, user, text, btns):
    if update.callback_query:
        update.callback_query.message.delete()
    context.bot.send_message(
        update._effective_chat.id,
        text,
        reply_markup=ReplyKeyboardMarkup(btns, resize_keyboard=True)
    )


@new_response
def help_h(update, context, data, user, text, btns):
    context.bot.send_message(
        update._effective_chat.id,
        text
    )


@new_response
def to_do_h(update, context, data, user, text, btns):
    context.bot.send_message(
        update._effective_chat.id,
        text
    )


# @new_response
def new_chat_added(update, context):
    dest = Destination.get_or_none(
        Destination.user_id == update.message.from_user.id
    )
    if not dest:
        Destination(
            user_id=update.message.from_user.id,
            chat_ids=update.message.chat.id
        ).save()
    else:
        dest.chat_ids += ',' + str(update.message.chat.id)
        dest.save()

    context.bot.send_message(
        update._effective_chat.id,
        txts['new_chat_added'].format(update.message.from_user.first_name)
    )


def notify(context, dest, txn, wlt):
    in_out = 'IN' if txn.to == wlt.address else 'OUT'
    wlt_name = wlt.name if wlt.name else wlt.address
    txt = f"{wlt_name}\n<b>{in_out}</b> {txn.amount} {txn.token}"

    chat_ids = list(set(dest.chat_ids.split(',')))

    for chat_id in chat_ids:
        try:
            context.bot.send_message(
                chat_id,
                txt
            )
            sleep(1)
        except:
            print('notify error waiting 60sec...')
            sleep(60)


def tnx_notifyer(context):
    while True:
        for dest in Destination.select():
            wlts = Wallet.select().where(Wallet.owner_id == dest.user_id)

            for wlt in wlts:
                prob_last_txn = Transaction.select().where(
                    Transaction.wallet_id == wlt.id
                ).order_by(Transaction.id.desc())

                prob_last_hash = False
                if prob_last_txn:
                    prob_last_hash = prob_last_txn.get().hash

                if wlt.address.startswith('0x'):
                    last_txn = ethscanio.get_last_txn_eth(wlt.address)
                    if prob_last_hash != last_txn['hash']:
                        amount = float(
                            last_txn['value'][:-6] + '.' +
                            last_txn['value'][-6:-5]
                        )
                        txn = Transaction(
                            wallet_id=wlt.id,
                            hash=last_txn['hash'],
                            froom=last_txn['from'],
                            to=last_txn['to'],
                            amount=amount,
                            token=last_txn['tokenSymbol'],
                            # direction='IN' if last_txn['to'] == wlt.address else 'OUT'
                        )
                        txn.save()
                        notify(context, dest.user_id, txn, wlt)
                        # send
                else:
                    last_txn = ethscanio.get_last_txn_trc(wlt.address)
                    if prob_last_hash != last_txn['transaction_id']:
                        amount = float(
                            last_txn['value'][:-6] + '.' +
                            last_txn['value'][-6:-5]
                        )
                        txn = Transaction(
                            wallet_id=wlt.id,
                            hash=last_txn['transaction_id'],
                            froom=last_txn['from'],
                            to=last_txn['to'],
                            amount=amount,
                            token=last_txn['token_info']['symbol'],
                            # direction='IN' if last_txn['to'] == wlt.address else 'OUT'
                        )
                        txn.save()
                        notify(context, dest, txn, wlt)
            sleep(5)
        sleep(5)
