import os
import json
import flet as ft
from flet_core.control_event import ControlEvent
import logging

from data import db_dbname, db_host, db_user, db_password
from database import Database
from .pages import Auth, Menu
from app.config import PATH_TO_BUYER_INFO


class App:
    def __init__(self, page: ft.Page):
        self.page = page
        self.db = Database(
            db_dbname=db_dbname,
            db_host=db_host,
            db_user=db_user,
            db_password=db_password
        )
        self.page.theme_mode = ft.ThemeMode.DARK
        self.title = None
        self.auth = None
        self.menu = None
        self.menu_specific_strategy = None

        # Создания файла для хранения информации о нас как о покупателе
        if not os.path.exists(PATH_TO_BUYER_INFO):
            with open(PATH_TO_BUYER_INFO, 'w') as file:
                json.dump({
                    'company': '',
                    'address': '',
                    'inn': '',
                    'kpp': '',
                    'bank': '',
                    'payment_account': '',
                    'bik': '',
                }, file, ensure_ascii=False, indent=4)

        logging.debug('Initialized App object')


    def run(self):
        self.title = 'Авторизация'
        self.auth = Auth(self.page, logging.INFO)
        self.menu = Menu(self.page, self.db, self.button_menu_logout)
        self.menu_specific_strategy = self.menu.menu_strategy

        # Связь между страницами
        self.auth.button_submit.on_click = self.button_auth_submit

        self.auth.load_page()
        # self.menu.load_page(1)  # debug mode


    def button_auth_submit(self, e: ControlEvent):
        login = self.auth.input_login.value.strip()
        password = self.auth.input_password.value
        user_id = self.db.login_employee(login, password)
        if user_id:
            self.menu.load_page(user_id)
        else:
            self.auth.wrong_password_alert()


    def button_menu_logout(self, e: ControlEvent):
        self.auth.load_page()