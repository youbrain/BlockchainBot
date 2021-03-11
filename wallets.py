#!/usr/bin/env python
# -*- coding: utf-8 -*-
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram import ext

from database import Wallet, Transaction, Token
from base import new_response, keybs, del_msg


@new_response
def wallets_h(update, context, data, user, text, btns):
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
            )
        ]
    )

    if update.callback_query:
        update.callback_query.edit_message_text(
            text, reply_markup=InlineKeyboardMarkup(keyb)
        )
        return -1

    context.bot.send_message(
        update._effective_chat.id,
        text,
        reply_markup=InlineKeyboardMarkup(keyb)
    )
    return -1


@new_response
def m_keyband_wall(update, context, data, user, text, btns):

    context.bot.send_message(
        update._effective_chat.id, '_',
        reply_markup=ReplyKeyboardMarkup(
            keybs['to_main'],
            resize_keyboard=True
        )
    )
    wallets_h(update, context)
    return -1


@new_response
def getwallet(update, context, data, user, text, btns):
    # show wallet info for future
    wlt = Wallet.get(Wallet.id == data[1])
    txns = Transaction.select().where(Transaction.wallet_id == wlt.id)[:10]
    txns = [f"txn" for txn in txns]

    text = text.format(wlt.name, wlt.address)
    update.callback_query.edit_message_text(text)


@new_response
def delwallet(update, context, data, user, text, btns):
    Wallet.get(Wallet.id == data[1]).delete_instance()
    wallets_h(update, context)

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
    if update.message.text == keybs['addwallet_name'][0][1]:
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

    context.bot.send_message(
        update._effective_chat.id, '_',
        reply_markup=ReplyKeyboardMarkup(
            keybs['to_main'],
            resize_keyboard=True
        )
    )

    wallets_h(update, context)

    return -1


addwallet_ch = ext.ConversationHandler(
    entry_points=[ext.CallbackQueryHandler(
        addwallet_address, pattern='addwallet')],
    states={
        0: [
            ext.MessageHandler(
                ext.Filters.regex(f"^({keybs['back']})$"),
                m_keyband_wall
            ),
            ext.MessageHandler(ext.Filters.text, addwallet_name)
        ],

        1: [
            ext.MessageHandler(
                ext.Filters.regex(f"^({keybs['back']})$"),
                m_keyband_wall
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

    text = ''
    total_usdt = 0.0
    total_usdc = 0.0

    for wlt in wallets:
        text += '<b>' + (wlt.name if wlt.name else wlt.address) + '</b>'

        usdt_token = Token.get(
            (Token.name == 'USDT') & (Token.wallet_id == wlt.id)
        )
        usdc_token = Token.get(
            (Token.name == 'USDC') & (Token.wallet_id == wlt.id)
        )

        if usdc_token.amount:
            text += f"\n<code>{usdc_token.amount} USDC</code>"
            total_usdc += usdc_token.amount

        if usdt_token.amount:
            text += f"\n<code>{usdt_token.amount} USDT</code>"
            total_usdt += usdt_token.amount

        if not usdc_token.amount and not usdt_token.amount:
            text += f"\n<code>Error</code>"

        text += '\n\n'

    total_usdc = "{:,}".format(total_usdc)
    total_usdc = "{:,}".format(total_usdt)
    text += f"\nTOTAL:\n{total_usdc} USDC   {total_usdt} USDT"

    context.bot.send_message(
        update._effective_chat.id,
        text,
        disable_web_page_preview=True
    )
