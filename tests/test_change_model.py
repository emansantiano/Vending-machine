import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from model.model import Base, Change

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

# Test adding a coin item to the database
def test_stock_item(test_db):
    # Create a new product instance
    new_product = Change(value=0.5, quantity=10)
    test_db.add(new_product)
    test_db.commit()

    # Fetch the product back from the database
    coin = test_db.query(Change).filter_by(value=0.5).first()
    # Check coin was added
    assert coin is not None
    assert coin.value == 0.5
    assert coin.quantity == 10

# Check class function can sum all change
def test_sum_table(test_db):
    # Create a new coin instance
    new_coin = Change(value=0.2, quantity=3)
    test_db.add(new_coin)
    test_db.commit()
    total_change = Change.sum_costs(test_db)

    assert round(total_change, 2) == 5.60
