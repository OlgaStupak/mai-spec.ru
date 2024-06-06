import flet as ft
from flet import TextField, ElevatedButton, Text, Row, Column
from flet_core.control_event import ControlEvent
import logging


class Auth:
    def __init__(self, page: ft.Page, logging_level: int):
        self.page = page
        logging.getLogger("httpx").setLevel(logging_level)

        # Page elements
        self.input_login = TextField(label='Логин')
        self.input_password = TextField(label='Пароль', password=True, can_reveal_password=True)
        self.button_submit = ElevatedButton(text='Войти', disabled=True)

        # Element actions
        self.input_login.on_change = self.__validate
        self.input_password.on_change = self.__validate

    def load_page(self) -> None:
        self.page.clean()
        self.page.title = 'Авторизация'
        self.__clean_fields()
        self.page.add(
            Row(
                controls=[
                    Column([
                        self.input_login,
                        self.input_password,
                        self.button_submit
                    ])
                ],
                alignment=ft.MainAxisAlignment.CENTER
            )
        )

    def wrong_password_alert(self) -> None:
        self.page.snack_bar = ft.SnackBar(content=ft.Text('Неверный логин или пароль'), show_close_icon=True)
        self.page.snack_bar.open = True
        self.page.update()

    def __validate(self, e: ControlEvent) -> None:
        if all([self.input_login.value, self.input_password.value]):
            self.button_submit.disabled = False
        else:
            self.button_submit.disabled = True
        self.page.update()

    def __clean_fields(self) -> None:
        self.input_login.value = ''
        self.input_password.value = ''