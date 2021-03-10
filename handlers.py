#!/usr/bin/env python
# -*- coding: utf-8 -*-
from telegram import ReplyKeyboardMarkup

from database import User, Destination
from base import new_response, txts, keybs


def start(update, context):
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

    to_main(update, context)


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
        dest.chat_ids += str(update.message.chat.id)
        dest.save()

    context.bot.send_message(
        update._effective_chat.id,
        txts['new_chat_added'].format(update.message.from_user.first_name)
    )


def tnx_notifyer(context):
    print(11111111111111)
    # for dest in Destination.select():

    # context.bot.send_message(chat_id='@examplechannel',
    #                          text='A single message with 30s delay')
