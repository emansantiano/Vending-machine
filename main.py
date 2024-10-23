import uvicorn

from fastapi import FastAPI, HTTPException

from typing import List, Union, Tuple


from vendingMachine import (
    VendingMachine,
    SelectedCodeInvalidError,
    OutOfStockError,
)

# Initialize the Vending Machine instance with a name and the database path
vending_machine = VendingMachine("dev_vending_machine", "test.db")
app = FastAPI()

# Endpoint to list the products in the vending machine
@app.get("/stock/show_stock")
def list_vending_contents():
    data = vending_machine.print_vending_data()
    return data

# Endpoint to list the change in the vending machine
@app.get("/machine_balance/show_change")
def list_change_contents():
    data = vending_machine.print_change_data()
    return data

# Endpoint to update the vending machine stock, either one entry at a time
# or multiple
@app.put("/stock/restock")
def update_vending_data(
    data: Union[List[Tuple[str, str, float, int]], Tuple[str, str, float, int]]
):
    # If multiple entries are set to update at once
    if all(isinstance(i, tuple) for i in data):
        for row in data:
            try:
                # Unpack the row into respective variables
                selection_code = row[0]
                product_name = row[1]
                cost = row[2]
                quantity = row[3]

                # Stock the vending machine row with provided data
                msg = vending_machine.stock_row(
                    selection_code, product_name, cost, quantity
                )
            except Exception as e:
                return {"error": f"Error occurred: {e}"}    # Return any errors

    # If just one entry is set to update
    else:
        try:
            selection_code = data[0]
            product_name = data[1]
            cost = data[2]
            quantity = data[3]
            vending_machine.stock_row(
                selection_code, product_name, cost, quantity)
        except Exception as e:
            return {"error": f"Error occurred: {e}"}    # Return any errors
    return {
        'details': 'Desired machine rows stocked to set quantities, items and prices'}


# Endpoint to update the machine's change balance
@app.put("/machine_balance/update/")
def update_machine_balance(
        data: Union[List[Tuple[float, int]], Tuple[float, int]]):
    # If multiple entries are set to update at once
    if all(isinstance(i, tuple) for i in data):
        for row in data:
            try:
                value = row[0]
                quantity = row[1]
                vending_machine.restock_change(
                    value, quantity)  # Update the change balance
            except Exception as e:
                return {"error": f"Error occurred: {e}"}  # Return any error
    # If only one entry to update
    else:
        try:
            value = data[0]
            quantity = data[1]
            vending_machine.restock_change(
                value, quantity)  # Update the change balance
        except Exception as e:
            return {"error": f"Error occurred: {e}"}
    return {'details': 'Desired coins stocked to inputted quantities'}


# Endpoint to check if a product is in stock and if so select it
@app.put("/select_product")
def check_stock(selection_code):
    try:
        cost = vending_machine.select_product(selection_code)
        return {
            "details": (
                f"Item is in stock and costs {cost}, "
                "please insert cash to continue"
            )
        }
    except SelectedCodeInvalidError as e:
        # Raise 404 for invalid selection code
        raise HTTPException(status_code=404, detail=str(e))
    except OutOfStockError as e:
        # Raise 404 for item out of stock
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred with your request: {e}"
        )   # Raise 500 for any other errors

# Endpoint to cancel a transaction
@app.put("/cancel_transaction")
def cancel_transaction():
    # Reset the current selection and return change
    msg = vending_machine.reset_selection()
    return {'details': f'{msg}'}

# Endpoint to get the user's balance
@app.get("/user_balance/")
def get_user_balance():
    balance = vending_machine.return_balance()
    return {"balance": f'{balance}'}

# Endpoint to update the user's balance with inserted coins
@app.post("/user_balance/update/")
def update_user_balance(coin: float):
    if coin not in [0.01, 0.02, 0.05, 0.1, 0.2, 0.5,
                    1, 2]:    # Check it is a valid denomination
        return {'details': "Not a valid coin, item has been returned"}
    # If a product has been selected, allow the user to proceed
    if vending_machine.selected_product is not None:
        try:
            output = vending_machine.insert_money(coin)   # Insert the coin
            return {'details': f'{output}'}
        except Exception as e:
            return {"error": f"Error occurred: {e}"}
    else:
        # Prompt user to select a product first and return their coin
        return {'details': "Please select a product first. Change returned"}


# Main entry point to run the FastAPI application
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)   # Start the server
