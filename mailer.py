from imaplib import IMAP4_SSL
import email
import quopri
import configparser


def read_msg(M, msg_id):
    _, deliv_data = M.fetch(msg_id, '(UID BODY[HEADER.FIELDS (Delivered-To)])')
    _, to_data = M.fetch(msg_id, '(UID BODY[HEADER.FIELDS (To)])')
    print(deliv_data)
    print(to_data)
    _, text_data = M.fetch(msg_id, '(UID BODY[TEXT])')
    dest = email.message_from_string(deliv_data[0][1].decode("utf-8"))
    to = email.message_from_string(to_data[0][1].decode("utf-8"))
    msg = email.message_from_string(text_data[0][1].decode("utf-8"))
    sanitized_to = to['To'].split(' ')[0].replace('"', '')
    return (dest['Delivered-To'], sanitized_to, quopri.decodestring(msg.get_payload()).decode('utf-8').split('[Tigo Tanzania]')[0])


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
                dest, to, msg = read_msg(M, msg_id)
                print(dest)
                print(to)
                m_id = int(msg_id)
                if processor(dest, m_id, msg):
                    print('Success: ', m_id)
                    typ, data = M.copy(msg_id, 'INBOX.Archive.Processed')
                    print(typ, data)
                    if typ == 'OK':
                        M.store(msg_id, '+FLAGS', '\\Deleted')
                else:
                    print('Fail: ', m_id)
                # break
            M.expunge()
        finally:
            print('Done executor!')
            M.close()
            M.logout()


def processor(dest, msg_id, msg):
    print(dest, " : ", msg_id, " : ", msg)
    return True


if __name__ == "__main__":
    mail_connect(processor)
