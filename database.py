import sqlite3
from datetime import date, datetime, timedelta
from smsapi import VirtualNumber, MdnMessage
from nowpayments import CryptoPayment


# ======================================================================================================================


def ensure_connection(func):
    def inner(*args, **kwargs):
        with sqlite3.connect('DataBase.db') as conn:
            res = func(*args, conn=conn, **kwargs)
        return res

    return inner


@ensure_connection
def init_db(conn, force: bool = False):
    c = conn.cursor()

    if force:
        c.execute("DROP TABLE IF EXISTS users_base")
        c.execute("DROP TABLE IF EXISTS voip_numbers")
        c.execute("DROP TABLE IF EXISTS crypto_payments")

    c.execute("""
        CREATE TABLE IF NOT EXISTS users_base (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            date_of_registration TEXT,
            balance REAL,
            deposit REAL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS voip_numbers (
            id INTEGER PRIMARY KEY,
            mdn_id INTEGER,
            mdn TEXT,
            service TEXT,
            state TEXT,
            price REAL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            till_expiration INTEGER,
            status TEXT DEFAULT 'Awaiting SMS',
            reply TEXT DEFAULT NULL,
            pin TEXT DEFAULT NULL,
            timestamp DATETIME DEFAULT NULL,
            user_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users_base (user_id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS crypto_payments (
            id INTEGER PRIMARY KEY,
            payment_id INTEGER,
            payment_amount REAL,
            payment_url TEXT,
            created_at DATETIME,
            status TEXT DEFAULT 'waiting',
            finished_at DATETIME DEFAULT NULL,
            user_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users_base (user_id)
        )
    """)

    conn.commit()


@ensure_connection
def get_user_id_for_sms(conn, number: str or int, number_id: str or int):
    c = conn.cursor()
    c.execute("SELECT user_id FROM voip_numbers WHERE mdn = ? AND mdn_id = ?", (number, number_id,))
    data = c.fetchone()
    return data[0]


@ensure_connection
def get_user_id_for_crypto(conn, payment_id: int):
    c = conn.cursor()
    c.execute("SELECT user_id FROM crypto_payments WHERE payment_id = ?", (payment_id,))
    data = c.fetchone()
    return data[0]


# ======================================================================================================================


