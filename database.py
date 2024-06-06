from datetime import date
import psycopg2


class Database:
    def __init__(self, db_dbname: str, db_host: str, db_user: str, db_password: str):
        self.conn = psycopg2.connect(dbname=db_dbname,
                                     host=db_host,
                                     user=db_user,
                                     password=db_password)
        self.cur = self.conn.cursor()

        files = [
            'sql/employee.sql',
            'sql/provider.sql',
            'sql/project.sql',
            'sql/item.sql',
        ]

        for file in files:
            with open(file, 'r', encoding='utf-8') as f:
                self.cur.execute(f.read())

    ### Авторизация ###
    def login_employee(self, login: str, password: str) -> int:
        self.cur.execute(f"SELECT login_employee('{login}', '{password}');")
        res = self.cur.fetchall()[0][0]
        if res is None:
            return 0
        return res

    ### Поставщики ###
    def get_providers(self) -> list[dict]:
        self.cur.execute(f"SELECT * FROM get_providers();")
        res = self.cur.fetchall()
        providers = []
        for provider in res:
            providers.append({
                'id': provider[0],
                'company': provider[1],
                'address': provider[2],
                'inn': provider[3],
                'kpp': provider[4],
                'bank': provider[5],
                'payment_account': provider[6],
                'bik': provider[7],
            })
        return providers

    def add_provider(
            self,
            company: str,
            address: str,
            inn: str,
            kpp: str,
            bank: str,
            payment_account: str,
            bik: str
    ) -> tuple[int, str]:
        self.cur.execute(f"SELECT * FROM add_provider('{company}', '{address}', '{inn}', '{kpp}', '{bank}', '{payment_account}', '{bik}');")
        self.conn.commit()
        result = self.cur.fetchall()
        provider_id, provider_company = result[0]
        return provider_id, provider_company

    def get_statement_providers_data(self, provider_ids: list[int]) -> list[dict]:
        self.cur.execute(f"SELECT * FROM get_statement_providers_data(ARRAY{provider_ids}::INT[]);")
        res = self.cur.fetchall()
        statement_data = []
        for data in res:
            statement_data.append({
                'company': data[0],
                'address': data[1],
                'inn': data[2],
                'kpp': data[3],
                'bank': data[4],
                'payment_account': data[5],
                'bik': data[6],
            })
        return statement_data


    ### Проекты ###
    def create_project(
            self,
            title: str,
            deadline: date,
            provider_id: int,
    ) -> int:
        self.cur.execute(f"SELECT * FROM create_project('{title}', '{deadline}', {provider_id});")
        self.conn.commit()
        return self.cur.fetchall()[0][0]

    def get_projects(self) -> list[dict]:
        self.cur.execute(f"SELECT * FROM get_projects();")
        res = self.cur.fetchall()
        projects = []
        for project in res:
            projects.append({
                'id': project[0],
                'title': project[1],
                'deadline': project[2],
                'provider_company': project[3],
                'creation_date': project[4],
                'edit_permissions': [{
                    'employee_id': perm[0],
                    'employee_login': perm[1],
                } for perm in project[5]],
            })
        return projects

    def get_employee_projects(self, employee_id: int) -> list[dict]:
        self.cur.execute(f"SELECT * FROM get_employee_projects({employee_id});")
        res = self.cur.fetchall()
        projects = []
        for project in res:
            projects.append({
                'id': project[0],
                'title': project[1],
                'deadline': project[2],
                'provider_company': project[3],
                'creation_date': project[4],
            })
        return projects

    def delete_project(self, project_id: int) -> None:
        self.cur.execute(f"SELECT delete_project({project_id});")
        self.conn.commit()

    def get_project_permissions(self, project_id: int) -> list[dict]:
        self.cur.execute(f"SELECT * FROM get_project_permissions({project_id});")
        res = self.cur.fetchall()
        permissions = []
        for perm in res:
            permissions.append({
                'employee_id': perm[0],
                'employee_login': perm[1],
                'employee_full_name': perm[2],
                'employee_sex': perm[3],
                'allowed': perm[4],
            })
        return permissions

    def update_project_permissions(self, project_id: int, employee_ids: list[int]) -> None:
        self.cur.execute(f"SELECT update_project_permissions({project_id}, ARRAY{employee_ids}::INT[]);")
        self.conn.commit()


    ### Сотрудники ###
    def get_employees(self) -> list[dict]:
        self.cur.execute(f"SELECT * FROM get_employees();")
        res = self.cur.fetchall()
        employees = []
        for employee in res:
            employees.append({
                'id': employee[0],
                'login': employee[1],
                'surname': employee[2],
                'name': employee[3],
                'patronymic': employee[4],
                'sex': employee[5],
                'registration_date': employee[6],
            })
        return employees

    def add_employee(
            self,
            login: str,
            password: str,
            surname: str,
            name: str,
            patronymic: str,
            sex: str
    ) -> int:
        assert sex in ['male', 'female']
        self.cur.execute(f"SELECT * FROM add_employee('{login}', '{password}', '{surname}', '{name}', '{patronymic}', '{sex}');")
        self.conn.commit()
        return self.cur.fetchall()[0][0]

    def delete_employee(self, employee_id: int) -> None:
        self.cur.execute(f"SELECT delete_employee({employee_id});")
        self.conn.commit()


    ### Товары ###
    def get_items(self, project_id: int = 0) -> list[dict]:
        self.cur.execute(f"SELECT * FROM get_items({project_id});")
        res = self.cur.fetchall()
        items = []
        for item in res:
            items.append({
                'id': item[0],
                'title': item[1],
                'article': item[2],
                'description': item[3],
                'price': item[4],
                'amount': item[5],
            })
        return items

    def update_specification(self, project_id: int, items: list[list[int]]) -> None:
        self.cur.execute(f"SELECT update_specification({project_id}, ARRAY{items}::INT[][]);")
        self.conn.commit()

    def add_item(self, title: str, article: int, description: str, price: float) -> int:
        self.conn.rollback()
        self.cur.execute(f"SELECT * FROM add_item('{title}', {article}, '{description}', {price});")
        self.conn.commit()
        return self.cur.fetchall()[0][0]

    def get_statement_items_data(self, project_ids: list[int] = None) -> list[dict]:
        if project_ids is None:
            project_ids = []
        self.cur.execute(f"SELECT * FROM get_statement_items_data(ARRAY{project_ids}::INT[]);")
        res = self.cur.fetchall()
        statement_data = []
        for data in res:
            statement_data.append({
                'title': data[0],
                'amount': data[1],
                'price': data[2],
                'cost': data[3],
                'provider_id': data[4],
            })
        return statement_data