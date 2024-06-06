from app.pages.statement_form_strategies import StatementFormStrategy


class StatementFormer:
    def __init__(self, forming_strategy: StatementFormStrategy):
        self.forming_strategy = forming_strategy

    def form_statement(self) -> None:
        self.forming_strategy.form_statement()