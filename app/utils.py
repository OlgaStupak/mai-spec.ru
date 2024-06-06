import json
from app.config import PATH_TO_BUYER_INFO


def get_buyer_info() -> dict:
    with open(PATH_TO_BUYER_INFO, 'r', encoding='utf-8') as file:
        return json.load(file)


def update_buyer_info(
        company: str,
        address: str,
        inn: str,
        kpp: str,
        bank: str,
        payment_account: str,
        bik: str
) -> None:
    buyer_info = {
        'company': company,
        'address': address,
        'inn': inn,
        'kpp': kpp,
        'bank': bank,
        'payment_account': payment_account,
        'bik': bik,
    }
    with open(PATH_TO_BUYER_INFO, 'w', encoding='utf-8') as file:
        json.dump(buyer_info, file, ensure_ascii=False, indent=4)
