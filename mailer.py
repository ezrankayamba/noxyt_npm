from imaplib import IMAP4_SSL
import email
import quopri
import configparser


def read_msg(M, msg_id):
    _, data = M.fetch(msg_id, '(UID BODY[HEADER.FIELDS (Delivered-To)])')
    _, data2 = M.fetch(msg_id, '(UID BODY[TEXT])')
    dest = email.message_from_string(data[0][1].decode("utf-8"))
    msg = email.message_from_string(data2[0][1].decode("utf-8"))
    return (dest['Delivered-To'], quopri.decodestring(msg.get_payload()).decode('utf-8').split('[Tigo Tanzania]')[0])


def mail_connect(processor):
    config = configparser.ConfigParser()
    config.read('mailer.cnf')
    params = dict(config['main'])
    with IMAP4_SSL(params['host']) as M:
        M.login(params['user'], params['password'])
        M.select()
        # print(M.list()[1])
        try:
            _, data = M.search(None, '(From "Tigo.Pesa@tigo.co.tz")')
            for msg_id in data[0].split():
                dest, msg = read_msg(M, msg_id)
                m_id = int(msg_id)
                if processor(dest, m_id, msg):
                    print('Success: ', m_id)
                    typ, data = M.copy(msg_id, 'INBOX.Archive.Processed')
                    print(typ, data)
                else:
                    print('Fail: ', m_id)
                break
        finally:
            print('Done executor!')
            M.close()
            M.logout()


def processor(dest, msg_id, msg):
    print(dest, " : ", msg_id, " : ", msg)
    return True


if __name__ == "__main__":
    mail_connect(processor)