class User:
    @staticmethod
    def _ensure_connection(func):
        def inner(self, *args, **kwargs):
            with sqlite3.connect('DataBase.db') as conn:
                return func(self, conn, *args, **kwargs)

        return inner

    @_ensure_connection
    def __init__(self, conn, user_id, username=None, date_of_registration=None, balance=None, deposit=None):
        self.user_id = user_id

        c = conn.cursor()
        c.execute("SELECT user_id FROM users_base WHERE user_id = ?", (self.user_id,))
        data = c.fetchone()

        if data is not None:
            username = c.execute("SELECT username FROM users_base WHERE user_id = ?", (self.user_id,)).fetchone()[0]
            date_of_registration = \
                c.execute("SELECT date_of_registration FROM users_base WHERE user_id = ?", (self.user_id,)).fetchone()[
                    0]
            balance = c.execute("SELECT balance FROM users_base WHERE user_id = ?", (self.user_id,)).fetchone()[0]
            deposit = c.execute("SELECT deposit FROM users_base WHERE user_id = ?", (self.user_id,)).fetchone()[0]
            self.username = "@" + username
            self.date_of_registration = date_of_registration
            self.balance = balance
            self.deposit = deposit
        elif data is None:
            self.username = "@" + username
            self.date_of_registration = date_of_registration or date.today()
            self.balance = balance or 0.0
            self.deposit = deposit or 0.0

    @_ensure_connection
    def add_to_database(self, conn):
        c = conn.cursor()
        c.execute("SELECT user_id FROM users_base WHERE user_id = ?", (self.user_id,))
        data = c.fetchone()

        if data is None:
            c.execute("INSERT INTO users_base (user_id, username, date_of_registration, balance, deposit)"
                      "VALUES (?, ?, ?, ?, ?)", (self.user_id, self.username, self.date_of_registration,
                                                 self.balance, self.deposit))
            conn.commit()

    @_ensure_connection
    def update_balance(self, conn, amount: float):
        c = conn.cursor()
        self.balance += amount

        if amount > 0:
            self.deposit += amount
            c.execute("UPDATE users_base SET balance = ?, deposit = ? WHERE user_id = ?",
                      (self.balance, self.deposit, self.user_id))
        else:
            c.execute("UPDATE users_base SET balance = ? WHERE user_id = ?",
                      (self.balance, self.user_id))

        conn.commit()

    @_ensure_connection
    def insert_voip_number(self, conn, number: VirtualNumber):
        c = conn.cursor()
        mdn_number = number.mdn_number_text()
        mdn_id = number.mdn_id
        service = number.service
        state = number.mdn_state
        price = number.price
        till_expiration = number.mdn_time_till_expiration
        c.execute("INSERT INTO voip_numbers (mdn, mdn_id, service, state, price, till_expiration, user_id)"
                  "VALUES (?, ?, ?, ?, ?, ?, ?)",
                  (mdn_number, mdn_id, service, state, price, till_expiration, self.user_id))
        conn.commit()

    @_ensure_connection
    def update_used_voip_number(self, conn, number: MdnMessage):
        c = conn.cursor()

        c.execute("UPDATE voip_numbers SET status = 'succeeded', reply = ?, pin = ?, timestamp = ? "
                  "WHERE mdn_id = ?",
                  (number.mdn_reply, number.pin, datetime.now(), number.mdn_id))
        conn.commit()
        print(f"VoIP number {number.mdn_number} with id {number.mdn_id} added to the used numbers history of {self.user_id} user.")

    @_ensure_connection
    def get_active_numbers(self, conn):
        c = conn.cursor()

        # Get the active numbers for the user with status 'waiting'
        c.execute("SELECT mdn_id, mdn, service, price, status, created_at, till_expiration FROM voip_numbers WHERE "
                  "user_id = ? AND status = 'Awaiting SMS'",
                  (self.user_id,))
        active_numbers = c.fetchall()

        if active_numbers:
            result_text = "number | service | price | status | time_left (minutes)\n"
            for number in active_numbers:
                number_id, mdn, service, price, status, created_at, till_expiration = number

                # Check if the number has exceeded its time
                expiration_time = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S") + timedelta(
                    minutes=till_expiration)
                time_left = expiration_time - datetime.now()
                time_left_minutes = max(time_left.total_seconds() / 60, 0)

                # Update the status to 'canceled' if exceeded
                if time_left <= timedelta(0):
                    c.execute("UPDATE voip_numbers SET status = 'canceled' WHERE id = ?", (number_id,))
                    continue  # Skip to the next iteration if the number is canceled

                # Update the time left
                c.execute("UPDATE voip_numbers SET till_expiration = ? WHERE id = ?", (time_left_minutes, number_id))

                result_text += f"{mdn} | {service} | {price} | {status} | {time_left_minutes:.2f}\n"

            conn.commit()
            return result_text
        else:
            return f"No active numbers found for user {self.user_id} with status 'waiting'."

    @_ensure_connection
    def get_used_numbers_history(self, conn):
        c = conn.cursor()

        c.execute(
            "SELECT timestamp, service, mdn, price, pin FROM voip_numbers WHERE user_id = ? AND status = ? LIMIT 20",
            (self.user_id, 'succeeded'))
        entries = c.fetchall()

        if entries:
            result_text = "timestamp | service | mdn | price | pin\n"
            for entry in entries:
                result_text += " | ".join(map(str, entry)) + "\n"

            return result_text
        else:
            return f"No entries found in the used numbers history for user {self.user_id}."

    @_ensure_connection
    def insert_crypto_payment(self, conn, payment: CryptoPayment):
        c = conn.cursor()
        payment_id = payment.payment_id
        payment_amount = payment.payment_amount
        payment_url = payment.payment_url
        created_at = payment.created_at
        c.execute("INSERT INTO crypto_payments (payment_id, payment_amount, payment_url, created_at, user_id)"
                  "VALUES (?, ?, ?, ?, ?)",
                  (payment_id, payment_amount, payment_url, created_at, self.user_id))
        conn.commit()

    @_ensure_connection
    def update_crypto_payment(self, conn, payment: CryptoPayment):
        c = conn.cursor()
        payment_id = payment.payment_id
        c.execute("UPDATE crypto_payments SET status = ?, finished_at = ? "
                  "WHERE payment_id = ?", ('finished', datetime.now(), payment_id))
        conn.commit()

    @_ensure_connection
    def get_finished_payments(self, conn):
        c = conn.cursor()

        c.execute(
            "SELECT finished_at, payment_url, payment_amount, payment_id FROM crypto_payments "
            "WHERE user_id = ? AND status = ? LIMIT 20",
            (self.user_id, 'finished'))
        entries = c.fetchall()

        if entries:
            result_text = "Finished at | Payment ID | Amount in <i>USD</i> | Payment URL\n"
            for entry in entries:
                result_text += " | ".join(map(str, entry)) + "\n"

            return result_text
        else:
            return f"No entries found in the payments history for user {self.user_id}."


# ======================================================================================================================


if __name__ == "__main__":
    init_db(force=False)

    def test_user_class():
        # Create a user
        user = User(user_id=1, username="Alice")

        # Add user to the database
        user.add_to_database()

        # Update balance
        user.update_balance(amount=50.0)

        # Insert a virtual number
        mdn_number = tuple(("123456789", "Test", None, 1.0, 60, 228))
        virtual_number = VirtualNumber(mdn=mdn_number)
        user.insert_voip_number(number=virtual_number)

        # Update used voip number
        form_data = {
            "id": 228,
            "to": "123456789",
            "service": "Test",
            "price": 1.0,
            "reply": "Reply",
            "pin": "1234",
            "from": "987654321",
            "date_time": datetime.now()
        }
        mdn_message = MdnMessage(form_data=form_data)
        user.update_used_voip_number(number=mdn_message)

        # Get active numbers
        active_numbers = user.get_active_numbers()
        print("Active Numbers:\n", active_numbers)

        # Get user used numbers history
        used_numbers_history = user.get_used_numbers_history()
        print("Used Numbers History:\n", used_numbers_history)

    # Run the test
    test_user_class()
