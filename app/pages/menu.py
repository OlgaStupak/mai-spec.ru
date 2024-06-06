import flet as ft

from database import Database
from .menu_strategies.chief_engineer import ChiefEngineer
from .menu_strategies.lead_employee import LeadEmployee


class Menu:
    def __init__(self, page: ft.Page, db: Database, exit_function):
        self.page = page
        self.db = db
        self.exit_function = exit_function
        self.user_id = None
        self.menu_strategy = None


    def load_page(self, user_id: int):
        self.user_id = user_id
        self.page.title = 'Главная'

        if user_id == 1:
            self.menu_strategy = ChiefEngineer(self.page, self.db, self.exit_function)
        else:
            self.menu_strategy = LeadEmployee(self.page, self.db, self.exit_function, user_id)

        self.menu_strategy.load_page()