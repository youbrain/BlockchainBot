#!/usr/bin/env python
# -*- coding: utf-8 -*-
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram import ext

import ethscanio
from database import Wallet, Transaction, Token
from base import new_response, txts, keybs, del_msg


@new_response
def wallets_h(update, context, data, user, text, btns):
    # context.user_data['to_del'] = update.message.message_id
    # del_msg(update, context)

    keyb = []
    for wlt in Wallet.select().where(Wallet.owner_id == user.chat_id):
        btn_name = wlt.name if wlt.name else wlt.address[:20]
        keyb.append([
            InlineKeyboardButton(
                text='❌ ' + btn_name,
                callback_data='delwallet_' + str(wlt.id)
            )]
        )

    keyb.append(
        [
            InlineKeyboardButton(
                text=btns,
                callback_data='addwallet'
            ),
            # InlineKeyboardButton(
            #     text=keybs['back'],
            #     callback_data='backtomain'
            # ),
        ]
    )

    if update.callback_query:
        update.callback_query.edit_message_text(
            text, reply_markup=InlineKeyboardMarkup(keyb)
        )
        return -1

    # remove_keyboard(update, context)
    context.bot.send_message(
        update._effective_chat.id,
        text,
        reply_markup=InlineKeyboardMarkup(keyb)
    )
    return -1


@new_response
def getwallet(update, context, data, user, text, btns):
    # show wallet info for future
    wlt = Wallet.get(Wallet.id == data[1])
    txns = Transaction.select().where(Transaction.wallet_id == wlt.id)[:10]
    txns = [f"txn" for txn in txns]

    text = text.format(wlt.name, wlt.address)
    update.callback_query.edit_message_text(text)
    # , reply_markup=InlineKeyboardMarkup(keyb)


@new_response
def delwallet(update, context, data, user, text, btns):
    Wallet.get(Wallet.id == data[1]).delete_instance()
    wallets_h(update, context)
    # wlt.del

# addwallet_ch


@new_response
def addwallet_address(update, context, data, user, text, btns):
    update.callback_query.message.delete()

    m = context.bot.send_message(
        update._effective_chat.id, text,
        reply_markup=ReplyKeyboardMarkup(
            [[keybs['back']]], resize_keyboard=True)
    )
    context.user_data['to_del'] = m.message_id
    return 0


@new_response
def addwallet_name(update, context, data, user, text, btns):
    context.user_data['wallet_address'] = update.message.text

    del_msg(update, context)
    m = context.bot.send_message(
        update._effective_chat.id, text,
        reply_markup=ReplyKeyboardMarkup(btns, resize_keyboard=True)
    )
    context.user_data['to_del'] = m.message_id

    return 1


@new_response
def addwallet_save(update, context, data, user, text, btns):
    if update.message.text == keybs['addwallet_name'][0][0]:
        name = None
    else:
        name = update.message.text

    wlt = Wallet(
        owner_id=user.chat_id,
        name=name,
        address=context.user_data['wallet_address']
    )
    wlt.save()

    Token(
        name='USDC',
        wallet_id=wlt.id
    ).save()

    Token(
        name='USDT',
        wallet_id=wlt.id
    ).save()

    wallets_h(update, context)

    return -1


addwallet_ch = ext.ConversationHandler(
    entry_points=[ext.CallbackQueryHandler(
        addwallet_address, pattern='addwallet')],
    states={
        0: [
            ext.MessageHandler(
                ext.Filters.regex(f"^({keybs['back']})$"),
                wallets_h
            ),
            ext.MessageHandler(ext.Filters.text, addwallet_name)
        ],

        1: [
            ext.MessageHandler(
                ext.Filters.regex(f"^({keybs['back']})$"),
                wallets_h
            ),
            ext.MessageHandler(ext.Filters.text, addwallet_save)
        ],
    },
    fallbacks=[],
    per_message=False,
)


@new_response
def balances_h(update, context, data, user, text, btns):
    wallets = Wallet.select().where(Wallet.owner_id == user.chat_id)
    # adrsses = [wlt.address for wlt in wallets]

    text = ''
    total = 0.0

    for wlt in wallets:
        now_balance_usdt = ethscanio.get_eth_balance(
            wlt.address,
            token='USDT'
        )
        usdt_token = Token.get(
            (Token.name == 'USDT') & (Token.wallet_id == wlt.id)
        )
        if wlt.address.startswith('0x'):
            text += f"<a href='https://etherscan.io/address/{wlt.address}'>{wlt.name if wlt.name else wlt.address}</a>\n"

            now_balance_usdc = ethscanio.get_eth_balance(
                wlt.address,
                token='USDC'
            )
            usdc_token = Token.get(
                (Token.name == 'USDC') & (Token.wallet_id == wlt.id)
            )

            if usdc_token.amount != now_balance_usdc:
                usdc_token.amount = now_balance_usdc
                usdc_token.save()

            if usdt_token.amount != now_balance_usdt:
                usdt_token.amount = now_balance_usdt
                usdt_token.save()

            total += now_balance_usdc
        else:
            text += f"<a href='https://tronscan.org/#/address/{wlt.address}'>{wlt.name if wlt.name else wlt.address}</a>\n"

            now_balance_usdt = ethscanio.get_trc_balance(wlt.address)

            if usdt_token.amount != now_balance_usdt:
                usdt_token.amount = now_balance_usdt
                usdt_token.save()

        text += f"<code>{usdc_token.amount}$ USDC</code>\n"
        text += f"<code>{usdt_token.amount}$ USDT</code>\n\n"

        total += now_balance_usdt

    text += 'TOTAL:  <b>' + str(total) + '</b> $ '

    context.bot.send_message(
        update._effective_chat.id,
        text,
        disable_web_page_preview=True
    )
