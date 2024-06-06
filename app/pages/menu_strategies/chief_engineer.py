from datetime import date
import flet as ft
from flet_core.control_event import ControlEvent
import logging

from database import Database
from . import MenuStrategy
from ..edit_permissions import EditPermissions
from ..edit_specification import EditSpecification
from ...schemas import CustomDatePicker, CustomSearchBar
from ...utils import get_buyer_info, update_buyer_info


class ChiefEngineer(MenuStrategy):

    def __init__(self, page: ft.Page, db: Database, exit_function, user_id: int = 1):
        super().__init__(page, db, exit_function, user_id)
        self.account_button_submit = None
        self.account_sex = None
        self.account_patronymic = None
        self.account_name = None
        self.account_surname = None
        self.account_password = None
        self.account_login = None

        self.create_project_date_selected = None
        self.create_project_custom_date_picker = None
        self.create_project_input_title = None
        self.create_project_custom_search_bar = None
        self.create_project_button_submit = None

        self.provider_company = None
        self.provider_address = None
        self.provider_inn = None
        self.provider_kpp = None
        self.provider_bank = None
        self.provider_payment_account = None
        self.provider_bik = None
        self.provider_button_back = None
        self.provider_button_submit = None


    def load_page(self) -> None:
        rail_padding = 10
        self.rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
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
                    icon=ft.icons.CREATE,
                    label='Создать проект',
                    padding=rail_padding,
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.PRINT,
                    label='Ведомость',
                    padding=rail_padding,
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.PEOPLE,
                    label='Сотрудники',
                    padding=rail_padding,
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.ADD_MODERATOR,
                    label='Добавить аккаунт',
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
                case 1: self.build_section_create_project()
                case 2: self._build_section_form_statement()
                case 3: self.build_section_employees()
                case 4: self.build_section_add_account()
                case 5: self.build_section_settings()
                case _: logging.error(f'Unknown option to build section ({index})')


    def build_section_projects(self) -> None:
        header = ft.Text('Проекты', **self.header_properties)
        projects = self.db.get_projects()
        project_list = ft.Card(
            content=ft.Container(
                width=500,
                content=ft.Column(
                    [
                        ft.ListTile(
                            title=ft.Text(f'{project["title"].title()}'),
                            subtitle=ft.Text(f'{project["deadline"]}: ' + (', '.join([x['employee_login'] for x in project['edit_permissions']]) if project['edit_permissions'] else '...')),
                            trailing=ft.PopupMenuButton(
                                icon=ft.icons.MORE_VERT,
                                items=[
                                    ft.PopupMenuItem(text='Редактировать доступ', data=(project['id'], project['title'],), on_click=self.__edit_permissions_window),
                                    ft.PopupMenuItem(text='Редактировать спецификацию', data=(project['id'], project['title'],), on_click=self.__edit_specification_window),
                                    ft.PopupMenuItem(text='Удалить', data=project['id'], on_click=self.__delete_project),
                                ],
                            ),
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


    def __edit_permissions_window(self, e: ControlEvent) -> None:
        project_id, project_title = e.control.data
        edit_permissions = EditPermissions(self.page, self.db, project_id, project_title, self.build_section_projects)
        edit_permissions.load_page()


    def __edit_specification_window(self, e: ControlEvent) -> None:
        project_id, project_title = e.control.data
        logging.info(f'Editing specification for project {project_id} ({project_title})')
        edit_specification = EditSpecification(self.page, self.db, project_id, project_title, self.build_section_projects)
        edit_specification.load_page()


    def __delete_project(self, e: ControlEvent) -> None:
        self.db.delete_project(e.control.data)
        self.build_section_projects()


    def build_section_create_project(self) -> None:
        header = ft.Row([ft.Text('Создание проекта', **self.header_properties)])

        # 1st element
        self.create_project_input_title = ft.TextField(label='Название проекта')

        # 2nd element
        self.create_project_date_selected = ft.Text('', size=20, weight=ft.FontWeight.W_400)
        self.create_project_custom_date_picker = CustomDatePicker(
            page=self.page,
            date_selected=self.create_project_date_selected,
        )
        input_date = ft.ElevatedButton(
            "Дедлайн",
            icon=ft.icons.CALENDAR_MONTH,
            on_click=lambda _: self.create_project_custom_date_picker.date_picker.pick_date(),
        )
        input_date = ft.Row([input_date, self.create_project_date_selected])

        # 3rd element
        providers = self.db.get_providers()
        provider_companies = list(map(lambda x: (x['id'], x['company'],), providers))
        provider_companies.append((0, 'Добавить поставщика',))
        self.create_project_custom_search_bar = CustomSearchBar(
            page=self.page,
            options=provider_companies,
            bar_hint_text='Поставщик',
            view_hint_text='Выберите поставщика из списка...',
            out_function=self.__add_provider_window
        )

        # Create button
        self.create_project_button_submit = ft.ElevatedButton('Создать проект', on_click=self.__create_project)

        self.content = ft.Column(
            controls=[
                header,
                self.create_project_input_title,
                input_date,
                self.create_project_custom_search_bar.search_bar,
                self.create_project_button_submit,
            ]
        )
        self._reload_menu()


    def __create_project(self, e: ControlEvent) -> None:
        title: str = self.create_project_input_title.value
        deadline: date = self.create_project_custom_date_picker.value
        provider_id: int = self.create_project_custom_search_bar.value_id

        # Validation
        if not all([title, deadline, provider_id]):
            self.page.snack_bar = ft.SnackBar(content=ft.Text('Заполните все поля'), show_close_icon=True)
            self.page.snack_bar.open = True
            self.page.update()
            return

        try:
            self.db.create_project(title, deadline, provider_id)
        except:
            self.page.snack_bar = ft.SnackBar(content=ft.Text('Ошибка создания проекта'), show_close_icon=True)
            self.page.snack_bar.open = True
            self.page.update()
            return
        else:
            self.page.snack_bar = ft.SnackBar(content=ft.Text('Проект успешно создан!'), show_close_icon=True)
            self.page.snack_bar.open = True
            self.create_project_input_title.value = ''
            self.create_project_custom_date_picker.clean()
            self.create_project_custom_search_bar.clean()
            self.page.update()


    def __add_provider_window(self) -> None:
        self.page.clean()
        header = ft.Text('Добавление поставщика', **self.header_properties)

        self.provider_company = ft.TextField(label='Компания', **self.textfield_properties, on_change=self.__validate_provider_fields)
        self.provider_address = ft.TextField(label='Юридический адрес', **self.textfield_properties, on_change=self.__validate_provider_fields)
        self.provider_inn = ft.TextField(label='ИНН', **self.textfield_properties, on_change=self.__validate_provider_fields)
        self.provider_kpp = ft.TextField(label='КПП', **self.textfield_properties, on_change=self.__validate_provider_fields)
        self.provider_bank = ft.TextField(label='Банк', **self.textfield_properties, on_change=self.__validate_provider_fields)
        self.provider_payment_account = ft.TextField(label='Платежный аккаунт', **self.textfield_properties, on_change=self.__validate_provider_fields)
        self.provider_bik = ft.TextField(label='БИК', **self.textfield_properties, on_change=self.__validate_provider_fields)

        self.provider_button_back = ft.ElevatedButton('Назад', on_click=self._reload_menu)
        self.provider_button_submit = ft.ElevatedButton('Добавить', disabled=True, on_click=self.__return_to_creating_project_after_adding_provider)

        form = ft.Column(
            controls=[
                header,
                self.provider_company,
                self.provider_address,
                self.provider_inn,
                self.provider_kpp,
                self.provider_bank,
                self.provider_payment_account,
                self.provider_bik,
                ft.Row([self.provider_button_back, self.provider_button_submit]),
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )
        self.page.add(form)


    def __validate_provider_fields(self, e: ControlEvent) -> None:
        if all([
            self.provider_company.value,
            self.provider_address.value,
            self.provider_inn.value,
            self.provider_kpp.value,
            self.provider_bank.value,
            self.provider_payment_account.value,
            self.provider_bik.value
        ]):
            self.provider_button_submit.disabled = False
        else:
            self.provider_button_submit.disabled = True
        self.page.update()


    def __return_to_creating_project_after_adding_provider(self, e: ControlEvent):
        company = self.provider_company.value
        address = self.provider_address.value
        inn = self.provider_inn.value
        kpp = self.provider_kpp.value
        bank = self.provider_bank.value
        payment_account = self.provider_payment_account.value
        bik = self.provider_bik.value

        if not inn.isnumeric():
            self.page.snack_bar = ft.SnackBar(content=ft.Text('Не удалось обновить данные. ИНН должен состоять из цифр'), show_close_icon=True)
            self.page.snack_bar.open = True
            self.page.update()
            return
        if not 10 <= len(inn) <= 15:
            self.page.snack_bar = ft.SnackBar(content=ft.Text('Не удалось обновить данные. ИНН должен быть от 10 до 15 символов'), show_close_icon=True)
            self.page.snack_bar.open = True
            self.page.update()
            return
        if not kpp.isnumeric():
            self.page.snack_bar = ft.SnackBar(content=ft.Text('Не удалось обновить данные. КПП должен состоять из цифр'), show_close_icon=True)
            self.page.snack_bar.open = True
            self.page.update()
            return
        if not len(kpp) == 9:
            self.page.snack_bar = ft.SnackBar(content=ft.Text('Не удалось обновить данные. КПП должен состоять из 9 символов'), show_close_icon=True)
            self.page.snack_bar.open = True
            self.page.update()
            return
        if not payment_account.isnumeric():
            self.page.snack_bar = ft.SnackBar(content=ft.Text('Не удалось обновить данные. Расчетный счет должен состоять из цифр'), show_close_icon=True)
            self.page.snack_bar.open = True
            self.page.update()
            return
        if not len(payment_account) == 20:
            self.page.snack_bar = ft.SnackBar(content=ft.Text('Не удалось обновить данные. Расчетный счет должен состоять из 20 символов'), show_close_icon=True)
            self.page.snack_bar.open = True
            self.page.update()
            return
        if not bik.isnumeric():
            self.page.snack_bar = ft.SnackBar(content=ft.Text('Не удалось обновить данные. БИК должен состоять из цифр'), show_close_icon=True)
            self.page.snack_bar.open = True
            self.page.update()
            return
        if not len(bik) == 9:
            self.page.snack_bar = ft.SnackBar(content=ft.Text('Не удалось обновить данные. БИК должен состоять из 9 символов'), show_close_icon=True)
            self.page.snack_bar.open = True
            self.page.update()
            return

        provider_details = {
            'company': company,
            'address': address,
            'inn': inn,
            'kpp': kpp,
            'bank': bank,
            'payment_account': payment_account,
            'bik': bik
        }
        try:
            provider_id, provider_company = self.db.add_provider(**provider_details)
        except:
            self.page.snack_bar = ft.SnackBar(content=ft.Text('Ошибка добавления поставщика'), show_close_icon=True)
            self.page.snack_bar.open = True
            self.page.update()
            return
        else:
            new_options = self.db.get_providers()
            provider_companies = list(map(lambda x: (x['id'], x['company'],), new_options))
            provider_companies.append((0, 'Добавить поставщика',))
            self.create_project_custom_search_bar.refresh_provider_list(new_options=provider_companies)
            self.create_project_custom_search_bar.value = provider_company

        # Return back to creating a project
        self._reload_menu()


    def build_section_employees(self) -> None:
        header = ft.Row([ft.Text('Сотрудники', **self.header_properties)])
        employees = self.db.get_employees()
        employee_list = ft.Card(
            content=ft.Container(
                width=500,
                content=ft.Column(
                    [
                        ft.ListTile(
                            leading=ft.Icon(ft.icons.MAN) if employee['sex'] == 'male' else ft.Icon(ft.icons.WOMAN),
                            title=ft.Text(employee['login']),
                            subtitle=ft.Text(f"{employee['surname']} {employee['name']} {employee['patronymic']}"),
                            trailing=ft.IconButton(icon=ft.icons.DELETE, tooltip='Удалить', data=employee['id'], on_click=self.__delete_employee),
                            on_click=self.__edit_employee,
                            data=employee['id'],
                        )
                        for employee in employees
                    ],
                    spacing=0
                ),
                padding=ft.padding.symmetric(vertical=10),
            )
        )

        self.content = ft.Column(
            controls=[
                header,
                employee_list
            ]
        )
        self._reload_menu()


    def __edit_employee(self, e: ControlEvent) -> None:
        employee_id = e.control.data
        # todo: редактирование сотрудника


    def __delete_employee(self, e: ControlEvent) -> None:
        if e.control.data == 1:
            logging.error('Cannot delete the main admin')
            return
        self.db.delete_employee(e.control.data)
        self.build_section_employees()


    def build_section_add_account(self) -> None:
        header = ft.Row([ft.Text('Добавление аккаунта', **self.header_properties)])

        self.account_login = ft.TextField(label='Логин', **self.textfield_properties, on_change=self.__validate_account_fields)
        self.account_password = ft.TextField(label='Пароль', **self.textfield_properties, on_change=self.__validate_account_fields)
        self.account_surname = ft.TextField(label='Фамилия', **self.textfield_properties, on_change=self.__validate_account_fields)
        self.account_name = ft.TextField(label='Имя', **self.textfield_properties, on_change=self.__validate_account_fields)
        self.account_patronymic = ft.TextField(label='Отчество', **self.textfield_properties, on_change=self.__validate_account_fields)
        self.account_sex = ft.RadioGroup(content=ft.Column(
            [
                ft.Radio(value='male', label='Мужской'),
                ft.Radio(value='female', label='Женский')
            ]),
            on_change=self.__validate_account_fields
        )

        self.account_button_submit = ft.ElevatedButton('Добавить', on_click=self.__add_employee)

        self.content = ft.Column(
            controls=[
                header,
                self.account_login,
                self.account_password,
                self.account_surname,
                self.account_name,
                self.account_patronymic,
                ft.Text('Пол'),
                self.account_sex,
                self.account_button_submit,
            ]
        )
        self._reload_menu()


    def __validate_account_fields(self, e: ControlEvent) -> None:
        if all([
            self.account_login.value,
            self.account_password.value,
            self.account_surname.value,
            self.account_name.value,
            self.account_patronymic.value,
            self.account_sex.value,
        ]):
            self.account_button_submit.disabled = False
        else:
            self.account_button_submit.disabled = True
        self.page.update()


    def __add_employee(self, e: ControlEvent) -> None:
        login = self.account_login.value
        password = self.account_password.value
        surname = self.account_surname.value
        name = self.account_name.value
        patronymic = self.account_patronymic.value
        sex = self.account_sex.value

        try:
            self.db.add_employee(login, password, surname, name, patronymic, sex)
        except:
            self.page.snack_bar = ft.SnackBar(content=ft.Text(f'Ошибка добавления аккаунта. Логин "{login}" уже существует'), show_close_icon=True)
            self.page.snack_bar.open = True
            self.page.update()
        else:
            self.page.snack_bar = ft.SnackBar(content=ft.Text('Аккаунт успешно добавлен!'), show_close_icon=True)
            self.page.snack_bar.open = True
            self.account_login.value = ''
            self.account_password.value = ''
            self.account_surname.value = ''
            self.account_name.value = ''
            self.account_patronymic.value = ''
            self.account_sex.value = ''
            self.account_button_submit.disabled = True
            self.page.update()


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

        # Ввод информации об организации
        buyer_info = ft.OutlinedButton('Изменить информацию об организации', on_click=self.__change_buyer_info)

        self.content = ft.Column(
            controls=[
                header,
                app_theme,
                buyer_info,
            ]
        )
        self._reload_menu()


    def __change_buyer_info(self, e: ControlEvent):
        def __save_buyer_info(e: ControlEvent):
            if inn.value:
                if not inn.value.isnumeric():
                    self.page.snack_bar = ft.SnackBar(content=ft.Text('Не удалось обновить данные. ИНН должен состоять из цифр'), show_close_icon=True)
                    self.page.snack_bar.open = True
                    self.page.update()
                    return
                if not 10 <= len(inn.value) <= 15:
                    self.page.snack_bar = ft.SnackBar(content=ft.Text('Не удалось обновить данные. ИНН должен быть от 10 до 15 символов'), show_close_icon=True)
                    self.page.snack_bar.open = True
                    self.page.update()
                    return
            if kpp.value:
                if not kpp.value.isnumeric():
                    self.page.snack_bar = ft.SnackBar(content=ft.Text('Не удалось обновить данные. КПП должен состоять из цифр'), show_close_icon=True)
                    self.page.snack_bar.open = True
                    self.page.update()
                    return
                if not len(kpp.value) == 9:
                    self.page.snack_bar = ft.SnackBar(content=ft.Text('Не удалось обновить данные. КПП должен состоять из 9 символов'), show_close_icon=True)
                    self.page.snack_bar.open = True
                    self.page.update()
                    return
            if payment_account.value:
                if not payment_account.value.isnumeric():
                    self.page.snack_bar = ft.SnackBar(content=ft.Text('Не удалось обновить данные. Расчетный счет должен состоять из цифр'), show_close_icon=True)
                    self.page.snack_bar.open = True
                    self.page.update()
                    return
                if not len(payment_account.value) == 20:
                    self.page.snack_bar = ft.SnackBar(content=ft.Text('Не удалось обновить данные. Расчетный счет должен состоять из 20 символов'), show_close_icon=True)
                    self.page.snack_bar.open = True
                    self.page.update()
                    return
            if bik.value:
                if not bik.value.isnumeric():
                    self.page.snack_bar = ft.SnackBar(content=ft.Text('Не удалось обновить данные. БИК должен состоять из цифр'), show_close_icon=True)
                    self.page.snack_bar.open = True
                    self.page.update()
                    return
                if not len(bik.value) == 9:
                    self.page.snack_bar = ft.SnackBar(content=ft.Text('Не удалось обновить данные. БИК должен состоять из 9 символов'), show_close_icon=True)
                    self.page.snack_bar.open = True
                    self.page.update()
                    return

            update_buyer_info(
                company.value,
                address.value,
                inn.value,
                kpp.value,
                bank.value,
                payment_account.value,
                bik.value
            )
            self.build_section_settings()

        info = get_buyer_info()

        company = ft.TextField(label='Название организации', value=info['company'], **self.textfield_properties)
        address = ft.TextField(label='Юридический адрес', value=info['address'], **self.textfield_properties)
        inn = ft.TextField(label='ИНН', value=info['inn'], **self.textfield_properties)
        kpp = ft.TextField(label='КПП', value=info['kpp'], **self.textfield_properties)
        bank = ft.TextField(label='Банк', value=info['bank'], **self.textfield_properties)
        payment_account = ft.TextField(label='Платежный аккаунт', value=info['payment_account'], **self.textfield_properties)
        bik = ft.TextField(label='БИК', value=info['bik'], **self.textfield_properties)

        button_back = ft.ElevatedButton('Назад', on_click=lambda _: self.build_section_settings())
        button_save = ft.ElevatedButton('Сохранить', on_click=__save_buyer_info)

        self.content = ft.Column([
            company,
            address,
            inn,
            kpp,
            bank,
            payment_account,
            bik,
            ft.Row([button_back, button_save])
        ])
        self._reload_menu()