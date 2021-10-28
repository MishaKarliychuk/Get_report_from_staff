import datetime

import mysql.connector

class Base():

    def __init__(self):
        self.con = self.__con()

    def __con(self):
        con = mysql.connector.connect(host='localhost', user='root', password='#', db='reports')

        mycursor = con.cursor()
        mycursor.execute("""
            CREATE TABLE IF NOT EXISTS users(
                user_id INTEGER NOT NULL,
                telegram_name TEXT
            )""")

        mycursor.execute("""
            CREATE TABLE IF NOT EXISTS report(
                user_id INTEGER NOT NULL,
                day INT,
                future_plans TEXT NULL,
                opinion_about_day TEXT NULL
            )""")

        con.commit()

        return con

    def select_all_users(self):
        cur = self.con.cursor()
        cur.execute("SELECT * FROM `users`")
        data = cur.fetchall()
        return data

    def select_user(self, user_id):
        cur = self.con.cursor()
        cur.execute(f"SELECT * FROM `users` WHERE user_id = {user_id}")
        data = cur.fetchone()
        return data

    def insert_user(self, user_id, telegram_name):
        if self.select_user(user_id):
            return False
        cur = self.con.cursor()
        cur.execute(f"INSERT users (user_id, telegram_name) VALUES ({user_id}, '{telegram_name}')")
        self.con.commit()


    # """"""""""""""""""""

    def update_opinion_about_day(self, user_id, opinion_about_day):
        c = self.con.cursor()
        c.execute(f'UPDATE report SET opinion_about_day = "{opinion_about_day}" WHERE user_id = {int(user_id)}')
        self.con.commit()

    def update_future_plans_of_user(self, user_id, future_plans):
        c = self.con.cursor()
        c.execute(f'UPDATE report SET future_plans = "{future_plans}" WHERE user_id = {int(user_id)}')
        self.con.commit()

    def select_report_of_user(self, user_id):
        now = datetime.datetime.now()
        cur = self.con.cursor()
        cur.execute(f"SELECT * FROM `report` WHERE user_id = {user_id} AND day = {now.day}")
        data = cur.fetchone()
        return data

    def select_all_reports_of_user(self, user_id):
        cur = self.con.cursor()
        cur.execute(f"SELECT * FROM `report` WHERE user_id = {user_id}")
        data = cur.fetchall()
        return data

    def select_all_reports(self):
        cur = self.con.cursor()
        cur.execute("SELECT * FROM `report`")
        data = cur.fetchall()
        return data

    def create_report_of_user(self, user_id):
        if self.select_report_of_user(user_id):
            return False

        now = datetime.datetime.now()

        cur = self.con.cursor()
        cur.execute(f"INSERT report (user_id, day) VALUES ({user_id}, '{now.day}')")
        self.con.commit()

#Base().select_all_users()