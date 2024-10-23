import pytest

from vendingMachine import VendingMachine, SelectedCodeInvalidError, OutOfStockError
from model.model import Change, Vending_machine_entry

# Define a fixture vending machine for testing
@pytest.fixture(scope='module')
def test_machine():
    vendingMachine = VendingMachine('test', ':memory:')
    yield vendingMachine

# Check stock can be added
def test_stock_row(test_machine):
    # Create a new product instance

    test_machine.stock_row(
        selection_code="A1",
        product_name="Product",
        cost=1.99,
        quantity=10)

    # Fetch the product back from the database
    product = test_machine.session.get(Vending_machine_entry, "A1")

    # Assert the right product has been added
    assert product is not None
    assert product.selection_code == "A1"
    assert product.product_name == "Product"
    assert product.cost == 1.99
    assert product.quantity == 10

# Check coins can be added
def test_stock_change(test_machine):

    test_machine.restock_change(value=0.50, quantity=10)

    # Fetch the product back from the database
    coin = test_machine.session.get(Change, 0.5)
   
    # Assert the right coins have been added
    assert coin is not None
    assert coin.value == 0.5
    assert coin.quantity == 10

# Check can return user money
def test_return_money(test_machine):
    test_machine.money_cache = 2.0
    test_machine.return_money()
    assert test_machine.money_cache == 0

# Check can print stock data
def test_print_vending_data(test_machine):
    entries = test_machine.session.query(Vending_machine_entry).all()
    assert len(entries) == 1
    assert entries[0].selection_code == "A1"

# Check can print machine change data
def test_print_change_data(test_machine):
    entries = test_machine.session.query(Change).all()
    assert len(entries) == 1
    assert entries[0].value == 0.5

# Test can select existent item
def test_select_existent_product(test_machine):
    cost = test_machine.select_product('A1')
    assert isinstance(cost, float)

# Test can't select non-existent
def test_select_non_existent_product(test_machine):
    with pytest.raises(SelectedCodeInvalidError):
        test_machine.select_product('A2')

# Test can't select out of stock item
def test_select_out_of_stock_existent_product(test_machine):
    with pytest.raises(OutOfStockError):
        test_machine.stock_row(
            selection_code="A1",
            product_name="Product",
            cost=1.99,
            quantity=0)
        test_machine.select_product('A1')

# Repopulate item as removed temporarily for test
    test_machine.stock_row(
        selection_code="A1",
        product_name="Product",
        cost=1.99,
        quantity=10)

# Test balance doesn't when given too little change
def test_insert_insufficient_money(test_machine):
    product = test_machine.session.get(Vending_machine_entry, "A1")
    test_machine.money_cache = 0
    test_machine.selected_product = product
    _msg = test_machine.insert_money(0.01)
    assert test_machine.money_cache == 0.01

# Test balance resets when given exact change
def test_insert_exact_money(test_machine): 
    product = test_machine.session.get(Vending_machine_entry, "A1")
    test_machine.money_cache = 0
    test_machine.selected_product = product
    _msg = test_machine.insert_money(1.99)
    assert test_machine.money_cache == 0

# Test balance resets when given excess change
def test_insert_excess_money(test_machine): 
    product = test_machine.session.get(Vending_machine_entry, "A1")
    test_machine.money_cache = 0
    test_machine.selected_product = product
    _msg = test_machine.insert_money(2.00)
    assert test_machine.money_cache == 0

# Test returns change when it has sufficient change
def test_when_sufficient_change(test_machine):
    coin_list, _msg = test_machine.calculate_change_possibility(0.5)
    assert isinstance(coin_list, list)

# Test machine accurately rejects transaction when it doesn't
# have enough change
def test_when_insufficient_change(test_machine):
    coin_list, _msg = test_machine.calculate_change_possibility(0.15)
    assert coin_list is None

# Test machine accurately resets selection
def test_reset_selection(test_machine):
    test_machine.selected_product = Vending_machine_entry()
    test_machine.reset_selection()
    assert test_machine.selected_product is None

# Test machine accurately returns balance
def test_return_balance(test_machine):
    test_machine.money_cache = 1
    balance = test_machine.return_balance()
    assert balance == 1
