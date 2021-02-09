class Customer:
    def __init__(self, row):
        c_id, name, email, msisdn = row
        self.id = c_id
        self.name = name
        self.email = email
        self.msisdn = msisdn

    @staticmethod
    def list(conn):
        cursor = None
        res = []
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM npm_customers")
            res = [Customer(row) for row in cursor.fetchall()]
        except Exception as e:
            print("Error listing customers", e)
        finally:
            if cursor:
                cursor.close()
        return res

    @staticmethod
    def new_messages(conn, email):
        cursor = None
        res = []
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM npm_messages where status=0 and email=%s', (email))
            res = [Customer(row) for row in cursor.fetchall()]
        except Exception as e:
            print("Error recording new message", e)
        finally:
            if cursor:
                cursor.close()
        return res

    @staticmethod
    def get(conn, email):
        cursor = None
        res = []
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM npm_customers where email=%s", (email,))
            res = [Customer(row) for row in cursor.fetchall()]
        except Exception as e:
            print("Error fething customers", e)
        finally:
            if cursor:
                cursor.close()
        return res[0] if len(res) else None


class Message:
    def __init__(self, row):
        m_id, status, email, message_id, body = row
        self.id = m_id
        self.email = email
        self.body = body

    @staticmethod
    def new_messages(conn, email):
        cursor = None
        res = []
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM npm_messages where status=0 and email=%s', (email))
            res = [Message(row) for row in cursor.fetchall()]
        except Exception as e:
            print("Error recording message2", e, email)
        finally:
            if cursor:
                cursor.close()
        return res

    @staticmethod
    def set_processed(conn, m_id, status):
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE npm_messages set status=%s WHERE id=%s", (status, m_id))
            conn.commit()
        except Exception as e:
            print("Error updating message", e)
        finally:
            if cursor:
                cursor.close()


class Alias:
    def __init__(self, row):
        a_id, email, alias, used = row
        self.id = a_id
        self.alias = alias
        self.email = email
        self.used = used

    @staticmethod
    def unused(conn):
        cursor = None
        res = []
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM npm_aliases where used=0 limit 1 ")
            res = [Alias(row) for row in cursor.fetchall()]
        except Exception as e:
            print("Error updating as unused", e)
        finally:
            if cursor:
                cursor.close()
        return res[0] if len(res) else None

    @staticmethod
    def set_used(conn, a_id):
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE npm_aliases set used=1 WHERE id=%s", (a_id,))
            conn.commit()
        except Exception as e:
            print("Error setting as used: ", e)
        finally:
            if cursor:
                cursor.close()
