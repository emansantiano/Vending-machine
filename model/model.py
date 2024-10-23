from sqlalchemy import Float, func, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# sqlalchemy declarative base class import to enable ORM
class Base(DeclarativeBase):
    pass

# Vending machine data entries object, inherits from Base to define
# define a SQLAlchemy model
class Vending_machine_entry(Base):
    """
    Represents a data entry for a product in a vending machine.

    Attributes:
        selection_code (str): Unique code for product selection (primary key).
        product_name (str): Name of the product.
        cost (float): Cost of the product.
        quantity (int): Available quantity of the product in stock.

    Methods:
        is_in_stock() -> bool:
            Checks if the product is currently in stock.

        try_purchase(money_inserted: float) -> Tuple[str, str]:
            Attempts to process a purchase based on the amount of money inserted.
            Returns a status indicating the outcome of the purchase attempt
            and a message providing further information.

        purchase() -> None:
            Decrements the available quantity of the product by one when a purchase is made.
    """
    __tablename__ = "vending_data"
    selection_code: Mapped[str] = mapped_column(primary_key=True)
    product_name: Mapped[str] = mapped_column(String(30))
    cost: Mapped[float]
    # have a max quantity that it can be?
    quantity: Mapped[int] = mapped_column()

    def is_in_stock(self):
        if self.quantity > 0:
            return True
        else:
            return False

    def try_purchase(self, money_inserted):
        if money_inserted < self.cost:
            rounded_outstanding = round(self.cost - money_inserted, 2)
            return "UNSOLD", f'Insufficient funds, please insert at least {rounded_outstanding}'
        elif money_inserted == self.cost:
            return "SOLD", f'Exact funds inserted, dispensing {self.product_name}'
        else:
            # excess funds inserted, need to handle this on
            return "EVALUATE", f'Excess funds inserted, dispensing {self.product_name} and returning £{money_inserted - self.cost}'

    def purchase(self):
        self.quantity -= 1

# Change data entries object, inherits from Base to define
# a SQLAlchemy model
class Change(Base):
    """
        Represents a data entry for the change available in a vending machine.

        Attributes:
            value (float): The monetary value of the change (primary key).
            quantity (int): The quantity of coins/bills of this value available.

        Methods:
            sum_costs(session: Session) -> float:
                Calculates the total value of all change entries in the database.
                Returns the sum of the product of each change value and its quantity.
    """
    __tablename__ = "change_data"
    value: Mapped[float] = mapped_column(Float, primary_key=True, index=True)
    # have a max quantity that it can be?
    quantity: Mapped[int] = mapped_column()

    @classmethod
    def sum_costs(cls, session):
        total_change = session.query(
            func.sum(cls.value * cls.quantity)).scalar()
        return total_change
