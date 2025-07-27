import sqlite3
import os
import re
from datetime import datetime
from typing import List, Dict, Optional, Tuple

def natural_sort_key(text):
    """
    Funkcja pomocnicza do sortowania naturalnego (numerycznego).
    Konwertuje ciągi znaków zawierające liczby na odpowiednie klucze sortowania.
    Np. 'Sztabka 1g', 'Sztabka 2g', 'Sztabka 10g' będą posortowane w tej kolejności.
    """
    def convert(text_part):
        return int(text_part) if text_part.isdigit() else text_part.lower()
    
    # Podziel tekst na części alfanumeryczne
    return [convert(c) for c in re.split('([0-9]+)', str(text))]

class GoldDatabase:
    """Klasa odpowiedzialna za zarządzanie bazą danych złota."""
    
    def __init__(self, db_name: str = "gold_vault.db"):
        """Inicjalizuje połączenie z bazą danych."""
        self.db_name = db_name
        self.init_database()
    
    def init_database(self):
        """Tworzy tabele bazy danych jeśli nie istnieją."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                
                # Sprawdź czy tabela inventory istnieje i ma starą strukturę
                cursor.execute("PRAGMA table_info(inventory)")
                columns = [column[1] for column in cursor.fetchall()]
                
                if columns and 'category' not in columns:
                    # Tabela istnieje ale ma starą strukturę - migracja
                    print("Migracja bazy danych...")
                    
                    # Utwórz nową tabelę z nową strukturą
                    cursor.execute("""
                        CREATE TABLE inventory_new (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            category TEXT NOT NULL DEFAULT 'Złom',
                            type TEXT NOT NULL,
                            unit_weight REAL NOT NULL,
                            purity REAL NOT NULL,
                            quantity REAL NOT NULL DEFAULT 0,
                            unit TEXT NOT NULL DEFAULT 'szt',
                            notes TEXT,
                            UNIQUE(category, type, purity)
                        )
                    """)
                    
                    # Skopiuj dane ze starej tabeli
                    cursor.execute("""
                        INSERT INTO inventory_new (type, unit_weight, purity, quantity, category, unit, notes)
                        SELECT type, unit_weight, purity, quantity, 'Złom', 'szt', ''
                        FROM inventory
                    """)
                    
                    # Usuń starą tabelę i zmień nazwę nowej
                    cursor.execute("DROP TABLE inventory")
                    cursor.execute("ALTER TABLE inventory_new RENAME TO inventory")
                    
                    print("Migracja zakończona.")
                else:
                    # Tabela inventory - nowa struktura
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS inventory (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            category TEXT NOT NULL,
                            type TEXT NOT NULL,
                            unit_weight REAL NOT NULL,
                            purity REAL NOT NULL,
                            quantity REAL NOT NULL DEFAULT 0,
                            unit TEXT NOT NULL DEFAULT 'szt',
                            notes TEXT,
                            UNIQUE(category, type, purity)
                        )
                    """)
                
                # Sprawdź czy tabela transactions istnieje i ma starą strukturę
                cursor.execute("PRAGMA table_info(transactions)")
                trans_columns = [column[1] for column in cursor.fetchall()]
                
                if trans_columns and 'weight_total' not in trans_columns:
                    # Tabela transactions istnieje ale ma starą strukturę - migracja
                    print("Migracja tabeli transactions...")
                    
                    # Utwórz nową tabelę z nową strukturą
                    cursor.execute("""
                        CREATE TABLE transactions_new (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            gold_type_id INTEGER,
                            transaction_type TEXT NOT NULL CHECK(transaction_type IN ('Kupno', 'Sprzedaż')),
                            quantity REAL NOT NULL,
                            weight_total REAL,
                            price_per_unit REAL NOT NULL,
                            price_per_gram REAL,
                            transaction_date TEXT NOT NULL,
                            description TEXT,
                            FOREIGN KEY (gold_type_id) REFERENCES inventory(id)
                        )
                    """)
                    
                    # Skopiuj dane ze starej tabeli
                    cursor.execute("""
                        INSERT INTO transactions_new (gold_type_id, transaction_type, quantity, price_per_unit, transaction_date, description)
                        SELECT gold_type_id, transaction_type, quantity, price_per_unit, transaction_date, description
                        FROM transactions
                    """)
                    
                    # Usuń starą tabelę i zmień nazwę nowej
                    cursor.execute("DROP TABLE transactions")
                    cursor.execute("ALTER TABLE transactions_new RENAME TO transactions")
                    
                    print("Migracja tabeli transactions zakończona.")
                else:
                    # Tabela transactions - rozszerzona o wagę i jednostkę
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS transactions (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            gold_type_id INTEGER,
                            transaction_type TEXT NOT NULL CHECK(transaction_type IN ('Kupno', 'Sprzedaż')),
                            quantity REAL NOT NULL,
                            weight_total REAL,
                            price_per_unit REAL NOT NULL,
                            price_per_gram REAL,
                            transaction_date TEXT NOT NULL,
                            description TEXT,
                            FOREIGN KEY (gold_type_id) REFERENCES inventory(id)
                        )
                    """)
                
                conn.commit()
        except sqlite3.Error as e:
            print(f"Błąd inicjalizacji bazy danych: {e}")
            raise
    
    def add_gold_type(self, category: str, gold_type: str, unit_weight: float, purity: float, unit: str = "szt", notes: str = "") -> bool:
        """Dodaje nowy typ złota do bazy danych."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO inventory (category, type, unit_weight, purity, unit, notes) VALUES (?, ?, ?, ?, ?, ?)",
                    (category, gold_type, unit_weight, purity, unit, notes)
                )
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False  # Kombinacja już istnieje
        except sqlite3.Error as e:
            print(f"Błąd dodawania typu złota: {e}")
            return False
    
    def get_inventory(self, sort_by: str = "category") -> List[Tuple]:
        """Pobiera aktualny stan magazynu z możliwością sortowania."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                
                # Pobierz wszystkie dane
                cursor.execute("""
                    SELECT category, type, unit_weight, purity, quantity, unit,
                           (unit_weight * quantity) as total_weight,
                           notes
                    FROM inventory
                """)
                inventory = cursor.fetchall()
                
                # Sortowanie w Pythonie dla lepszej kontroli nad sortowaniem numerycznym
                if sort_by == "category":
                    inventory.sort(key=lambda x: (x[0], -x[3], natural_sort_key(x[1])))  # kategoria, czystość DESC, typ numerycznie
                elif sort_by == "type":
                    inventory.sort(key=lambda x: (natural_sort_key(x[1]), -x[3]))  # typ numerycznie, czystość DESC
                elif sort_by == "purity":
                    inventory.sort(key=lambda x: (-x[3], x[0], natural_sort_key(x[1])))  # czystość DESC, kategoria, typ numerycznie
                elif sort_by == "quantity":
                    inventory.sort(key=lambda x: (-x[4], x[0], natural_sort_key(x[1])))  # ilość DESC, kategoria, typ numerycznie
                elif sort_by == "weight":
                    inventory.sort(key=lambda x: (-x[6], x[0], natural_sort_key(x[1])))  # waga DESC, kategoria, typ numerycznie
                else:
                    inventory.sort(key=lambda x: (x[0], -x[3], natural_sort_key(x[1])))  # domyślnie jak kategoria
                
                return inventory
        except sqlite3.Error as e:
            print(f"Błąd pobierania magazynu: {e}")
            return []
    
    def get_gold_types(self) -> List[Tuple]:
        """Pobiera listę typów złota z ID oraz dodatkowymi informacjami."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, category, type, purity, unit FROM inventory")
                gold_types = cursor.fetchall()
                
                # Sortowanie numeryczne
                gold_types.sort(key=lambda x: (x[1], natural_sort_key(x[2]), -x[3]))  # kategoria, typ numerycznie, czystość DESC
                
                return gold_types
        except sqlite3.Error as e:
            print(f"Błąd pobierania typów złota: {e}")
            return []
    
    def get_gold_quantity(self, gold_type_id: int) -> float:
        """Pobiera dostępną ilość danego typu złota."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT quantity FROM inventory WHERE id = ?", (gold_type_id,))
                result = cursor.fetchone()
                return result[0] if result else 0
        except sqlite3.Error as e:
            print(f"Błąd pobierania ilości złota: {e}")
            return 0
    
    def get_gold_categories(self) -> List[str]:
        """Pobiera listę unikalnych kategorii złota."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT DISTINCT category FROM inventory ORDER BY category")
                return [row[0] for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Błąd pobierania kategorii złota: {e}")
            return []

    def add_transaction(self, gold_type_id: int, transaction_type: str, 
                       quantity: float, price_per_unit: float, 
                       transaction_date: str, description: str = "") -> bool:
        """Dodaje transakcję i aktualizuje stan magazynu."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                
                # Sprawdź dostępność przy sprzedaży
                if transaction_type == "Sprzedaż":
                    current_quantity = self.get_gold_quantity(gold_type_id)
                    if current_quantity < quantity:
                        return False
                
                # Pobierz dane o złocie dla obliczenia wag
                cursor.execute("SELECT unit_weight FROM inventory WHERE id = ?", (gold_type_id,))
                result = cursor.fetchone()
                if not result:
                    return False
                
                unit_weight = result[0]
                weight_total = quantity * unit_weight
                price_per_gram = price_per_unit / unit_weight if unit_weight > 0 else 0
                
                # Dodaj timestamp do daty jeśli nie ma czasu
                if len(transaction_date) == 10:  # Format YYYY-MM-DD
                    transaction_date = f"{transaction_date} {datetime.now().strftime('%H:%M:%S')}"
                
                # Dodaj transakcję
                cursor.execute("""
                    INSERT INTO transactions 
                    (gold_type_id, transaction_type, quantity, weight_total, price_per_unit, price_per_gram, transaction_date, description)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (gold_type_id, transaction_type, quantity, weight_total, price_per_unit, price_per_gram, transaction_date, description))
                
                # Aktualizuj stan magazynu
                quantity_change = quantity if transaction_type == "Kupno" else -quantity
                cursor.execute("""
                    UPDATE inventory 
                    SET quantity = quantity + ? 
                    WHERE id = ?
                """, (quantity_change, gold_type_id))
                
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Błąd dodawania transakcji: {e}")
            return False
    
    def get_transaction_by_id(self, transaction_id: int) -> Optional[Tuple]:
        """Pobiera szczegóły transakcji po ID."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT t.id, t.gold_type_id, i.category, i.type, i.purity, 
                           t.transaction_type, t.quantity, t.price_per_unit, 
                           t.transaction_date, t.description
                    FROM transactions t
                    JOIN inventory i ON t.gold_type_id = i.id
                    WHERE t.id = ?
                """, (transaction_id,))
                return cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Błąd pobierania transakcji: {e}")
            return None
    
    def get_transactions_with_id(self, sort_by: str = "date", date_from: Optional[str] = None, date_to: Optional[str] = None) -> List[Tuple]:
        """Pobiera wszystkie transakcje z ID, z opcjonalnym filtrowaniem daty dla głównego okna."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                query = """
                    SELECT 
                        t.id, t.transaction_date, gt.category, gt.type, gt.purity, 
                        t.transaction_type, t.quantity, t.price_per_unit, 
                        (t.quantity * t.price_per_unit) as total_value, 
                        t.description, t.gold_type_id
                    FROM transactions t
                    JOIN inventory gt ON t.gold_type_id = gt.id
                """
                
                conditions = []
                params = []
                
                if date_from and date_from != "RRRR-MM-DD":
                    conditions.append("t.transaction_date >= ?")
                    params.append(date_from)
                if date_to and date_to != "RRRR-MM-DD":
                    conditions.append("t.transaction_date <= ?")
                    params.append(date_to)
                    
                if conditions:
                    query += " WHERE " + " AND ".join(conditions)

                sort_mapping = {
                    "date": "t.transaction_date DESC",
                    "type": "gt.category, gt.type",
                    "value": "total_value DESC",
                    "transaction_type": "t.transaction_type"
                }
                
                order_by_clause = sort_mapping.get(sort_by, "t.transaction_date DESC")
                query += f" ORDER BY {order_by_clause}"
                
                cursor.execute(query, params)
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Błąd pobierania transakcji: {e}")
            return []

    def get_all_transactions_for_history(self, sort_by: str = "date", filters: Optional[dict] = None) -> List[Tuple]:
        """Pobiera transakcje dla okna historii z zaawansowanym filtrowaniem."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                query = """
                    SELECT 
                        t.id, t.transaction_date, gt.category, gt.type, gt.purity, 
                        t.transaction_type, t.quantity, gt.unit, t.weight_total, 
                        t.price_per_unit, t.price_per_gram,
                        (t.quantity * t.price_per_unit) as total_value, 
                        t.description
                    FROM transactions t
                    JOIN inventory gt ON t.gold_type_id = gt.id
                """
                
                conditions = []
                params = []
                
                if filters:
                    date_from = filters.get("date_from")
                    date_to = filters.get("date_to")
                    category = filters.get("category")
                    trans_type = filters.get("trans_type")

                    if date_from and date_from != "RRRR-MM-DD":
                        conditions.append("t.transaction_date >= ?")
                        params.append(date_from)
                    if date_to and date_to != "RRRR-MM-DD":
                        conditions.append("t.transaction_date <= ?")
                        params.append(date_to)
                    if category and category != "Wszystkie":
                        conditions.append("gt.category = ?")
                        params.append(category)
                    if trans_type and trans_type != "Wszystkie":
                        conditions.append("t.transaction_type = ?")
                        params.append(trans_type)

                if conditions:
                    query += " WHERE " + " AND ".join(conditions)

                sort_mapping = {
                    "date": "t.transaction_date DESC",
                    "type": "gt.category, gt.type",
                    "value": "total_value DESC",
                    "transaction_type": "t.transaction_type"
                }
                
                order_by_clause = sort_mapping.get(sort_by, "t.transaction_date DESC")
                query += f" ORDER BY {order_by_clause}"
                
                cursor.execute(query, params)
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Błąd pobierania historii transakcji: {e}")
            return []

    def update_transaction(self, transaction_id: int, gold_type_id: int, quantity: float, price_per_unit: float, transaction_date: str, description: str) -> bool:
        """Aktualizuje istniejącą transakcję."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                
                old_transaction = cursor.execute("SELECT gold_type_id, transaction_type, quantity FROM transactions WHERE id = ?", (transaction_id,)).fetchone()
                if not old_transaction: return False
                
                old_gold_id, transaction_type, old_quantity = old_transaction
                
                # Revert old transaction from inventory
                quantity_change_old = -old_quantity if transaction_type == "Kupno" else old_quantity
                cursor.execute("UPDATE inventory SET quantity = quantity + ? WHERE id = ?", (quantity_change_old, old_gold_id))
                
                # Check availability for the new transaction if it's a sale
                if transaction_type == "Sprzedaż":
                    current_quantity_new_type = cursor.execute("SELECT quantity FROM inventory WHERE id = ?", (gold_type_id,)).fetchone()[0]
                    if current_quantity_new_type < quantity:
                        # Rollback inventory change and exit
                        cursor.execute("UPDATE inventory SET quantity = quantity - ? WHERE id = ?", (quantity_change_old, old_gold_id))
                        conn.commit()
                        return False
                
                # Get gold data for weight calculation
                unit_weight = cursor.execute("SELECT unit_weight FROM inventory WHERE id = ?", (gold_type_id,)).fetchone()[0]
                weight_total = quantity * unit_weight
                price_per_gram = price_per_unit / unit_weight if unit_weight > 0 else 0
                
                # Update transaction details
                cursor.execute("""
                    UPDATE transactions 
                    SET gold_type_id = ?, quantity = ?, weight_total = ?, price_per_unit = ?, price_per_gram = ?, transaction_date = ?, description = ?
                    WHERE id = ?
                """, (gold_type_id, quantity, weight_total, price_per_unit, price_per_gram, transaction_date, description, transaction_id))
                
                # Apply new transaction to inventory
                quantity_change_new = quantity if transaction_type == "Kupno" else -quantity
                cursor.execute("UPDATE inventory SET quantity = quantity + ? WHERE id = ?", (quantity_change_new, gold_type_id))
                
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Błąd aktualizacji transakcji: {e}")
            conn.rollback()
            return False

    def delete_transaction(self, transaction_id: int) -> bool:
        """Usuwa transakcję i przywraca stan magazynu."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                
                transaction = cursor.execute("SELECT gold_type_id, transaction_type, quantity FROM transactions WHERE id = ?", (transaction_id,)).fetchone()
                if not transaction:
                    return False
                
                gold_type_id, transaction_type, quantity = transaction
                
                # Revert inventory state
                quantity_change = -quantity if transaction_type == "Kupno" else quantity
                cursor.execute("UPDATE inventory SET quantity = quantity + ? WHERE id = ?", (quantity_change, gold_type_id))
                
                # Delete the transaction
                cursor.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
                
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Błąd usuwania transakcji: {e}")
            return False
