import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from model.model import Base, Vending_machine_entry

# Define a fixture to set up the database for testing
@pytest.fixture(scope='module')
def test_db():
    # Create an in-memory SQLite database for testing
    engine = create_engine("sqlite:///:memory:")
    # Create the table defined in the model
    Base.metadata.create_all(engine)
    # Create a new session for database interactions
    Session = sessionmaker(bind=engine)
    session = Session()
    # Yield the session for use in tests
    yield session
    # Close the session and drop all tables after tests are done
    session.close()
    Base.metadata.drop_all(engine)

# Test adding an item to the database
def test_stock_item(test_db):

    new_product = Vending_machine_entry(
        selection_code="A1",
        product_name="Product",
        cost=1.99,
        quantity=10)
    test_db.add(new_product)
    test_db.commit()

    # Fetch the product back from the database
    product = test_db.query(Vending_machine_entry).filter_by(
        selection_code="A1").first()

    # Assert it is the right product
    assert product is not None
    assert product.selection_code == "A1"
    assert product.product_name == "Product"
    assert product.cost == 1.99
    assert product.quantity == 10

# Test adding an incorrectly defined item to the database
def test_stocking_product_with_incorrect_fields(test_db):
    print("testting")
    # Try to create a product with the wrong primary key field and check it fails
    with pytest.raises(Exception):
        faulty_entry = Vending_machine_entry(
            code="A1000", product_name="Product", cost=1.99, quantity=10)
        test_db.add(faulty_entry)
        test_db.commit()  # This should raise an exception
     # Rollback the change
    test_db.rollback()

# Check the vending machine can accurately calculate stock
def test_product_is_in_stock(test_db):
    # Create a product and update its quantity
    product = test_db.query(Vending_machine_entry).filter_by(
        selection_code="A1").first()
    in_stock = product.is_in_stock()

    assert in_stock is True

# Check the  machine won't vend when insufficient cash
def test_purchase_insufficient_cash(test_db):
    product = test_db.query(Vending_machine_entry).filter_by(
        selection_code="A1").first()
    status, _msg = product.try_purchase(1.50)

    assert status == "UNSOLD"

# Check the  machine will vend with exact cash
def test_purchase_exact_cash(test_db):
    product = test_db.query(Vending_machine_entry).filter_by(
        selection_code="A1").first()
    status, _msg = product.try_purchase(1.99)
    assert status == "SOLD"

# Check the  machine will calculate vending when excess cash
def test_purchase_excess_change(test_db):
    product = test_db.query(Vending_machine_entry).filter_by(
        selection_code="A1").first()
    status, _msg = product.try_purchase(2.00)
    assert status == "EVALUATE"
