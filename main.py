import colorama
from colorama import Fore, Style
from persiantools.jdatetime import JalaliDateTime
from pymongo import MongoClient
from pymongo.collection import Collection

colorama.init()


class WalletManager:
    def __init__(self):
        self.client, self.collection = self.connect_to_mongodb()

    def connect_to_mongodb(self) -> tuple[MongoClient, Collection]:
        client = MongoClient("mongodb://localhost:27017")
        db = client["nobitex"]
        collection = db["wallet"]
        return client, collection

    def initialize_total_fund_key(self) -> None:
        if self.collection.count_documents({"_id": "total_fund"}) == 0:
            current_time = JalaliDateTime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.collection.insert_one(
                {"_id": "total_fund", "value": 0, "updated_at": current_time}
            )

    def initialize_total_stock_key(self) -> None:
        if self.collection.count_documents({"_id": "total_stock"}) == 0:
            current_time = JalaliDateTime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.collection.insert_one(
                {"_id": "total_stock", "value": 0, "updated_at": current_time}
            )
            print("Total stock initialized with the value of 0.")
        else:
            user_input = input(
                f"{Fore.YELLOW}Current total {Style.BRIGHT}Stock{Style.NORMAL}:\n{Fore.BLUE}press Enter to skip {Style.RESET_ALL}"
            )
            if user_input:
                try:
                    stock_value = int(user_input)
                    current_time = JalaliDateTime.now().strftime("%Y-%m-%d %H:%M:%S")
                    self.collection.update_one(
                        {"_id": "total_stock"},
                        {"$set": {"value": stock_value, "updated_at": current_time}},
                    )
                    print("Total stock updated successfully.")
                except ValueError:
                    print("Invalid input. No update for total stock.")

    def update_total_fund_key(self, number: int) -> None:
        current_time = JalaliDateTime.now().strftime("%Y-%m-%d %H:%M:%S")
        if number >= 0:
            self.collection.update_one(
                {"_id": "total_fund"},
                {"$inc": {"value": number}, "$set": {"updated_at": current_time}},
            )
        else:
            self.collection.update_one(
                {"_id": "total_fund"},
                {"$inc": {"value": -number}, "$set": {"updated_at": current_time}},
            )

    def retrieve_total_fund_value(self) -> int:
        total_fund_value = self.collection.find_one({"_id": "total_fund"})
        return total_fund_value

    def retrieve_total_stock_value(self) -> int:
        total_stock_value = self.collection.find_one({"_id": "total_stock"})
        return total_stock_value

    def close_mongodb_connection(self) -> None:
        self.client.close()

    def main(self) -> None:
        print(
            "Last total funds value:",
            self.retrieve_total_fund_value()["value"],
        )
        total_stock_value = self.retrieve_total_stock_value()["value"]
        total_stock_updated_at = self.retrieve_total_stock_value()["updated_at"]
        print(
            f"Last total stock value: {total_stock_value}\nLast update: {total_stock_updated_at}"
        )

        self.initialize_total_fund_key()
        self.initialize_total_stock_key()

        print("\n===== Update Funds =====")
        user_input = input(
            f"{Fore.YELLOW}Enter the updated amount (e.g., 1000 or -1000): {Style.RESET_ALL}"
        )

        if user_input:
            try:
                number = int(user_input)
                self.update_total_fund_key(number)
                print("Funds updated successfully.")
            except ValueError:
                print("Invalid input. No update on funds.")

        updated_total_fund = self.retrieve_total_fund_value()["value"]
        updated_total_stock = self.retrieve_total_stock_value()["value"]

        print("\n=== Current Status ===")
        print("Current total Funds value:", updated_total_fund)
        print("Current total Stock value:", updated_total_stock)

        total_profit = updated_total_fund - updated_total_stock

        if total_profit < 0:
            print(f"\nTotal Profit: {Fore.RED}{total_profit}{Style.RESET_ALL}")
        elif total_profit > 0:
            print(f"\nTotal Profit: {Fore.GREEN}{total_profit}{Style.RESET_ALL}")
        else:
            print("\nTotal Profit:", total_profit)

        self.close_mongodb_connection()


if __name__ == "__main__":
    wallet_manager = WalletManager()
    wallet_manager.main()
