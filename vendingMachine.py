from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from model.model import Base, Change, Vending_machine_entry


class OutOfStockError(Exception):
    """Exception raised when a selected product is out of stock."""
    pass


class SelectedCodeInvalidError(Exception):
    """Exception raised when an invalid product selection code is provided."""
    pass


class VendingMachine:
    """
    A class to represent a vending machine.

    This class manages the vending machine's operations, including stocking items,
    processing purchases, and managing change. It interacts with a database to store
    product and change data.

    Attributes:
        vending_machine_name (str): The name of the vending machine.
        vending_db_file_path (str): The file path for the SQLite database.
        engine (Engine): The SQLAlchemy engine used to connect to the database.
        Session (sessionmaker): A factory for creating new session objects.
        session (Session): The current database session.
        money_cache (float): The amount of money currently inserted into the machine.
        selected_product (Vending_machine_entry): The currently selected product.
    """

    def __init__(self, vending_machine_name, vending_db_file_path):
        """
        Initializes the VendingMachine instance.

        Args:
            vending_machine_name (str): The name of the vending machine.
            vending_db_file_path (str): The file path for the SQLite database.
        """
        self.vending_machine_name = vending_machine_name
        self.vending_db_file_path = vending_db_file_path
        # DB created if it doesn't exist
        self.engine = create_engine(
            f"sqlite:///{self.vending_db_file_path}", echo=True)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        Base.metadata.create_all(self.engine)
        self.money_cache = 0  # Balance user has put in the machine
        self.selected_product = None

    def stock_row(self, selection_code, product_name, cost, quantity):
        """
        Stocks or updates a product entry in the vending machine.

        Args:
            selection_code (str): The code for the product selection.
            product_name (str): The name of the product.
            cost (float): The price of the product.
            quantity (int): The quantity of the product.

        Returns:
            str: A message indicating the result of the operation.
        """
        try:
            product_row = Vending_machine_entry(
                selection_code=selection_code,
                product_name=product_name,
                cost=cost,
                quantity=quantity,
            )
            self.session.merge(product_row)
            self.session.commit()   # Commit result to table
            return f"Stock row {selection_code} updated"
        except Exception as e:
            self.session.rollback() # Rollback change on error
            return f"Error occurred: {e}"

    def restock_change(self, value, quantity):
        """
        Restocks the change available in the vending machine.

        Args:
            value (float): The value of the coin.
            quantity (int): The number of coins to add.

        Returns:
            str: A message indicating the result of the operation.
        """
        try:
            product_row = Change(value=value, quantity=quantity)
            self.session.merge(product_row)
            self.session.commit()
            return f"Coin ${value} topped up to {quantity} coins"
        except Exception as e:
            self.session.rollback()
            return f"Error occurred: {e}"


    def return_money(self):
        """
        Returns any money currently cached in the machine.

        Returns:
            str: A message indicating the result of the operation.
        """
        if self.money_cache > 0:
            self.money_cache = 0
            return "Money inserted has been returned"
        else:
            return "No money to return"

    def print_vending_data(self):
        """
        Retrieves and returns all product entries in the vending machine.

        Returns:
            list: A list of Vending_machine_entry objects.
        """
        entries = (
            self.session.query(Vending_machine_entry)
            .order_by(Vending_machine_entry.selection_code.asc())
            .all()
        )
        return entries

    def print_change_data(self):
        """
        Retrieves and returns all coin entries in the vending machine.

        Returns:
            list: A list of Change objects.
        """
        entries = self.session.query(Change).all()
        return entries

    def select_product(self, selection_code):
        """
        Selects a product based on the provided selection code.

        Args:
            selection_code (str): The code for the selected product.

        Returns:
            float: The cost of the selected product.

        Raises:
            SelectedCodeInvalidError: If the selection code is invalid.
            OutOfStockError: If the selected product is out of stock.
        """
        product = self.session.get(Vending_machine_entry, selection_code)
        if product is None:
            raise SelectedCodeInvalidError(
                "Selected product code is not valid")
        elif product.quantity == 0:
            raise OutOfStockError("Item is out of stock")
        else:
            self.selected_product = product
            return product.cost

    def insert_money(self, inserted_amount):
        """
        Inserts money into the vending machine and attempts to purchase the selected product.

        Args:
            inserted_amount (float): The amount of money inserted.

        Returns:
            str: A message indicating the result of the purchase attempt.
        """
        self.money_cache += inserted_amount
        status, msg = self.selected_product.try_purchase(self.money_cache)
        # If insufficient funds inserted
        if status == "UNSOLD":
            return msg
        # If exact funds inserted
        elif status == "SOLD":
            self.selected_product.purchase()
            self.selected_product = None
            self.money_cache = 0
            self.session.commit()
            return msg
        # If change required
        if status == "EVALUATE":
            # return required change here
            possible, msg = self.check_enough_change()
            # Is exact change possible
            if possible:
                self.selected_product.purchase()
                self.selected_product = None
                self.money_cache = 0
                return msg
            else:
                self.money_cache = 0
                return msg

    def check_enough_change(self):
        """
        Checks if there is enough change available to give back after a purchase.

        Returns:
            tuple: A tuple containing a boolean indicating success and a message.
        """
        required_change = self.money_cache - self.selected_product.cost
        required_change = round(required_change, 2) # Round to avoid float errors
        # Total change in the machine
        total_change_available = Change.sum_costs(self.session)
        
        # If no change has been loaded into the machine
        if total_change_available is None:
            print(1)
            return (
                False,
                "No change in the machine, please speak to admins. Coin being returned",
            )
        # If insufficient change is in machine
        elif total_change_available < required_change:
            return False, "Not enough change in machine, inserted coins being returned"
        else:
            change_list, msg = self.calculate_change_possibility(
                required_change)
            print(change_list)
            # If change can be given, dispense it and update the quantity in the machine
            if change_list is not None:
                for coin in change_list:
                    coin.quantity -= 1
                self.session.commit()  # Commit changes to table

                return (
                    True,
                    f"Enough change in machine, product dispensing and £{required_change} being returned",
                )

            else:
                self.money_cache = 0
                return (
                    False,
                    "Not enough change in machine, inserted coins being returned",
                )

    def calculate_change_possibility(self, change_required):
        """
        Calculates the possibility of providing change for a given amount.

        Args:
            change_required (float): The amount of change needed.

        Returns:
            tuple: A tuple containing a list of coins for change and a message.
        """
        # Implements a greedy algorithm to assess whether change can easily be 
        # provided, given the current coins available in the machine
        change_list = []
        coin_table = self.session.query(
            Change).order_by(Change.value.desc()).all()
        # Iterate through the coins of the table, minusing their value from
        # the required change, until they run out or are larger than the 
        # remaining required change
        for coin in coin_table:
            while change_required >= round(
                    coin.value, 2) and coin.quantity > 0:
                if change_required >= round(coin.value, 2):
                    change_list.append(coin)
                    change_required -= coin.value
                    change_required = round(change_required, 2)

        # If change cannot be fulfilled via greedy algo
        if change_required > 0:
            print(change_required)
            return None, "Change not possible not possible"

        return change_list, "Change available"

   
    def reset_selection(self):
        self.money_cache = 0
        self.selected_product = None
        return "Any selection cancelled and any money returned"

    def return_balance(self):
        balance = self.money_cache
        return balance