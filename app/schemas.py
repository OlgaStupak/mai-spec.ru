from datetime import datetime, timedelta, date
from time import sleep
import flet as ft
from flet_core.control_event import ControlEvent


class ItemTile(ft.ListTile):
    def __init__(
            self,
            page: ft.Page,
            item: dict,
            delete_function=None
    ):
        super().__init__()
        self.page = page
        self.item = item
        self.delete_function = delete_function
        self.max_description_length = 500
        self.very_small_number = 1e-9

        # ListTile fields
        self.title = ft.Text(f"{item['article']}, \"{item['title']}\"")
        self.subtitle = self.__get_subtitle()
        self.trailing = self.__get_trailing()
        self.leading = ft.Icon(ft.icons.CARD_TRAVEL)
        self.data = item['id']

    def __get_subtitle(self):
        description = self.item['description']
        if len(description) > self.max_description_length:
            description = description[:self.max_description_length - 3] + '...'
        price_float = round(float(self.item['price']), 2)
        price = f'{price_float:_}'.replace('.', ',').replace('_', '.') + f"{'0 ₽' if price_float * 10 % 1 < self.very_small_number else ' ₽'}"

        return ft.Column(
            [
                ft.Text(price),
                ft.Text(description),
            ],
            spacing=0
        )

    def __get_trailing(self):
        def validate_amount(e: ControlEvent):
            nonlocal prev_val
            try:
                value = int(amount_el.value)
                if value <= 0:
                    amount_el.value = prev_val
                else:
                    prev_val = value
                    self.item['amount'] = value
            except ValueError:
                amount_el.value = prev_val
                self.item['amount'] = prev_val
            if int(amount_el.value) > 1:
                button_minus.disabled = False
            else:
                button_minus.disabled = True
            self.page.update()

        def increase_by_one(e: ControlEvent):
            nonlocal prev_val
            prev_val = int(amount_el.value)
            amount_el.value = self.item['amount'] = str(prev_val + 1)
            button_minus.disabled = False
            self.page.update()

        def decrease_by_one(e: ControlEvent):
            nonlocal prev_val
            prev_val = int(amount_el.value)
            new_value = prev_val - 1
            amount_el.value = str(new_value)
            self.item['amount'] = new_value
            if new_value == 1:
                button_minus.disabled = True
            self.page.update()

        amount_el = ft.TextField(
            value=str(self.item['amount']),
            text_align=ft.TextAlign.CENTER,
            width=80,
            on_change=validate_amount
        )
        prev_val = self.item['amount']
        button_delete = ft.IconButton(icon=ft.icons.DELETE, data=self.item['id'], on_click=self.delete_function, tooltip='Убрать товар из спецификации')
        button_plus = ft.IconButton(icon=ft.icons.PLUS_ONE, on_click=increase_by_one, tooltip='Увеличить количество на 1')
        button_minus = ft.IconButton(icon=ft.icons.EXPOSURE_MINUS_1, on_click=decrease_by_one, tooltip='Уменьшить количество на 1')
        if self.item['amount'] == 1:
            button_minus.disabled = True

        return ft.Row(
            [
                button_minus,
                amount_el,
                button_plus,
                button_delete
            ],
            width=230,
            alignment=ft.MainAxisAlignment.END
        )


class CustomDatePicker:
    def __init__(self, page: ft.Page, date_selected):
        self.page = page
        self.date_selected = date_selected

        self.date_picker = ft.DatePicker(
            on_change=self.on_change,
            on_dismiss=self.on_dismiss,
            first_date=datetime.now() + timedelta(days=1),
            last_date=datetime.now() + timedelta(days=365 * 2),
        )
        self.page.overlay.append(self.date_picker)

    @property
    def value(self):
        return self.date_picker.value.date() if self.date_picker.value else None

    def on_change(self, e: ControlEvent):
        self.date_selected.value = f"{self.date_picker.value:%d.%m.%Y}" if self.date_picker.value.date() != date.today() else ''
        self.page.update()

    def on_dismiss(self, e: ControlEvent):
        self.date_selected.value = ''
        self.page.update()

    def clean(self):
        self.date_picker.value = None
        self.date_selected.value = ''


class CustomSearchBar:
    def __init__(
            self, page: ft.Page,
            options: list[tuple[int, str]],
            bar_hint_text='Выбор',
            view_hint_text='Выберите элемент из списка...',
            out_function=None
    ):
        self.page = page
        self.out_function = out_function
        self.id2company = {option[0]: option[1] for option in options}
        self.search_bar = ft.SearchBar(
            view_elevation=4,
            divider_color=ft.colors.AMBER,
            bar_hint_text=bar_hint_text,
            view_hint_text=view_hint_text,
            controls=[
                ft.ListTile(title=ft.Text(option[1]), on_click=self.close_anchor, data=option[0]) for option in options
            ],
        )

    @property
    def value(self):
        return self.search_bar.value if self.search_bar.value != self.id2company[0] else ''

    @property
    def value_id(self):
        for id_, company in self.id2company.items():
            if company == self.search_bar.value:
                return id_
        return 0

    @value.setter
    def value(self, value):
        self.search_bar.value = value

    def refresh_provider_list(self, new_options: list[tuple[int, str]]):
        self.id2company = {option[0]: option[1] for option in new_options}
        self.search_bar.controls = [
            ft.ListTile(title=ft.Text(option[1]), on_click=self.close_anchor, data=option[0]) for option in new_options
        ]

    def close_anchor(self, e):
        if e.control.data == 0:  # добавление поставщика
            self.search_bar.close_view('')
            sleep(0.1)
            self.out_function()
        self.search_bar.close_view(self.id2company[e.control.data])

    def clean(self):
        self.search_bar.close_view(self.id2company[0])