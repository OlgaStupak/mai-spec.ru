import flet as ft
import pandas as pd

from database import Database
from app.utils import get_buyer_info
from app.pages.statement_form_strategies import StatementFormStrategy


class Automatic(StatementFormStrategy):
    def __init__(self, page: ft.Page, db: Database, employee_id: int, out_function):
        super().__init__(page, db, employee_id, out_function)
        self.statement_data = {
            'items_info': pd.DataFrame(columns=['Товары', 'Кол-во', 'Цена', 'Сумма']),
            'buyer_info': get_buyer_info(),
            'providers_info': [],
        }

    def form_statement(self) -> None:
        self.__get_statement_data()
        self._print_statement(self.statement_data)

    def __get_statement_data(self) -> None:
        # Get items data
        items = self.db.get_statement_items_data()
        unique_providers = set()
        for item in items:
            # Add item to items_info DataFrame
            self.statement_data['items_info'] = pd.concat([self.statement_data['items_info'], pd.DataFrame(
                [[item['title'], item['amount'], item['price'], item['cost']]],
                columns=self.statement_data['items_info'].columns
            )], ignore_index=True)
            unique_providers.add(item['provider_id'])

        # Get providers info
        self.statement_data['providers_info'] = self.db.get_statement_providers_data(list(unique_providers))