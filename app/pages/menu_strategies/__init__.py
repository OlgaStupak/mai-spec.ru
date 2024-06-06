from abc import ABC, abstractmethod
import flet as ft
from flet_core.control_event import ControlEvent
import logging

from database import Database
from app.config import *
from app.utils import get_buyer_info
from app.pages.form_statement import StatementFormer
from app.pages.statement_form_strategies.automatic import Automatic
from app.pages.statement_form_strategies.selective import Selective


class MenuStrategy(ABC):
    def __init__(self, page: ft.Page, db: Database, exit_function, user_id: int = 1):
        self.page = page
        self.db = db
        self.exit_function = exit_function
        self.user_id = user_id
        self.current_section_index = 0

        self.permanent_elements = None
        self.content = None
        self.right_side = None
        self.rail = None

        self.header_properties = header_properties
        self.textfield_properties = textfield_properties

        logging.debug('Initialized MenuStratagy object')

    @abstractmethod
    def load_page(self) -> None:
        pass

    @abstractmethod
    def change_menu_section(self, e: ControlEvent) -> None:
        pass

    @abstractmethod
    def build_section_projects(self) -> None:
        pass

    @abstractmethod
    def build_section_settings(self) -> None:
        pass

    def _build_section_form_statement(self) -> None:
        header = ft.Row([ft.Text('Формирование ведомости', **header_properties)])
        phrase = ft.Text('Каким способом сформировать ведомость?', size=20)
        explanation1 = ft.ListTile(
            width=500,
            leading=ft.Icon(ft.icons.ARTICLE),
            title=ft.Text('При автоматической генерации ведомости берутся спецификации всех действующих проектов, у которых срок реализации в будущем;')
        )
        explanation2 = ft.ListTile(
            width=500,
            leading=ft.Icon(ft.icons.ARTICLE),
            title=ft.Text('При выборочной генерации ведомости вы сами выбираете спецификации, по которым нужно сформировать ведомость.')
        )
        containers_bgcolor = ft.colors.GREY_900 if self.page.theme_mode == ft.ThemeMode.DARK else ft.colors.GREY_300
        var_automatic = ft.Container(
            content=ft.Text("Автоматически", size=20, weight=ft.FontWeight.W_400),
            data='automatic',
            margin=10,
            padding=10,
            alignment=ft.alignment.center,
            bgcolor=containers_bgcolor,
            width=230,
            height=150,
            border_radius=10,
            ink=True,
            on_click=self.__generate_statement,
        )
        var_selective = ft.Container(
            content=ft.Text("Выборочно", size=20, weight=ft.FontWeight.W_400),
            data='selective',
            margin=10,
            padding=10,
            alignment=ft.alignment.center,
            bgcolor=containers_bgcolor,
            width=230,
            height=150,
            border_radius=10,
            ink=True,
            on_click=self.__generate_statement,
        )

        self.content = ft.Column([
            header,
            phrase,
            ft.Row([var_automatic, var_selective]),
            explanation1,
            explanation2,
        ])
        self._reload_menu()

    def __generate_statement(self, e: ControlEvent) -> None:
        buyer_info = get_buyer_info()
        if not all(buyer_info.values()):
            alert_msg = 'Заполните информацию о вашей организации в настройках. Оставшиеся к заполнению поля: '
            russian_keys = {
                'company': 'название организации',
                'address': 'юридический адрес',
                'inn': 'ИНН',
                'kpp': 'КПП',
                'bank': 'банк',
                'payment_account': 'расчетный счет',
                'bik': 'БИК',
            }
            alert_msg += ', '.join([russian_keys[key] for key, value in buyer_info.items() if not value])
            self.page.snack_bar = ft.SnackBar(content=ft.Text(alert_msg), show_close_icon=True)
            self.page.snack_bar.open = True
            self.page.update()
            return

        if e.control.data == 'automatic':
            statement_former = StatementFormer(Automatic(self.page, self.db, self.user_id, self._reload_menu))
        elif e.control.data == 'selective':
            statement_former = StatementFormer(Selective(self.page, self.db, self.user_id, self._reload_menu))
        else:
            logging.error('Unknown statement form strategy')
            return

        statement_former.form_statement()


    def _reload_menu(self, e: ControlEvent = None):
        self.page.clean()
        self.right_side = ft.Column([self.permanent_elements, self.content])
        self.page.add(
            ft.Row(
                [
                    self.rail,
                    ft.VerticalDivider(width=1),
                    self.right_side
                ],
                expand=True,
            )
        )