#!/usr/bin/env python
# -*- coding: utf-8 -*-
import peewee
from datetime import datetime
from os import environ as evars


db = peewee.PostgresqlDatabase(
    'cryptobot',
    user='cryptobot',
    password='crypto123rgrgF@',
    host='localhost',
    port=5432,
    autocommit=True,
    autorollback=True
)
'''
db = peewee.MySQLDatabase('blockchainbot', user='bot', password=evars['mysql_pswd'],
                          host='127.0.0.1', port=3306)

db_file = 'development.db' if bool(evars['debug']) else 'production.db'
db = peewee.SqliteDatabase(db_file)
'''


class User(peewee.Model):
    id = peewee.AutoField()
    chat_id = peewee.IntegerField()

    first_name = peewee.CharField()
    last_name = peewee.CharField(null=True)
    username = peewee.CharField(null=True, unique=True)
    language = peewee.CharField(null=True)
    start_time = peewee.DateTimeField(default=datetime.now())

    is_banned = peewee.BooleanField(default=False)

    class Meta:
        database = db
        db_table = 'users'


class Wallet(peewee.Model):
    id = peewee.AutoField()
    owner_id = peewee.IntegerField()

    address = peewee.CharField()
    balance = peewee.FloatField(null=True)
    name = peewee.CharField(null=True)

    class Meta:
        database = db
        db_table = 'wallets'


class Token(peewee.Model):
    id = peewee.AutoField()
    wallet_id = peewee.IntegerField()

    name = peewee.CharField()
    amount = peewee.FloatField(default=0.0)

    is_hide = peewee.BooleanField(default=False)

    class Meta:
        database = db
        db_table = 'tokens'


class Transaction(peewee.Model):
    id = peewee.AutoField()
    wallet_id = peewee.IntegerField()

    hash = peewee.CharField()
    froom = peewee.CharField()
    to = peewee.CharField()
    amount = peewee.FloatField(default=0.0)
    token = peewee.CharField()
    time = peewee.DateTimeField(default=datetime.now())

    class Meta:
        database = db
        db_table = 'transactions'


class Destination(peewee.Model):
    id = peewee.AutoField()

    user_id = peewee.CharField()
    chat_ids = peewee.TextField(null=True)

    class Meta:
        database = db
        db_table = 'destinations'


Destination.create_table()
User.create_table()
Wallet.create_table()
Token.create_table()
Transaction.create_table()
