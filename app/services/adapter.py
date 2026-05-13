from abc import ABC, abstractmethod
from app.config import settings

class ERPConnector(ABC):
    @abstractmethod
    async def get_remote_orders(self):
        pass

    @abstractmethod
    async def get_stock_data(self):
        pass

class ExcelAdapter(ERPConnector):
    async def get_remote_orders(self):
        return {
            "source": "excel",
            "status": "success",
            "orders": [
                {
                    "order_id": "XL-1001",
                    "customer": "Local Market",
                    "status": "pending"
                },
                {
                    "order_id": "XL-1002",
                    "customer": "Coffee Shop",
                    "status": "processing"
                }
            ]
        }
    async def get_stock_data(self):

        return {
            "source": "excel",
            "warehouse_status": "local_file_system",
            "products": 58
        }

class SAPAdapter(ERPConnector):
    async def get_remote_orders(self):
         return {
            "source": "sap_s4hana",
            "status": "connected",
            "orders": [
                {
                    "order_id": "SAP-9001",
                    "customer": "Enterprise Retail",
                    "status": "approved"
                },
                {
                    "order_id": "SAP-9002",
                    "customer": "Global Foods",
                    "status": "waiting_supply"
                }
            ]
        }

    async def get_stock_data(self):

        return {
            "source": "sap_s4hana",
            "warehouse_status": "enterprise_sync_active",
            "products": 1248
        }


def get_erp_adapter():

    if settings.ERP_MODE == "enterprise":
        return SAPAdapter()

    return ExcelAdapter()
