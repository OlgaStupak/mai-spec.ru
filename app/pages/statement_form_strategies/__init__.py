from datetime import datetime
from abc import ABC, abstractmethod
import flet as ft
import pandas as pd

from database import Database


class StatementFormStrategy(ABC):
    """
    Абстрактный класс стратегии формирования ведомости
    """
    def __init__(self, page: ft.Page, db: Database, employee_id: int, out_function):
        self.page = page
        self.db = db
        self.employee_id = employee_id
        self.out_function = out_function
        self.very_small_number = 1e-9

    @abstractmethod
    def form_statement(self) -> None:
        pass

    @staticmethod
    def _make_items_table(items: pd.DataFrame) -> ft.DataTable:
        return ft.DataTable(
            columns=[ft.DataColumn(ft.Text(item)) for item in ['№'] + list(items.columns)],
            rows=[
                ft.DataRow(
                    cells=[ft.DataCell(ft.Text(str(cell_data))) for cell_data in [index + 1] + list(row)]
                ) for index, row in items.iterrows()
            ]
        )

    def _print_statement(self, statement_data: dict[str, pd.DataFrame | dict | list[dict]]) -> None:
        page_width = self.page.width
        button_back = ft.IconButton(icon=ft.icons.ARROW_LEFT, tooltip='Назад', on_click=self.out_function)
        header = ft.Row(
            controls=[ft.Text(f'Ведомость от {datetime.now():%d.%m.%Y} г.', size=15)],
            width=page_width,
            alignment=ft.MainAxisAlignment.CENTER
        )
        items_table = ft.Row(
            controls=[self._make_items_table(statement_data['items_info'])],
            width=page_width,
            alignment=ft.MainAxisAlignment.CENTER
        )
        total = float(round(statement_data['items_info']['Сумма'].sum(), 2))
        total_str = f'{total:_}'.replace('.', ',').replace('_', ' ') + f"{'0 ₽' if total * 10 % 1 < self.very_small_number else ' ₽'}"
        total_el = ft.Row(
            controls=[
                ft.Row([ft.Text('Всего:')], width=page_width/5, alignment=ft.MainAxisAlignment.START),
                ft.Row([ft.Text(total_str)], width=page_width/4, alignment=ft.MainAxisAlignment.START)
            ],
            width=page_width,
            alignment=ft.MainAxisAlignment.CENTER
        )
        nds = float(round(total * 0.18, 2))  # НДС 18%
        nds_str = f'{nds:_}'.replace('.', ',').replace('_', ' ') + f"{'0 ₽' if nds * 10 % 1 < self.very_small_number else ' ₽'}"
        nds_el = ft.Row(
            controls=[
                ft.Row([ft.Text('в т.ч. НДС 18%')], width=page_width/5, alignment=ft.MainAxisAlignment.START),
                ft.Row([ft.Text(nds_str)], width=page_width/4, alignment=ft.MainAxisAlignment.START)
            ],
            width=page_width,
            alignment=ft.MainAxisAlignment.CENTER
        )
        buyer_el = ft.ListTile(
            width=page_width/3,
            title=ft.Text(f'Покупатель:'),
            subtitle=ft.Column(
                [
                    ft.Text(f'{statement_data["buyer_info"]["company"]}'),
                    ft.Text(statement_data['buyer_info']['address']),
                    ft.Text(f'ИНН {statement_data["buyer_info"]["inn"]} КПП {statement_data["buyer_info"]["kpp"]}'),
                    ft.Text(f'АКБ {statement_data["buyer_info"]["bank"]}'),
                    ft.Text(f'р/с {statement_data["buyer_info"]["payment_account"]}'),
                    ft.Text(f'БИК {statement_data["buyer_info"]["bik"]}'),
                ]
            )
        )
        providers_el = ft.Column([
            ft.ListTile(
                width=page_width/3,
                title=ft.Text('Поставщик:'),
                subtitle=ft.Column(
                    [
                        ft.Text(f'{provider["company"]}'),
                        ft.Text(f'{provider["address"]}'),
                        ft.Text(f'ИНН {provider["inn"]} КПП {provider["kpp"]}'),
                        ft.Text(f'АКБ {provider["bank"]}'),
                        ft.Text(f'р/с {provider["payment_account"]}'),
                        ft.Text(f'БИК {provider["bik"]}')
                    ]
                )
            ) for provider in statement_data['providers_info']
        ])

        self.page.clean()
        self.page.add(
            button_back,
            header,
            items_table,
            total_el,
            nds_el,
            ft.Row(
                controls=[buyer_el, providers_el],
                width=page_width,
                alignment=ft.MainAxisAlignment.CENTER
            ),
        )