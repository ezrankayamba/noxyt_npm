import requests
import json

URL = 'https://my-json-server.typicode.com/ezrankayamba/fake-api/tokens'


def purchase_token(trans_id, amount, payer_account, email, msisdn):
    payload = {'trans_id': trans_id, 'amount': amount, 'payer_account': payer_account, 'email': email, 'msisdn': msisdn}
    r = requests.post(URL, json=payload)
    return r.json()


if __name__ == "__main__":
    trans_id = '123444'
    amount = 1000
    payer_account = '6363636366'
    resp = purchase_token(trans_id, amount, payer_account)
    print(resp)
