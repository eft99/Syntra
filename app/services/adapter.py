from abc import ABC, abstractmethod


class ERPConnector(ABC):
    @abstractmethod
    async def get_remote_orders(self):
        pass


class ExcelAdapter(ERPConnector):
    async def get_remote_orders(self):
        return "Veriler Excel'den başarıyla simüle edildi."


class SAPAdapter(ERPConnector):
    async def get_remote_orders(self):
        return "Veriler SAP S/4HANA üzerinden çekildi (Simüle Edildi)."


def get_erp_adapter(env: str = "kobi") -> ERPConnector:
    if env == "enterprise":
        return SAPAdapter()
    return ExcelAdapter()
