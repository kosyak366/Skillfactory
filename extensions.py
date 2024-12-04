import requests
import json
from config import keys

class APIException (Exception):
    pass

class CryptoConverter:
    @staticmethod
    def get_price(base, quote, amount):

        if quote == base:
            raise APIException(f'Невозможно конвертировать валюту ({base}) саму в себя..')

        try:
            val_quote = keys[quote]
        except KeyError:
            raise APIException(f'Не удалось обработать {quote}')

        try:
            val_base = keys[base]
        except KeyError:
            raise APIException(f'Не удалось обработать {base}')

        try:
            amount = float(amount)
        except ValueError:
            raise APIException(f'Не удалось обработать {amount}')

        r = requests.get(f'https://min-api.cryptocompare.com/data/price?fsym={val_quote}&tsyms={val_base}')
        price = json.loads(r.content)[val_base]
        total = float(price * amount)
        return total, price