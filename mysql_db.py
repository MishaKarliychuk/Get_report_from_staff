import datetime

import mysql.connector
from pytz import timezone
from config import PASSWORD_MYSQL

class Base():

    def __init__(self):
        self.con = self.__con()

    def __con(self):
        con = mysql.connector.connect(host='localhost', user='root', password=PASSWORD_MYSQL, db='reports')

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
                date TEXT,
                report TEXT NULL
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
        # если пользователь уже создан, то обновляем его никнейм
        if self.select_user(user_id):
            self.update_telegram_name_user(user_id, telegram_name)
            return False
        cur = self.con.cursor()
        cur.execute(f"INSERT users (user_id, telegram_name) VALUES ({user_id}, '{telegram_name}')")
        self.con.commit()

    def update_telegram_name_user(self, user_id, telegram_name):
        c = self.con.cursor()
        c.execute(f'UPDATE users SET telegram_name = "{telegram_name}" WHERE user_id = {int(user_id)}')
        self.con.commit()


    # """"""""""""""""""""

    def update_opinion_about_day(self, user_id, opinion_about_day):
        c = self.con.cursor()
        c.execute(f'UPDATE report SET opinion_about_day = "{opinion_about_day}" WHERE user_id = {int(user_id)}')
        self.con.commit()

    def update_report_text_of_user(self, user_id, report_text):
        c = self.con.cursor()
        c.execute(f'UPDATE report SET report = "{report_text}" WHERE user_id = {int(user_id)}')
        self.con.commit()

    def select_report_of_user(self, user_id):
        """Достает отчет от пользователя за сегодня"""
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

    def create_report_of_user(self, user_id, report_text):
        # if self.select_report_of_user(user_id):
        #     return False

        now = datetime.datetime.now(timezone('Poland'))

        report_text = report_text.replace('\n', '   |   ')
        cur = self.con.cursor()
        cur.execute(f"INSERT report (user_id, day, date, report) VALUES ({user_id}, '{now.day}', '{now}', '{report_text}')")
        self.con.commit()

#Base().select_all_users()