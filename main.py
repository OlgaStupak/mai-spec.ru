import flet as ft
import logging
from app import App


def main(page: ft.Page):

    # Настройка логов
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        filename='info.log',
        filemode='w',
        level=logging.INFO
    )

    app = App(page)
    app.run()


if __name__ == '__main__':
    ft.app(target=main, view=ft.WEB_BROWSER)
    # ft.app(target=main)