from __future__ import print_function
import time
import re
import base64
import datetime
import json
# import gmail
from api import purchase_token
from db import db_connect
from models import Customer, Message
import mailer

API_STATUS_KEY = 'status'
API_STATUS_SUCCESS = 'SUCCESS'

# API_STATUS_KEY = 'id'
# API_STATUS_SUCCESS = 1

regex_lines = []
with open('trans_type_regex.properties', 'r') as regex_file:
    regex_lines = regex_file.readlines()


def process_payment(conn, results, c):
    print('Process payment: ', results)
    print('1. Record payment')
    trans_id = results['trans_id']
    amount = results['amount'].replace(',', '')
    payer_account = results['payer_account']
    trans_date = results['trans_date'].rstrip()
    trans_date = datetime.datetime.strptime(trans_date, '%d/%m/%y %H:%M').isoformat(' ')
    balance = results['balance'].replace(',', '')
    channel = results['channel']
    receipt_no = results['receipt_no']
    sql = f"insert into npm_payments(trans_id, amount, payer_account, trans_date, balance, channel, receipt_no, email, msisdn) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    print(sql)
    params = (trans_id, amount, payer_account, trans_date, balance, channel, receipt_no, c.email, c.msisdn)
    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
        print(f'Rows interted: {cursor.rowcount}')
        if cursor.rowcount:
            resp = purchase_token(trans_id, amount, payer_account, c.email, c.msisdn)
            print(resp)
            if API_STATUS_KEY in resp and resp[API_STATUS_KEY] == API_STATUS_SUCCESS:
                sql = f"update npm_payments set status='Completed' where trans_id='{trans_id}' "
                cursor.execute(sql)
                conn.commit()
            return True
    except Exception as e:
        print("DB Error: ", e)
    finally:
        if cursor:
            cursor.close()
    return False


def parse_mail(conn, msg_text, c, dry_run=False):
    try:
        for regex_line in regex_lines:
            key, regex = tuple(regex_line.split('='))
            test = re.findall(regex.strip(), msg_text.strip())
            match = test[0] if test else None
            if not match:
                continue
            pattern = ('prefix', 'amount', 'payer_account', 'payer_name', 'trans_id', 'trans_date', 'balance')
            if key == 'tigopesa.en':
                pattern = ('prefix', 'amount', 'payer_account', 'payer_name', 'trans_date', 'trans_id', 'balance')
            if key.startswith('iop.receiving'):
                pattern = ('prefix', 'balance', 'amount', 'channel', 'payer_account',
                           'payer_name', 'trans_id', 'receipt_no', 'trans_date')
            print(f'Match: {match}')
            if len(match) == len(pattern):
                result = dict(zip(pattern, match))
                result['msg_key'] = key
                if key.startswith('tigopesa'):
                    result['channel'] = 'Tigo'
                    result['receipt_no'] = 'ON-NET'
                print(result)
                if not dry_run:
                    print(f'Recording payment...')
                    return process_payment(conn, result, c)
                return True
            else:
                print(f'No match => {key}|{regex}|{msg_text}')
    except Exception as e:
        print(f'Error: {e}')
    print(f'No match for all available regex: {msg_text}')
    return False


def mail_processor_thread():
    while True:
        with db_connect() as conn:
            print('Reading mail...')
            customers = Customer.list(conn)
            for c in customers:
                messages = Message.new_messages(conn, c.email)
                for message in messages:
                    msg_text = message['body']
                    if msg_text and parse_mail(conn, msg_text, c):
                        print('Successfully parsed the mail')
                        Message.set_processed(conn, message['id'], 1)
                    else:
                        print('Failed to parse the mail')
                        Message.set_processed(conn, message['id'], -1)
            # break
        time.sleep(15)


def mail_reader_thread():
    while True:
        with db_connect() as conn:
            def save_mail(dest, msg_id, msg):
                sql = f"insert into npm_messages(message_id, email, body) values (%s, %s,  %s)"
                print(sql)
                params = (msg_id, dest, msg)
                cursor = None
                try:
                    cursor = conn.cursor()
                    cursor.execute(sql, params)
                    conn.commit()
                    print(f'Rows interted: {cursor.rowcount}')
                    if cursor.rowcount:
                        return True
                except Exception as e:
                    print("DB Error: ", e)
                finally:
                    if cursor:
                        cursor.close()
                return False
            mailer.mail_connect(save_mail)
        time.sleep(15)
