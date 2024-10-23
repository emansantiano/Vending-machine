# Vending Machine API

This is a FastAPI application that simulates a vending machine, allowing users to interact with it to select products, check stock, and manage the balance of coins. The application uses a SQLite database to store product and change information.

## Features

- View available products and their quantities
- View available change in the vending machine
- Update stock for products in the vending machine
- Update the balance of coins in the machine
- Select products and manage user balance
- Handle transactions with error handling for out-of-stock items and invalid product codes

## Prerequisites

Make sure you have the following installed:

- Python 3.10.14
- pip (Python package manager)

## Installation

Create a pip venv in the project directory, as follows:

```bash
python -m venv venv
```
Activate the venv as so:

```bash
source venv/bin/activate
```
Then run this to install any needed packages
```bash
pip install -r requirements.txt 
```
to run the application, run in project directory:

```bash
fastapi dev main.py
```


## API Endpints. 
By default hosted at http://127.0.0.1:8000/
Go to http://127.0.0.1:8000/docs for easy interaction with the API without the need for Postman etc.

1. Show Stock
GET /stock/show_stock

Returns a list of all products currently in the vending machine.

2. Show Change Balance

GET /machine_balance/show_change

Returns the current change available in the vending machine.

3. Restock Products

PUT /stock/restock

Update the stock of products in the vending machine. Accepts either a single product or multiple products.

Request Body:

    Single Product:
e.g.
["A1", "Soda", 1.50, 10]

Multiple Products:
e.g.
    [
        ["A1", "Soda", 1.50, 10],
        ["B1", "Chips", 1.00, 5]
    ]

4. Update Change Balance

PUT /machine_balance/update/

Update the balance of coins in the machine. Accepts either a single coin entry or multiple entries.

Request Body:

    Single Coin:
e.g

[0.50, 20]

Multiple Coins:
e.g.
    [
        [0.50, 20],
        [1.00, 15]
    ]

5. Select Product

PUT /select_product

Select a product by its selection code. If the product is in stock, it prompts the user to insert money.

Request Body:
 e.g.
A1

(Any string selection code)

6. Cancel Transaction

PUT /cancel_transaction

Cancel the current transaction and reset the selection, returning any inserted money.

7. Get User Balance

GET /user_balance/

Returns the current balance of money inserted into the vending machine.

8. Update User Balance

POST /user_balance/update/

Insert a coin into the vending machine. Only accepts valid coin denominations. 
This can only be used after a user has selected a valid product. Once more enough change is inserted,
the product is returned and any change is also returned. The transaction stops if sufficient change
cannot be returned based on what the user has input

Request Body:

0.50

(Float of the coin value in poundse.g. 0.50, 1.0, 0.01 etc.)


## Testing
From project directory run:

pytest tests/

Unit tests will run and results will be returned

## Improvements/things that I was unable to do in the time given
Use Pydantic to validate inputs to the API, especially for populating new coins 
and vending machine entries

Testing:
-testing of API script (integration testing)
-more edge cases

General:
-password/basic auth to stop anyone being able to access the change and products in the vending machine
-better error code returns
-more edge case consideration
-more thorough documentation
-better commenting/docustrings

