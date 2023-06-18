import locale

import colorama
from colorama import Fore, Style
from persiantools.jdatetime import JalaliDateTime
from pymongo import MongoClient
from pymongo.collection import Collection

colorama.init()
locale.setlocale(locale.LC_ALL, "")


class Database:
    def __init__(self):
        self.client = MongoClient("mongodb://localhost:27017")
        self.db = self.client["test-wallet-client"]
        self.collection = self.db["wallet"]

    def close_connection(self):
        self.client.close()


class KeyInitializer:
    def __init__(self, collection: Collection):
        self.collection = collection

    def initialize_key(self, key: str, initial_value: int):
        if self.collection.count_documents({"_id": key}) == 0:
            current_time = JalaliDateTime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.collection.insert_one(
                {"_id": key, "value": initial_value, "updated_at": current_time}
            )


class KeyUpdater:
    def __init__(self, collection: Collection):
        self.collection = collection

    def update_key(self, key: str, number: int):
        current_time = JalaliDateTime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.collection.update_one(
            {"_id": key},
            {"$inc": {"value": number}, "$set": {"updated_at": current_time}},
        )

    def set_key(self, key: str, number: int):
        current_time = JalaliDateTime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.collection.update_one(
            {"_id": key},
            {"$set": {"value": number, "updated_at": current_time}},
        )


class KeyRetriever:
    def __init__(self, collection: Collection):
        self.collection = collection

    def retrieve_key_value(self, key: str):
        key_value = self.collection.find_one({"_id": key})
        return key_value


class WalletManager:
    def __init__(self):
        self.database = Database()
        self.collection = self.database.collection
        self.key_initializer = KeyInitializer(self.collection)
        self.key_updater = KeyUpdater(self.collection)
        self.key_retriever = KeyRetriever(self.collection)

    def main(self) -> None:
        self.key_initializer.initialize_key("total_fund", 0)
        self.key_initializer.initialize_key("total_stock", 0)

        total_stock_value = locale.format_string(
            f="%d",
            grouping=True,
            val=self.key_retriever.retrieve_key_value("total_stock")["value"],
        )
        total_stock_updated_at = self.key_retriever.retrieve_key_value("total_stock")[
            "updated_at"
        ]
        total_fund_value = self.key_retriever.retrieve_key_value("total_fund")["value"]
        print(
            "Last total funds value:",
            locale.format_string(
                f="%d",
                grouping=True,
                val=total_fund_value,
            ),
        )

        print(
            f"Last total stock value: {total_stock_value}\nLast update: {total_stock_updated_at}"
        )

        print("\n===== Update Funds =====")
        fund_input = input(
            f"{Fore.YELLOW}Enter the updated amount (e.g., 1000 or -1000 or reset): {Style.RESET_ALL}"
        )

        if fund_input:
            try:
                if fund_input == "reset":
                    self.key_updater.set_key("total_fund", 0)
                    print("Funds reset successfully.")
                else:
                    number = int(fund_input)
                    self.key_updater.update_key("total_fund", number)
                    print("Funds updated successfully.")
            except ValueError:
                print("Invalid input. No update on funds.")

        updated_total_fund = self.key_retriever.retrieve_key_value("total_fund")[
            "value"
        ]
        updated_total_stock = self.key_retriever.retrieve_key_value("total_stock")[
            "value"
        ]
        print("\n===== Update Stocks =====")
        stock_input = input(
            f"{Fore.YELLOW}Current total {Style.BRIGHT}Stock{Style.NORMAL}:\n{Fore.BLUE}press Enter to skip {Style.RESET_ALL}"
        )
        if stock_input:
            try:
                stock_value = int(stock_input)
                self.key_updater.set_key("total_stock", stock_value)
                print("Stock updated successfully.")
            except ValueError:
                print("Invalid input. No update for total stock.")

        updated_total_fund = self.key_retriever.retrieve_key_value("total_fund")[
            "value"
        ]
        updated_total_stock = self.key_retriever.retrieve_key_value("total_stock")[
            "value"
        ]

        print("\n=== Current Status ===")
        print(
            "Current total Funds value:",
            locale.format_string(f="%d", grouping=True, val=updated_total_fund),
        )
        print(
            "Current total Stock value:",
            locale.format_string(f="%d", grouping=True, val=updated_total_stock),
        )

        total_profit = updated_total_stock - updated_total_fund
        total_profit_locale = locale.format_string(
            f="%d", grouping=True, val=total_profit
        )

        if total_profit < 0:
            print(f"\nTotal Profit: {Fore.RED}{total_profit_locale}{Style.RESET_ALL}")
        elif total_profit > 0:
            print(f"\nTotal Profit: {Fore.GREEN}{total_profit_locale}{Style.RESET_ALL}")
        else:
            print("\nTotal Profit:", total_profit_locale)

        self.database.close_connection()


if __name__ == "__main__":
    wallet_manager = WalletManager()
    wallet_manager.main()
