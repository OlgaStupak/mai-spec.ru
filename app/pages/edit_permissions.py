from time import sleep
import flet as ft
from flet_core.control_event import ControlEvent
from database import Database


class EditPermissions:
    def __init__(self, page: ft.Page, db: Database, project_id: int, project_title: str, out_function):
        self.page = page
        self.page.title = 'Редактирование прав доступа к проекту'
        self.db = db
        self.project_id = project_id
        self.project_title = project_title
        self.out_function = out_function
        self.permissions: list[dict] = self.db.get_project_permissions(self.project_id)
        self.header = ft.Text(f'Редактирование прав доступа к проекту "{self.project_title.title()}"', size=40, weight=ft.FontWeight.W_700)
        self.save_and_exit_button = ft.ElevatedButton('Сохранить и выйти', on_click=self.save_and_exit)
        self.search_bar = None

    def load_page(self):
        self.__update_page()

    def save_and_exit(self, e: ControlEvent) -> None:
        allowed_employees = list(map(lambda x: x['employee_id'], filter(lambda x: x['allowed'], self.permissions)))
        self.db.update_project_permissions(self.project_id, allowed_employees)
        self.out_function()

    def __update_permission(self, e: ControlEvent, allowed: bool):
        employee_id = e.control.data
        for permission in self.permissions:
            if permission['employee_id'] == employee_id:
                permission['allowed'] = allowed
                break
        self.__update_page()

    def __update_page(self):
        self.page.clean()
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.page.add(ft.Column([
            self.header,
            ft.Row([
                ft.Column([
                    ft.Text('Сотрудники с правами:', size=25),
                    self.__make_allowed_list()
                ]),
                ft.Column([
                    self.__make_search_bar()
                ])
            ]),
            self.save_and_exit_button,
        ])),

    def __make_allowed_list(self):
        return ft.Card(
            content=ft.Container(
                width=400,
                content=ft.Column(
                    [
                        ft.ListTile(
                            title=ft.Text(permission['employee_full_name']),
                            subtitle=ft.Text(permission['employee_login']),
                            trailing=ft.IconButton(icon=ft.icons.REMOVE, tooltip='Отнять права', data=permission['employee_id'],
                                                   on_click=lambda _: self.__update_permission(_, False)),
                        )
                        for permission in list(filter(lambda x: x['allowed'], self.permissions))
                    ],
                    spacing=0
                ),
                padding=ft.padding.symmetric(vertical=10),
            )
        )

    def __make_search_bar(self):
        options = [[permission['employee_id'], permission['employee_full_name'], permission['employee_login']]
                   for permission in self.permissions if not permission['allowed']]
        self.search_bar = ft.SearchBar(
            width=300,
            view_elevation=4,
            divider_color=ft.colors.AMBER,
            bar_hint_text='Выбрать сотрудника',
            view_hint_text='Выберите сотрудника из списка...',
            controls=[
                ft.ListTile(
                    title=ft.Text(option[1]),
                    subtitle=ft.Text(option[2]),
                    on_click=self.close_anchor,
                    data=option[0]
                ) for option in options
            ],
        )
        return self.search_bar

    def close_anchor(self, e):
        self.search_bar.close_view('')
        sleep(0.1)
        self.__update_permission(e, True)