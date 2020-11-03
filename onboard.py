import sys
import gmail
import numpy as np
from db import db_connect
from models import Alias, Customer

if __name__ == '__main__':
    params = sys.argv[1:]
    if len(params):
        with db_connect() as conn:
            if params[0] == 'aliases':
                base = gmail.base_email
                # base = 'npmnoxytsoftwaresolutionsnots'
                email = f'{base}@gmail.com'
                n = len(base)-1
                m1 = np.tril(np.ones(shape=(n, n)), k=-1)
                m2 = np.triu(np.ones(shape=(n, n)))
                combined = np.vstack((m1, m2))
                cursor = None
                try:
                    cursor = conn.cursor()
                    sql = 'INSERT IGNORE INTO npm_aliases (email, alias) values (%s, %s)'
                    for row in combined:
                        res = [None]*(2*n + 1)
                        res[::2] = base
                        res[1::2] = ['.' if x else '' for x in row]
                        alias = ''.join(res)
                        print(alias)
                        cursor.execute(sql, (email, f'{alias}@gmail.com'))
                        conn.commit()
                except Exception as e:
                    print("Error1", e)
                finally:
                    if cursor:
                        cursor.close()

            elif params[0] == 'create' and len(params) >= 3:
                print('Creating customer: ', params)
                name = params[1]
                msisdn = params[2]
                unused = Alias.unused(conn)
                if unused:
                    try:
                        cursor = conn.cursor()
                        sql = 'INSERT INTO npm_customers (name, email, msisdn) values (%s, %s, %s)'
                        cursor.execute(sql, (name,  unused.alias, msisdn))
                        conn.commit()
                        cust = Customer.get(conn, unused.alias)
                        if cust:
                            service = gmail.init_service()
                            gmail.setup_alias(service, cust)
                            Alias.set_used(conn, unused.id)
                            print(f'Successfully onboared {name} - {msisdn} with email id/alias: {unused.alias}')
                    except Exception as e:
                        print("Error?...", e)
                    finally:
                        if cursor:
                            cursor.close()
            else:
                print('Unknown command: ', params[0])
    else:
        print("Missing command. Run $ python onboard.py [create <name> <msisdn>] [aliases]")
