import flet as ft
import pandas as pd
from flet_core.control_event import ControlEvent

from database import Database
from app.utils import get_buyer_info
from app.pages.statement_form_strategies import StatementFormStrategy


class Selective(StatementFormStrategy):
    def __init__(self, page: ft.Page, db: Database, employee_id: int, out_function):
        super().__init__(page, db, employee_id, out_function)
        self.statement_data = {
            'items_info': pd.DataFrame(columns=['Товары', 'Кол-во', 'Цена', 'Сумма']),
            'buyer_info': get_buyer_info(),
            'providers_info': [],
        }

    def form_statement(self) -> None:
        self.__get_chosen_projects()


    def __get_chosen_projects(self) -> None:
        def validate_checkbox(e: ControlEvent):
            if any([checkbox.value for checkbox in checkbox_projects.controls]):
                button_form_statement.disabled = False
            else:
                button_form_statement.disabled = True
            self.page.update()

        projects = self.db.get_projects()

        page_width = self.page.width
        button_back = ft.IconButton(icon=ft.icons.ARROW_LEFT, tooltip='Назад', on_click=self.out_function)
        header = ft.Row(
            controls=[ft.Text(f'Выберите спецификации, которые должны быть в ведомости', size=25)],
            width=page_width,
            alignment=ft.MainAxisAlignment.CENTER
        )
        checkbox_projects = ft.Column([
            ft.Checkbox(
                f"{project['title']}\nДедлайн: {project['deadline'].strftime('%d.%m.%Y')}\nСотрудники с правами на редактирование: "
                f"{', '.join([perm['employee_login'] for perm in project['edit_permissions']]) if project['edit_permissions'] else '...'}",
                data=project['id'],
                on_change=validate_checkbox
            ) for project in projects
        ])
        button_form_statement = ft.ElevatedButton(
            'Сформировать ведомость',
            disabled=True,
            on_click=lambda _: self.__print_statement([checkbox.data for checkbox in checkbox_projects.controls if checkbox.value])
        )

        self.page.clean()
        self.page.add(
            button_back,
            header,
            checkbox_projects,
            button_form_statement,
        )


    def __print_statement(self, project_ids: list[int]) -> None:
        self.__get_statement_data(project_ids)
        self._print_statement(self.statement_data)


    def __get_statement_data(self, project_ids: list[int]) -> None:
        # Get items data
        items = self.db.get_statement_items_data(project_ids=project_ids)
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