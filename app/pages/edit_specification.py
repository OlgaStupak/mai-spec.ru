from time import sleep
import flet as ft
from flet_core.control_event import ControlEvent
import logging
from psycopg2.errors import UniqueViolation

from database import Database
from app.schemas import ItemTile
from app.config import *


class EditSpecification:
    def __init__(self, page: ft.Page, db: Database, project_id: int, project_title: str, out_function):
        self.page = page
        self.page.title = 'Редактирование спецификации проекта'
        self.db = db
        self.project_id = project_id
        self.project_title = project_title
        self.out_function = out_function
        self.items: list[dict] = self.db.get_items(self.project_id)
        self.header = ft.Text(f'Спецификация проекта "{self.project_title.title()}"', size=40, weight=ft.FontWeight.W_700)
        self.button_save_and_exit = ft.ElevatedButton('Сохранить и выйти', on_click=self.__save_and_exit)
        self.content = None
        self.item_tiles = None
        logging.info('EditSpecification object initialized successfully')

    def load_page(self):
        self.__update_page()

    def __delete_item(self, e: ControlEvent):
        item_id = e.control.data
        self.items = [item for item in self.items if item['id'] != item_id]
        self.__update_page()

    def __save_and_exit(self, e: ControlEvent):
        items = []
        for item in self.items:
            items.append([item['id'], item['amount']])
        self.db.update_specification(self.project_id, items)
        self.out_function()

    def __create_item_window(self, e: ControlEvent):
        item_adder = ItemAdder(self.page, self.db, self.items, self.__update_page)
        item_adder.load_page()

    def __add_item_window(self, e: ControlEvent):
        def close_anchor(e: ControlEvent):
            nonlocal items
            chosen_item = e.control.data
            for i in items:
                if i['id'] == chosen_item:
                    chosen_item = i
            new_item = {
                'id': chosen_item['id'],
                'title': chosen_item['title'],
                'article': chosen_item['article'],
                'description': chosen_item['description'],
                'price': chosen_item['price'],
                'amount': 1
            }
            self.items.append(new_item)
            self.items.sort(key=lambda x: x['title'])
            item_search_bar.close_view('')
            sleep(0.1)
            self.__update_page()

        # Получаем товары, которые не в текущей спецификации
        items = self.db.get_items()
        current_project_item_ids = list(map(lambda x: x['id'], self.items))
        items = [item for item in items if item['id'] not in current_project_item_ids]

        header = ft.Text('Выбор товара', **header_properties)
        item_search_bar = ft.SearchBar(
            divider_color=ft.colors.AMBER,
            bar_hint_text="Выбор товара...",
            view_hint_text="Выберите товар из списка...",
            controls=[ft.ListTile(
                title=ft.Text(item['title']),
                subtitle=ft.Text(f"Артикул: {item['article']}"),
                data=item['id'],
                on_click=close_anchor,
            ) for item in items]
        )
        button_back = ft.ElevatedButton('Назад', on_click=lambda _: self.__update_page())

        self.page.clean()
        self.page.add(
            ft.Column([
                header,
                item_search_bar,
                button_back,
            ])
        )

    def __update_page(self):
        button_save_and_exit = ft.IconButton(ft.icons.ARROW_LEFT, tooltip='Сохранить и выйти', on_click=self.__save_and_exit)
        button_create_item = ft.IconButton(ft.icons.ADD_CARD_SHARP, tooltip='Создать товар', on_click=self.__create_item_window)
        button_add_item = ft.IconButton(ft.icons.PRODUCTION_QUANTITY_LIMITS, tooltip='Добавить существующий товар', on_click=self.__add_item_window)
        item_tiles = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    controls=[ItemTile(
                        self.page,
                        item,
                        self.__delete_item
                    ) for item in self.items],
                    spacing=0
                ),
                width=1000,
            )
        )

        self.page.clean()
        self.page.add(
            ft.Column([
                self.header,
                ft.Row([button_save_and_exit, button_create_item, button_add_item]),
                item_tiles,
                self.button_save_and_exit
            ])
        )


class ItemAdder:
    def __init__(self, page: ft.Page, db: Database, items: list[dict], out_function):
        self.page = page
        self.db = db
        self.items = items
        self.out_function = out_function

        # Page elements
        self.header = None
        self.title = None
        self.article = None
        self.description = None
        self.price = None
        self.button_back = None
        self.button_submit = None

    def load_page(self):
        self.header = ft.Text('Добавление товара', size=40, weight=ft.FontWeight.W_700)

        self.title = ft.TextField(label='Название', **textfield_properties, on_change=self.__validate_fields)
        self.article = ft.TextField(label='Артикул', **textfield_properties, on_change=self.__validate_fields)
        self.description = ft.TextField(label='Описание', **textfield_properties, on_change=self.__validate_fields)
        self.price = ft.TextField(label='Цена', **textfield_properties, on_change=self.__validate_fields)

        self.button_back = ft.ElevatedButton('Назад', on_click=lambda _: self.out_function())
        self.button_submit = ft.ElevatedButton('Добавить', disabled=True, on_click=self.__add_item_and_exit)

        self.page.clean()
        self.page.add(
            ft.Column([
                self.header,
                self.title,
                self.article,
                self.description,
                self.price,
                ft.Row([self.button_back, self.button_submit])
            ])
        )

    def __validate_fields(self, e: ControlEvent):
        if all([
            self.title.value,
            self.article.value,
            self.description.value,
            self.price.value,
        ]):
            self.button_submit.disabled = False
        else:
            self.button_submit.disabled = True
        self.page.update()

    def __add_item_and_exit(self, e: ControlEvent):
        # Validate field values
        try:
            article = int(self.article.value)
            if article <= 0:
                raise ValueError
        except ValueError:
            self.page.snack_bar = ft.SnackBar(content=ft.Text('Ошибка добавления товара. Артикул должен быть целым положительным числом'), show_close_icon=True)
            self.page.snack_bar.open = True
            self.page.update()
            return

        try:
            price = float(self.price.value)
            price = round(price, 2)
            if float(self.price.value) <= 0:
                raise ValueError
        except ValueError:
            self.page.snack_bar = ft.SnackBar(content=ft.Text('Ошибка добавления товара. Цена должна быть положительным числом'), show_close_icon=True)
            self.page.snack_bar.open = True
            self.page.update()
            return

        # Add item to database
        title = self.title.value
        description = self.description.value
        try:
            item_id = self.db.add_item(title, article, description, price)
        except UniqueViolation:
            self.page.snack_bar = ft.SnackBar(content=ft.Text(f'Ошибка добавления товара. Товар с таким артикулом ({article}) уже существует'), show_close_icon=True)
            self.page.snack_bar.open = True
            self.page.update()
            return

        # Add item to items list and return to previous page
        new_item = {
            'id': item_id,
            'title': title,
            'article': article,
            'description': description,
            'price': price,
            'amount': 1
        }
        self.items.append(new_item)
        self.items.sort(key=lambda x: x['title'])
        self.out_function()