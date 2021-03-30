#!/bin/bash
export bot_token=1640746210:AAFoP4vpOYOyeM5H8HWj6hu61z-XuBlQfHw
export debug=True
export ethscanio_api_key=VY4A2HFJX28YJRZ77GX85X22SE7Q9DG8MV
export dev_chat_id=383253401
export mysql_pswd=crypto123rgrgF@

cd /root/BlockchainBot
source env/bin/activate
sleep 10
python3 main.py #& disown
