
#!/usr/bin/env python
# -*- coding: utf-8 -*-
from telegram import ReplyKeyboardMarkup
from time import sleep
from threading import Thread
from datetime import datetime

import ethscanio
from database import User, Destination, Wallet, Transaction, Token
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


def update_balance(address, token, is_eth=False, is_usdt=False):
    if is_eth:
        now_balance = ethscanio.get_eth_balance(
            address,
            token=token.name
        )
    else:
        now_balance = ethscanio.get_trc_balance(address)

    token.amount = now_balance
    token.save()


def notify(context, dest, txn, wlt, token='ETH'):
    in_out = '+' if txn.to.lower() == wlt.address.lower() else '-'
    wlt_name = wlt.name if wlt.name else wlt.address
    txt = f"<b>{wlt_name}</b>\n{in_out} {txn.amount} {txn.token}"

    chat_ids = list(set(dest.chat_ids.split(',')))

    for chat_id in chat_ids:
        sent = 0
        while sent < 5:
            try:
                context.bot.send_message(
                    chat_id,
                    txt
                )
                sent = 5
            except Exception as e:
                print(e, 'error waiting 60sec...')
                sleep(60)
                sent += 1
        sleep(1)


def tnx_notifyer(context):
    # return
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

                # try:
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
                            froom=last_txn['from'].lower(),
                            to=last_txn['to'].lower(),
                            amount=amount,
                            token=last_txn['tokenSymbol'],
                            time=datetime.fromtimestamp(
                                int(last_txn['timeStamp']))
                        )
                        txn.save()

                        token = Token.get(
                            (Token.wallet_id == wlt.id) & (
                                Token.name == txn.token)
                        )
                        Thread(target=update_balance, args=(
                            wlt.address, token), kwargs={'is_eth': True}).start()

                        Thread(target=notify, args=(
                            context, dest, txn, wlt)).start()
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
                            froom=last_txn['from'].lower(),
                            to=last_txn['to'].lower(),
                            amount=amount,
                            token=last_txn['token_info']['symbol'],
                            time=datetime.fromtimestamp(
                                int((str(last_txn['block_timestamp']))[:-3]))
                        )
                        txn.save()

                        token = Token.get(
                            (Token.wallet_id == wlt.id) & (
                                Token.name == txn.token)
                        )
                        Thread(target=update_balance,
                               args=(wlt.address, token), kwargs={'is_eth': False}).start()

                        Thread(target=notify, args=(
                            context, dest, txn, wlt)).start()
                # except Exception as e:
                #     print(e)
            sleep(5)


#tnx_notifyer(1)
