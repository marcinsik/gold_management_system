# Gold Warehouse - Desktop Application

## Description
A desktop application for managing a gold warehouse, written in Python using the Tkinter (GUI) and SQLite3 (database) libraries. The program works offline and allows for full management of gold stocks and transaction history.

## Features

### Main window (Warehouse)
- Displays a table with the current gold warehouse inventory
- Columns: Gold Type, Unit Weight (g), Purity (%), Quantity, Total Weight (g)
- Buttons: Add New Gold, Buy Gold, Sell Gold, Show Transaction History, Exit

### Gold type management
- Adding new gold types (bars, coins, etc.)
- Validation of type uniqueness
- Data validity check (weight, purity)

### Transactions
- **Buying gold**: Adding gold to the warehouse
- **Selling gold**: Removing gold from the warehouse (with availability check)
- Automatic updating of warehouse stocks
- Saving the full transaction history

### Transaction history
- Full history of all transactions
- Display: Date, Gold Type, Transaction Type, Quantity, Price, Value, Description
- Chronological sorting (most recent at the top)

## Requirements
- Python 3.7+
- Libraries: tkinter, sqlite3 (built into Python)

## Installation and launch

1. Copy the `gold_vault.py` and `database.py` files to a single directory
2. Launch the program:
```bash
   python gold_vault.py
   ```

## Database structure

### `inventory` table
- `id`: Primary key
- `type`: Gold type (unique)
- `unit_weight`: Unit weight in grams
- `purity`: Purity in percent
- `quantity`: Quantity in stock

### `transactions` table
- `id`: Primary key
- `gold_type_id`: Reference to gold type
- `transaction_type`: “Purchase” or “Sale”
- `quantity`: Transaction quantity
- `price_per_unit`: Price per unit
- `transaction_date`: Transaction date
- `description`: Transaction description

## Database file
The database is automatically created in the `gold_vault.db` file in the program directory.
