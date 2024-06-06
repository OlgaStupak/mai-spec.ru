from datetime import date
import flet as ft
from flet_core.control_event import ControlEvent
import logging

from database import Database
from . import MenuStrategy
from ..edit_specification import EditSpecification


class LeadEmployee(MenuStrategy):

    def __init__(self, page: ft.Page, db: Database, exit_function, user_id: int = 1):
        super().__init__(page, db, exit_function, user_id)


    def load_page(self) -> None:
        rail_padding = 10
        self.rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            extended=True,
            min_width=100,
            min_extended_width=400,
            leading=ft.FloatingActionButton(icon=ft.icons.LOGOUT, tooltip='Выйти из аккаунта', on_click=self.exit_function),
            group_alignment=0.0,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.icons.WORK,
                    label='Проекты',
                    padding=rail_padding,
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.PRINT,
                    label='Ведомость',
                    padding=rail_padding,
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.SETTINGS,
                    label='Настройки',
                    padding=rail_padding,
                ),
            ],
            on_change=self.change_menu_section,
        )

        # Upper bar of each section
        self.permanent_elements = ft.Row(
            controls=[
                # тут была кнопка выхода из аккаунта
            ],
            alignment=ft.MainAxisAlignment.END,
        )

        self.page.clean()
        self.build_section_projects()

    def change_menu_section(self, e: ControlEvent) -> None:
        index = e.control.selected_index
        if self.current_section_index != index:
            self.current_section_index = index
            match index:
                case 0: self.build_section_projects()
                case 1: self._build_section_form_statement()
                case 2: self.build_section_settings()
                case _: logging.error(f'Unknown option to build section ({index})')


    def build_section_projects(self) -> None:
        header = ft.Text('Проекты', **self.header_properties)
        projects = self.db.get_employee_projects(self.user_id)
        project_list = ft.Card(
            content=ft.Container(
                width=500,
                content=ft.Column(
                    [
                        ft.ListTile(
                            title=ft.Text(f'{project["title"].title()}'),
                            subtitle=ft.Text(f'{project["deadline"]}'),
                            on_click=self.__edit_specification_window,
                            data=(project['id'], project['title'],),
                        )
                        for project in projects
                    ],
                    spacing=0
                ),
                padding=ft.padding.symmetric(vertical=10),
            )
        )

        self.content = ft.Column(
            controls=[
                header,
                project_list
            ]
        )
        self._reload_menu()


    def __edit_specification_window(self, e: ControlEvent) -> None:
        project_id, project_title = e.control.data
        logging.info(f'Editing specification for project {project_id} ({project_title})')
        edit_specification = EditSpecification(self.page, self.db, project_id, project_title, self.build_section_projects)
        edit_specification.load_page()


    def build_section_create_project(self) -> None:
        pass

    def build_section_employees(self) -> None:
        pass

    def build_section_add_account(self) -> None:
        pass

    def build_section_settings(self) -> None:
        def change_theme(e: ControlEvent):
            nonlocal button_theme_icon
            if self.page.theme_mode == ft.ThemeMode.LIGHT:
                self.page.theme_mode = ft.ThemeMode.DARK
                button_theme_icon.icon = ft.icons.NIGHTLIGHT
            else:
                self.page.theme_mode = ft.ThemeMode.LIGHT
                button_theme_icon.icon = ft.icons.LIGHT_MODE
            self.page.update()

        header = ft.Row([ft.Text('Настройки', **self.header_properties)])
        button_theme_icon = ft.IconButton(ft.icons.LIGHT_MODE, tooltip='Сменить тему', on_click=change_theme)
        if self.page.theme_mode == ft.ThemeMode.DARK:
            button_theme_icon.icon = ft.icons.NIGHTLIGHT
        app_theme = ft.Row([ft.Text('Тема приложения'), button_theme_icon])

        self.content = ft.Column(
            controls=[
                header,
                app_theme,
            ]
        )
        self._reload_menu()