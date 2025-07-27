import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
from typing import Optional
from database import GoldDatabase

class GoldVaultApp:
    """Główna aplikacja zarządzania magazynem złota."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Magazyn Złota")
        self.root.geometry("1400x800")
        self.root.resizable(True, True)
        
        # Ustawienie minimalnego rozmiaru okna
        self.root.minsize(1200, 700)
        
        # Konfiguracja stylów dla lepszej czytelności
        self.setup_styles()
        
        # Inicjalizacja bazy danych
        try:
            self.db = GoldDatabase()
        except Exception as e:
            messagebox.showerror("Błąd bazy danych", f"Nie można zainicjować bazy danych:\n{str(e)}")
            self.root.destroy()
            return
        
        # Utworzenie GUI
        self.create_widgets()
        self.refresh_inventory()
        
        # Centrowanie okna
        self.center_window()
    
    def setup_styles(self):
        """Konfiguruje style dla lepszej czytelności."""
        style = ttk.Style()
        
        # Większe czcionki dla różnych elementów
        style.configure("Title.TLabel", font=("Arial", 20, "bold"))
        style.configure("Section.TLabelframe.Label", font=("Arial", 12, "bold"))
        style.configure("Section.TLabelframe", padding=15)
        style.configure("Big.TButton", font=("Arial", 11), padding=(10, 8))
        style.configure("Detail.TButton", font=("Arial", 10), padding=(8, 6))
        
        # Ustawienia dla Treeview - znacznie większe wiersze i czcionki
        style.configure("Treeview", font=("Arial", 12), rowheight=55)
        style.configure("Treeview.Heading", font=("Arial", 13, "bold"), padding=(8, 12))
    
    def center_window(self):
        """Centruje główne okno na ekranie."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_widgets(self):
        """Tworzy interfejs użytkownika."""
        # Główny frame z większymi paddingami
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Konfiguracja siatki głównej
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Tytuł z większą czcionką
        title_label = ttk.Label(main_frame, text="MAGAZYN ZŁOTA", 
                               style="Title.TLabel")
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 25))
        
        # Lewa część - Magazyn z większymi paddingami
        left_frame = ttk.LabelFrame(main_frame, text="Stan Magazynu", 
                                   style="Section.TLabelframe")
        left_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Prawa część - Historia transakcji
        right_frame = ttk.LabelFrame(main_frame, text="Historia Transakcji", 
                                    style="Section.TLabelframe")
        right_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0))
        
        # Tabela magazynu w lewej części
        self.create_inventory_table(left_frame)
        
        # Opcje sortowania pod tabelą magazynu
        self.create_sort_options(left_frame)
        
        # Historia transakcji w prawej części
        self.create_transaction_history(right_frame)
        
        # Opcje sortowania historii
        self.create_history_sort_options(right_frame)
        
        # Przyciski na dole z większymi odstępami
        self.create_buttons(main_frame)
    
    def create_inventory_table(self, parent):
        """Tworzy tabelę magazynu."""
        # Konfiguracja siatki dla parent
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        
        # Frame dla tabeli z większymi paddingami
        table_frame = ttk.Frame(parent)
        table_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(5, 0))
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        
        # Treeview z większymi wierszami - dodano kategorię
        self.tree = ttk.Treeview(table_frame, columns=("category", "type", "quantity", "unit_weight", "purity", "total_weight"), 
                                show="headings", height=9)
        
        # Nagłówki kolumn z lepszymi nazwami
        self.tree.heading("category", text="KATEGORIA")
        self.tree.heading("type", text="TYP ZŁOTA")
        self.tree.heading("quantity", text="ILOŚĆ")
        self.tree.heading("unit_weight", text="WAGA JEDN.")
        self.tree.heading("purity", text="CZYSTOŚĆ")
        self.tree.heading("total_weight", text="ŁĄCZNA WAGA")
        
        # Szerokość kolumn i wyrównanie - większe dla większych czcionek
        self.tree.column("category", width=120, anchor="w")
        self.tree.column("type", width=180, anchor="w")
        self.tree.column("quantity", width=90, anchor="center")
        self.tree.column("unit_weight", width=120, anchor="center")
        self.tree.column("purity", width=100, anchor="center")
        self.tree.column("total_weight", width=130, anchor="center")
        
        # Scrollbary
        v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Umieszczenie elementów
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
    
    def create_transaction_history(self, parent):
        """Tworzy tabelę historii transakcji w prawej części."""
        # Konfiguracja siatki dla parent
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        
        # Frame dla tabeli
        history_frame = ttk.Frame(parent)
        history_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(5, 0))
        history_frame.columnconfigure(0, weight=1)
        history_frame.rowconfigure(0, weight=1)
        
        # Treeview dla historii - większe wiersze
        self.history_tree = ttk.Treeview(history_frame, 
                                        columns=("date", "type", "transaction", "quantity", "value"), 
                                        show="headings", height=9)
        
        # Nagłówki kolumn z większymi literami
        self.history_tree.heading("date", text="DATA")
        self.history_tree.heading("type", text="TYP ZŁOTA")
        self.history_tree.heading("transaction", text="TRANSAKCJA")
        self.history_tree.heading("quantity", text="ILOŚĆ")
        self.history_tree.heading("value", text="WARTOŚĆ")
        
        # Szerokość kolumn i wyrównanie - większe dla większych czcionek
        self.history_tree.column("date", width=100, anchor="center")
        self.history_tree.column("type", width=160, anchor="w")
        self.history_tree.column("transaction", width=110, anchor="center")
        self.history_tree.column("quantity", width=80, anchor="center")
        self.history_tree.column("value", width=110, anchor="center")
        
        # Scrollbary
        v_scrollbar_hist = ttk.Scrollbar(history_frame, orient="vertical", command=self.history_tree.yview)
        h_scrollbar_hist = ttk.Scrollbar(history_frame, orient="horizontal", command=self.history_tree.xview)
        self.history_tree.configure(yscrollcommand=v_scrollbar_hist.set, xscrollcommand=h_scrollbar_hist.set)
        
        # Umieszczenie elementów
        self.history_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar_hist.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar_hist.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Obsługa podwójnego kliknięcia na transakcji
        self.history_tree.bind('<Double-1>', self.on_transaction_double_click)
        
        # Przycisk "Więcej szczegółów" z większą czcionką
        detail_button = ttk.Button(parent, text="WIĘCEJ SZCZEGÓŁÓW", 
                                  command=self.show_transactions, style="Detail.TButton")
        detail_button.grid(row=1, column=0, pady=(15, 0))
    
    def create_buttons(self, parent):
        """Tworzy przyciski."""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=2, column=0, columnspan=2, pady=(25, 0))
        
        # Pierwszy rząd przycisków
        buttons_row1 = [
            ("DODAJ NOWE ZŁOTO", self.add_gold_type),
            ("KUP ZŁOTO", self.buy_gold),
            ("SPRZEDAJ ZŁOTO", self.sell_gold)
        ]
        
        # Drugi rząd przycisków
        buttons_row2 = [
            ("PEŁNA HISTORIA", self.show_transactions),
            ("WYJDŹ", self.root.quit)
        ]
        
        # Utworzenie pierwszego rzędu
        for i, (text, command) in enumerate(buttons_row1):
            btn = ttk.Button(button_frame, text=text, command=command, 
                           style="Big.TButton", width=18)
            btn.grid(row=0, column=i, padx=12, pady=8)
        
        # Utworzenie drugiego rzędu
        for i, (text, command) in enumerate(buttons_row2):
            btn = ttk.Button(button_frame, text=text, command=command, 
                           style="Big.TButton", width=18)
            btn.grid(row=1, column=i, padx=12, pady=8)
    
    def create_sort_options(self, parent):
        """Tworzy opcje sortowania magazynu."""
        # Konfiguracja siatki
        parent.rowconfigure(1, weight=0)
        
        # Frame dla opcji sortowania
        sort_frame = ttk.Frame(parent)
        sort_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        sort_frame.columnconfigure(1, weight=1)
        
        # Etykieta
        ttk.Label(sort_frame, text="Sortuj według:", font=("Arial", 11, "bold")).grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        # Combo box z opcjami sortowania
        self.sort_combo = ttk.Combobox(sort_frame, width=20, state="readonly", font=("Arial", 10))
        self.sort_combo['values'] = (
            "Kategoria", 
            "Typ złota", 
            "Czystość", 
            "Ilość", 
            "Łączna waga"
        )
        self.sort_combo.set("Kategoria")  # Domyślne sortowanie
        self.sort_combo.grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
        
        # Przyciski szybkiego sortowania
        sort_buttons = [
            ("📊 Kategoria", lambda: self.sort_inventory("category")),
            ("🔤 Typ", lambda: self.sort_inventory("type")),
            ("⭐ Czystość", lambda: self.sort_inventory("purity")),
            ("🔢 Ilość", lambda: self.sort_inventory("quantity")),
            ("⚖️ Waga", lambda: self.sort_inventory("weight"))
        ]
        
        for i, (text, command) in enumerate(sort_buttons):
            btn = ttk.Button(sort_frame, text=text, command=command, width=12)
            btn.grid(row=0, column=i+2, padx=2)
        
        # Bind dla combo box
        self.sort_combo.bind('<<ComboboxSelected>>', self.on_sort_change)
    
    def on_sort_change(self, event=None):
        """Obsługuje zmianę sortowania z combo box."""
        sort_mapping = {
            "Kategoria": "category",
            "Typ złota": "type",
            "Czystość": "purity",
            "Ilość": "quantity",
            "Łączna waga": "weight"
        }
        
        selected = self.sort_combo.get()
        if selected in sort_mapping:
            self.sort_inventory(sort_mapping[selected])
    
    def sort_inventory(self, sort_by: str):
        """Sortuje i odświeża magazyn według wybranego kryterium."""
        # Aktualizuj combo box
        sort_mapping_reverse = {
            "category": "Kategoria",
            "type": "Typ złota",
            "purity": "Czystość",
            "quantity": "Ilość",
            "weight": "Łączna waga"
        }
        
        if sort_by in sort_mapping_reverse:
            self.sort_combo.set(sort_mapping_reverse[sort_by])
        
        # Wyczyść istniejące dane
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Pobierz i wyświetl dane z nowym sortowaniem
        inventory = self.db.get_inventory(sort_by)
        if not inventory:
            # Dodaj informację o pustym magazynie
            self.tree.insert("", "end", values=(">>> MAGAZYN PUSTY <<<", "", "", "", "", ""))
            return
        
        for item in inventory:
            # Formatuj dane dla lepszej czytelności
            category, type_name, unit_weight, purity, quantity, unit, total_weight, notes = item
            
            formatted_item = (
                category.upper(),  # kategoria - wielkie litery
                type_name.upper(),  # typ złota - wielkie litery
                f"{quantity} {unit}",  # ilość z jednostką
                f"{unit_weight:.2f} g",  # waga jednostkowa z jednostką
                f"{purity:.1f}%",  # czystość z procentem
                f"{total_weight:.2f} g"  # łączna waga z jednostką
            )
            self.tree.insert("", "end", values=formatted_item)
        
        # Odśwież również historię transakcji
        self.refresh_transaction_history()
    
    def refresh_inventory(self):
        """Odświeża tabelę magazynu z aktualnym sortowaniem."""
        # Pobierz aktualne sortowanie lub użyj domyślnego
        current_sort = "category"
        if hasattr(self, 'sort_combo'):
            sort_mapping = {
                "Kategoria": "category",
                "Typ złota": "type",
                "Czystość": "purity",
                "Ilość": "quantity",
                "Łączna waga": "weight"
            }
            selected = self.sort_combo.get()
            if selected in sort_mapping:
                current_sort = sort_mapping[selected]
        
        # Wyczyść istniejące dane
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Pobierz i wyświetl dane
        inventory = self.db.get_inventory(current_sort)
        if not inventory:
            # Dodaj informację o pustym magazynie
            self.tree.insert("", "end", values=(">>> MAGAZYN PUSTY <<<", "", "", "", "", ""))
            return
        
        for item in inventory:
            # Formatuj dane dla lepszej czytelności - dostosowj do nowej struktury
            category, type_name, unit_weight, purity, quantity, unit, total_weight, notes = item
            
            formatted_item = (
                category.upper(),  # kategoria - wielkie litery
                type_name.upper(),  # typ złota - wielkie litery
                f"{quantity} {unit}",  # ilość z jednostką
                f"{unit_weight:.2f} g",  # waga jednostkowa z jednostką
                f"{purity:.1f}%",  # czystość z procentem
                f"{total_weight:.2f} g"  # łączna waga z jednostką
            )
            self.tree.insert("", "end", values=formatted_item)
        
        # Odśwież również historię transakcji
        self.refresh_transaction_history()
        
        # Upewnij się, że sortowanie historii jest ustawione na "Data"
        if hasattr(self, 'history_sort_combo'):
            self.history_sort_combo.set("Data")
    
    def refresh_transaction_history(self):
        """Odświeża tabelę historii transakcji z aktualnym sortowaniem."""
        # Zawsze sortuj domyślnie po dacie (najnowsze na górze), chyba że użytkownik wybrał inaczej
        current_sort = "date"
        if hasattr(self, 'history_sort_combo') and self.history_sort_combo.get():
            sort_mapping = {
                "Data": "date",
                "Typ złota": "type", 
                "Wartość": "value",
                "Rodzaj transakcji": "transaction_type"
            }
            selected = self.history_sort_combo.get()
            if selected in sort_mapping:
                current_sort = sort_mapping[selected]
        
        # Wyczyść istniejące dane
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # Pobierz wszystkie transakcje z sortowaniem wraz z ID
        transactions = self.db.get_transactions_with_id(current_sort)
        recent_transactions = transactions  # Pokaż wszystkie transakcje
        
        if not recent_transactions:
            # Dodaj informację o braku transakcji
            self.history_tree.insert("", "end", values=("", ">>> BRAK TRANSAKCJI <<<", "", "", ""))
            return
        
        for transaction in recent_transactions:
            # Nowa struktura z ID, category, type, purity
            trans_id, date, category, gold_type, purity, trans_type, quantity, price, total_value, description, gold_type_id = transaction
            
            # Skróć nazwę typu złota jeśli jest za długa
            display_type = f"{category} - {gold_type}"
            short_type = display_type[:15] + "..." if len(display_type) > 15 else display_type
            
            # Czytelniejszy typ transakcji
            trans_display = "KUPNO" if trans_type == "Kupno" else "SPRZEDAŻ"
            
            formatted_transaction = (
                date[:10],  # Tylko data bez godziny
                short_type.upper(),  # Wielkie litery
                trans_display,
                f"{quantity:.1f}",  # Ilość jako liczba (bez sztuki bo mogą być różne jednostki)
                f"{total_value:.0f} zł"  # Z jednostką
            )
            
            # Wstaw z ID jako tag dla edycji
            self.history_tree.insert("", "end", values=formatted_transaction, tags=(trans_id,))
    
    def add_gold_type(self):
        """Otwiera dialog dodawania nowego typu złota."""
        dialog = AddGoldTypeDialog(self.root, self.db, self)
        if dialog.result:
            self.refresh_inventory()
    
    def buy_gold(self):
        """Otwiera dialog kupna złota."""
        # Sprawdź czy są dostępne typy złota
        if not self.db.get_gold_types():
            messagebox.showwarning("Uwaga", "Najpierw dodaj typy złota do bazy danych!")
            return
        
        dialog = TransactionDialog(self.root, self.db, "Kupno", self)
        if dialog.result:
            self.refresh_inventory()
    
    def sell_gold(self):
        """Otwiera dialog sprzedaży złota."""
        # Sprawdź czy są dostępne typy złota
        if not self.db.get_gold_types():
            messagebox.showwarning("Uwaga", "Najpierw dodaj typy złota do bazy danych!")
            return
        
        dialog = TransactionDialog(self.root, self.db, "Sprzedaż", self)
        if dialog.result:
            self.refresh_inventory()
    
    def show_transactions(self):
        """Otwiera okno historii transakcji."""
        TransactionHistoryWindow(self.root, self.db)
    
    def create_history_sort_options(self, parent):
        """Tworzy opcje sortowania historii transakcji."""
        # Konfiguracja siatki
        parent.rowconfigure(1, weight=0)
        
        # Frame dla opcji sortowania historii
        history_sort_frame = ttk.Frame(parent)
        history_sort_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        history_sort_frame.columnconfigure(1, weight=1)
        
        # Etykieta
        ttk.Label(history_sort_frame, text="Sortuj według:", font=("Arial", 11, "bold")).grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        # Combo box z opcjami sortowania
        self.history_sort_combo = ttk.Combobox(history_sort_frame, width=15, state="readonly", font=("Arial", 10))
        self.history_sort_combo['values'] = (
            "Data", 
            "Typ złota", 
            "Wartość", 
            "Rodzaj transakcji"
        )
        self.history_sort_combo.set("Data")  # Domyślne sortowanie
        self.history_sort_combo.grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
        
        # Przyciski szybkiego sortowania
        history_sort_buttons = [
            ("📅 Data", lambda: self.sort_transactions("date")),
            ("🔤 Typ", lambda: self.sort_transactions("type")),
            ("💰 Wartość", lambda: self.sort_transactions("value")),
            ("🔄 Rodzaj", lambda: self.sort_transactions("transaction_type"))
        ]
        
        for i, (text, command) in enumerate(history_sort_buttons):
            btn = ttk.Button(history_sort_frame, text=text, command=command, width=10)
            btn.grid(row=0, column=i+2, padx=2)
        
        # Bind dla combo box
        self.history_sort_combo.bind('<<ComboboxSelected>>', self.on_history_sort_change)
    
    def on_history_sort_change(self, event=None):
        """Obsługuje zmianę sortowania historii z combo box."""
        sort_mapping = {
            "Data": "date",
            "Typ złota": "type",
            "Wartość": "value",
            "Rodzaj transakcji": "transaction_type"
        }
        
        selected = self.history_sort_combo.get()
        if selected in sort_mapping:
            self.sort_transactions(sort_mapping[selected])
    
    def sort_transactions(self, sort_by: str):
        """Sortuje i odświeża historię transakcji według wybranego kryterium."""
        # Aktualizuj combo box
        sort_mapping_reverse = {
            "date": "Data",
            "type": "Typ złota",
            "value": "Wartość",
            "transaction_type": "Rodzaj transakcji"
        }
        
        if sort_by in sort_mapping_reverse:
            self.history_sort_combo.set(sort_mapping_reverse[sort_by])
        
        # Wyczyść istniejące dane
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # Pobierz wszystkie transakcje z nowym sortowaniem wraz z ID
        transactions = self.db.get_transactions_with_id(sort_by)
        recent_transactions = transactions  # Pokaż wszystkie transakcje
        
        if not recent_transactions:
            # Dodaj informację o braku transakcji
            self.history_tree.insert("", "end", values=("", ">>> BRAK TRANSAKCJI <<<", "", "", ""))
            return
        
        for transaction in recent_transactions:
            # Nowa struktura z ID, category, type, purity
            trans_id, date, category, gold_type, purity, trans_type, quantity, price, total_value, description, gold_type_id = transaction
            
            # Skróć nazwę typu złota jeśli jest za długa
            display_type = f"{category} - {gold_type}"
            short_type = display_type[:15] + "..." if len(display_type) > 15 else display_type
            
            # Czytelniejszy typ transakcji
            trans_display = "KUPNO" if trans_type == "Kupno" else "SPRZEDAŻ"
            
            formatted_transaction = (
                date[:10],  # Tylko data bez godziny
                short_type.upper(),  # Wielkie litery
                trans_display,
                f"{quantity:.1f}",  # Ilość jako liczba (bez sztuki bo mogą być różne jednostki)
                f"{total_value:.0f} zł"  # Z jednostką
            )
            
            # Wstaw z ID jako tag dla edycji
            self.history_tree.insert("", "end", values=formatted_transaction, tags=(trans_id,))
    
    def on_transaction_double_click(self, event):
        """Obsługuje podwójne kliknięcie na transakcji w historii."""
        selection = self.history_tree.selection()
        if not selection:
            return
        
        # Pobierz ID transakcji z tagów
        item = selection[0]
        tags = self.history_tree.item(item, "tags")
        if tags:
            transaction_id = int(tags[0])
            
            # Otwórz okno edycji pojedynczej transakcji
            dialog = SingleTransactionEditDialog(self.root, self.db, transaction_id, self)
            if dialog.result:
                self.refresh_inventory()
    
    def run(self):
        """Uruchamia aplikację."""
        self.root.mainloop()


class AddGoldTypeDialog:
    """Dialog dodawania nowego typu złota."""
    
    def __init__(self, parent, db: GoldDatabase, main_app=None):
        self.db = db
        self.result = False
        self.main_app = main_app  # Referencja do głównej aplikacji
        
        # Tworzenie okna
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Dodaj Nowy Typ Złota")
        self.dialog.geometry("750x650")
        self.dialog.resizable(True, True)
        self.dialog.grab_set()
        
        # Konfiguracja czcionek dla dialogu
        self.dialog.option_add('*Font', 'Arial 11')
        
        # Centrowanie okna
        self.dialog.transient(parent)
        self.center_window()
        
        self.create_widgets()
    
    def center_window(self):
        """Centruje okno na ekranie."""
        self.dialog.update_idletasks()
        width = 850
        height = 850
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_widgets(self):
        """Tworzy interfejs dialogu."""
        main_frame = ttk.Frame(self.dialog, padding="25")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Konfiguracja siatki
        main_frame.columnconfigure(1, weight=1)
        
        # Kategoria złota
        ttk.Label(main_frame, text="Kategoria:", font=("Arial", 12)).grid(row=0, column=0, sticky=tk.W, pady=20)
        self.category_combo = ttk.Combobox(main_frame, width=45, font=("Arial", 11), state="readonly")
        self.category_combo['values'] = ("Złom", "Moneta", "Sztabka", "Biżuteria", "Inne")
        self.category_combo.set("Złom")  # Domyślna wartość
        self.category_combo.grid(row=0, column=1, pady=20, padx=(15, 0), sticky="ew")
        
        # Pola wprowadzania z większymi czcionkami i odstępami
        ttk.Label(main_frame, text="Typ Złota:", font=("Arial", 12)).grid(row=1, column=0, sticky=tk.W, pady=20)
        self.type_entry = ttk.Entry(main_frame, width=45, font=("Arial", 11))
        self.type_entry.grid(row=1, column=1, pady=20, padx=(15, 0), sticky="ew")
        
        ttk.Label(main_frame, text="Waga Jednostkowa (g):", font=("Arial", 12)).grid(row=2, column=0, sticky=tk.W, pady=20)
        self.weight_entry = ttk.Entry(main_frame, width=45, font=("Arial", 11))
        self.weight_entry.grid(row=2, column=1, pady=20, padx=(15, 0), sticky="ew")
        
        ttk.Label(main_frame, text="Czystość (%):", font=("Arial", 12)).grid(row=3, column=0, sticky=tk.W, pady=20)
        self.purity_entry = ttk.Entry(main_frame, width=45, font=("Arial", 11))
        self.purity_entry.grid(row=3, column=1, pady=20, padx=(15, 0), sticky="ew")
        
        # Jednostka
        ttk.Label(main_frame, text="Jednostka:", font=("Arial", 12)).grid(row=4, column=0, sticky=tk.W, pady=20)
        self.unit_combo = ttk.Combobox(main_frame, width=45, font=("Arial", 11), state="readonly")
        self.unit_combo['values'] = ("szt", "g", "oz")
        self.unit_combo.set("szt")  # Domyślna wartość
        self.unit_combo.grid(row=4, column=1, pady=20, padx=(15, 0), sticky="ew")
        
        # Notatki
        ttk.Label(main_frame, text="Notatki:", font=("Arial", 12)).grid(row=5, column=0, sticky=tk.W, pady=20)
        self.notes_entry = ttk.Entry(main_frame, width=45, font=("Arial", 11))
        self.notes_entry.grid(row=5, column=1, pady=20, padx=(15, 0), sticky="ew")
        
        # Przyciski z większymi czcionkami
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=25)
        
        ttk.Button(button_frame, text="DODAJ", command=self.add_gold, 
                  width=15, style="Big.TButton").pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="ANULUJ", command=self.dialog.destroy, 
                  width=15, style="Big.TButton").pack(side=tk.LEFT, padx=10)
        
        # Focus na pierwszym polu
        self.category_combo.focus()
        
        # Obsługa klawisza Enter
        self.dialog.bind('<Return>', lambda event: self.add_gold())
        self.dialog.bind('<Escape>', lambda event: self.dialog.destroy())
    
    def add_gold(self):
        """Dodaje nowy typ złota."""
        try:
            # Walidacja danych
            category = self.category_combo.get().strip()
            if not category:
                messagebox.showerror("Błąd", "Wybierz kategorię!")
                return
            
            gold_type = self.type_entry.get().strip()
            if not gold_type:
                messagebox.showerror("Błąd", "Typ złota nie może być pusty!")
                return
            
            unit_weight = float(self.weight_entry.get())
            if unit_weight <= 0:
                messagebox.showerror("Błąd", "Waga jednostkowa musi być dodatnia!")
                return
            
            purity = float(self.purity_entry.get())
            if not (0 < purity <= 100):
                messagebox.showerror("Błąd", "Czystość musi być między 0 a 100%!")
                return
            
            unit = self.unit_combo.get().strip()
            if not unit:
                messagebox.showerror("Błąd", "Wybierz jednostkę!")
                return
            
            notes = self.notes_entry.get().strip()
            
            # Dodawanie do bazy
            if self.db.add_gold_type(category, gold_type, unit_weight, purity, unit, notes):
                messagebox.showinfo("Sukces", f"Typ złota '{gold_type}' został dodany!")
                self.result = True
                
                # Odśwież główne okno natychmiast po dodaniu typu złota
                if self.main_app:
                    self.main_app.refresh_inventory()
                
                self.dialog.destroy()
            else:
                messagebox.showerror("Błąd", "Typ złota o tej kombinacji (kategoria, typ, czystość) już istnieje!")
        
        except ValueError:
            messagebox.showerror("Błąd", "Waga i czystość muszą być liczbami!")


class TransactionDialog:
    """Dialog transakcji (kupno/sprzedaż)."""
    
    def __init__(self, parent, db: GoldDatabase, transaction_type: str, main_app=None):
        self.db = db
        self.transaction_type = transaction_type
        self.result = False
        self.main_app = main_app  # Referencja do głównej aplikacji
        
        # Tworzenie okna
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"{transaction_type} Złota")
        self.dialog.geometry("750x550")
        self.dialog.resizable(True, True)
        self.dialog.grab_set()
        
        # Konfiguracja czcionek dla dialogu
        self.dialog.option_add('*Font', 'Arial 11')
        
        # Centrowanie okna
        self.dialog.transient(parent)
        self.center_window()
        
        self.create_widgets()
    
    def center_window(self):
        """Centruje okno na ekranie."""
        self.dialog.update_idletasks()
        width = 850
        height = 850
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_widgets(self):
        """Tworzy interfejs dialogu."""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Konfiguracja siatki
        main_frame.columnconfigure(1, weight=1)
        
        # Typ złota
        ttk.Label(main_frame, text="Typ Złota:").grid(row=0, column=0, sticky=tk.W, pady=15)
        self.gold_combo = ttk.Combobox(main_frame, width=55, state="readonly")
        self.gold_combo.grid(row=0, column=1, pady=15, padx=(10, 0), sticky="ew")
        
        # Pobierz typy złota
        gold_types = self.db.get_gold_types()
        type_names = []
        self.gold_data = {}
        
        for gold_id, category, gold_type, purity, unit in gold_types:
            display_name = f"{category} - {gold_type} ({purity:.1f}%)"
            type_names.append(display_name)
            self.gold_data[display_name] = gold_id
        
        self.gold_combo['values'] = type_names
        
        # Ilość
        ttk.Label(main_frame, text="Ilość:").grid(row=1, column=0, sticky=tk.W, pady=15)
        self.quantity_entry = ttk.Entry(main_frame, width=55)
        self.quantity_entry.grid(row=1, column=1, pady=15, padx=(10, 0), sticky="ew")
        
        # Cena za jednostkę
        ttk.Label(main_frame, text="Cena za Jednostkę (zł):").grid(row=2, column=0, sticky=tk.W, pady=15)
        self.price_entry = ttk.Entry(main_frame, width=55)
        self.price_entry.grid(row=2, column=1, pady=15, padx=(10, 0), sticky="ew")
        
        # Data transakcji
        ttk.Label(main_frame, text="Data Transakcji:").grid(row=3, column=0, sticky=tk.W, pady=15)
        self.date_entry = ttk.Entry(main_frame, width=55)
        self.date_entry.grid(row=3, column=1, pady=15, padx=(10, 0), sticky="ew")
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # Opis
        ttk.Label(main_frame, text="Opis:").grid(row=4, column=0, sticky=tk.W, pady=15)
        self.description_entry = ttk.Entry(main_frame, width=55)
        self.description_entry.grid(row=4, column=1, pady=15, padx=(10, 0), sticky="ew")
        
        # Informacja o dostępności (tylko dla sprzedaży)
        if self.transaction_type == "Sprzedaż":
            self.info_label = ttk.Label(main_frame, text="", foreground="blue", font=("Arial", 11, "bold"))
            self.info_label.grid(row=5, column=0, columnspan=2, pady=10)
            self.gold_combo.bind('<<ComboboxSelected>>', self.update_availability_info)
            
            # Dodaj również aktualizację przy zmianie ilości
            self.quantity_entry.bind('<KeyRelease>', self.update_availability_info)
        
        # Przyciski z większymi czcionkami
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=25)
        
        ttk.Button(button_frame, text=self.transaction_type.upper(), command=self.process_transaction, 
                  width=15, style="Big.TButton").pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="ANULUJ", command=self.dialog.destroy, 
                  width=15, style="Big.TButton").pack(side=tk.LEFT, padx=10)
        
        # Focus na pierwszym polu
        self.gold_combo.focus()
        
        # Obsługa klawiszy
        self.dialog.bind('<Return>', lambda event: self.process_transaction())
        self.dialog.bind('<Escape>', lambda event: self.dialog.destroy())
    
    def update_availability_info(self, event=None):
        """Aktualizuje informację o dostępności złota."""
        if self.transaction_type == "Sprzedaż":
            gold_type = self.gold_combo.get()
            if gold_type and gold_type in self.gold_data:
                gold_id = self.gold_data[gold_type]
                available = self.db.get_gold_quantity(gold_id)
                
                # Sprawdź ile użytkownik chce sprzedać
                try:
                    quantity_str = self.quantity_entry.get().strip()
                    if quantity_str:
                        requested = float(quantity_str)
                        if requested > available:
                            self.info_label.config(text=f"⚠️ Dostępne: {available:.1f} - NIEWYSTARCZAJĄCE!", 
                                                  foreground="red")
                        else:
                            remaining = available - requested
                            self.info_label.config(text=f"✓ Dostępne: {available:.1f} - Po sprzedaży zostanie: {remaining:.1f}", 
                                                  foreground="green")
                    else:
                        self.info_label.config(text=f"Dostępne w magazynie: {available:.1f}", 
                                              foreground="blue")
                except ValueError:
                    self.info_label.config(text=f"Dostępne w magazynie: {available:.1f}", 
                                          foreground="blue")
    
    def process_transaction(self):
        """Przetwarza transakcję."""
        try:
            # Walidacja danych
            gold_type = self.gold_combo.get()
            if not gold_type:
                messagebox.showerror("Błąd", "Wybierz typ złota!")
                return
            
            quantity_str = self.quantity_entry.get().strip()
            if not quantity_str:
                messagebox.showerror("Błąd", "Wprowadź ilość!")
                return
            
            quantity = float(quantity_str)  # Zmiana na float dla elastyczności
            if quantity <= 0:
                messagebox.showerror("Błąd", "Ilość musi być dodatnia!")
                return
            
            price_str = self.price_entry.get().strip()
            if not price_str:
                messagebox.showerror("Błąd", "Wprowadź cenę!")
                return
            
            price = float(price_str)
            if price <= 0:
                messagebox.showerror("Błąd", "Cena musi być dodatnia!")
                return
            
            date = self.date_entry.get().strip()
            if not date:
                messagebox.showerror("Błąd", "Wprowadź datę!")
                return
            
            description = self.description_entry.get().strip()
            gold_id = self.gold_data[gold_type]
            
            # Walidacja formatu daty
            try:
                datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Błąd", "Data musi być w formacie YYYY-MM-DD!")
                return
            
            description = self.description_entry.get().strip()
            gold_id = self.gold_data[gold_type]
            
            # Dodatkowa walidacja dla sprzedaży
            if self.transaction_type == "Sprzedaż":
                available = self.db.get_gold_quantity(gold_id)
                if available < quantity:
                    messagebox.showerror("Błąd", f"Niewystarczająca ilość w magazynie!\nDostępne: {available}, Wymagane: {quantity}")
                    return
            
            # Dodawanie transakcji
            if self.db.add_transaction(gold_id, self.transaction_type, quantity, price, date, description):
                total_value = quantity * price
                messagebox.showinfo("Sukces", 
                    f"Transakcja {self.transaction_type.lower()} została zapisana!\n"
                    f"Ilość: {quantity} szt.\n"
                    f"Cena jednostkowa: {price:.2f} zł\n"
                    f"Wartość całkowita: {total_value:.2f} zł")
                self.result = True
                
                # Odśwież główne okno natychmiast po transakcji
                if self.main_app:
                    self.main_app.refresh_inventory()
                
                self.dialog.destroy()
            else:
                messagebox.showerror("Błąd", "Błąd podczas zapisywania transakcji!")
        
        except ValueError as e:
            if "invalid literal for int()" in str(e):
                messagebox.showerror("Błąd", "Ilość musi być liczbą całkowitą!")
            else:
                messagebox.showerror("Błąd", "Cena musi być liczbą!")
        except Exception as e:
            messagebox.showerror("Błąd", f"Wystąpił błąd: {str(e)}")


class SingleTransactionEditDialog:
    """Dialog edycji pojedynczej transakcji."""
    
    def __init__(self, parent, db: GoldDatabase, transaction_id: int, main_app=None):
        self.db = db
        self.transaction_id = transaction_id
        self.result = False
        self.main_app = main_app
        
        # Tworzenie okna
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Edytuj Transakcję")
        self.dialog.geometry("750x600")
        self.dialog.resizable(True, True)
        
        # Konfiguracja czcionek dla dialogu
        self.dialog.option_add('*Font', 'Arial 11')
        
        # Centrowanie okna
        self.dialog.transient(parent)
        self.center_window()
        
        # Wczytaj dane transakcji
        self.transaction_data = self.db.get_transaction_by_id(transaction_id)
        if not self.transaction_data:
            messagebox.showerror("Błąd", "Nie można wczytać danych transakcji!")
            self.dialog.destroy()
            return
        
        self.create_widgets()
        self.load_transaction_data()
        
        # Grab set dopiero po pełnym utworzeniu okna
        self.dialog.grab_set()
    
    def center_window(self):
        """Centruje okno na ekranie."""
        self.dialog.update_idletasks()
        width = 950
        height = 800
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_widgets(self):
        """Tworzy interfejs dialogu."""
        main_frame = ttk.Frame(self.dialog, padding="25")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Konfiguracja siatki
        main_frame.columnconfigure(1, weight=1)
        
        # Informacja o transakcji
        _, _, category, gold_type, purity, trans_type, quantity, price, date, description = self.transaction_data
        info_text = f"Edytuj transakcję: {trans_type} - {category} {gold_type} ({purity:.1f}%)"
        ttk.Label(main_frame, text=info_text, font=("Arial", 12, "bold"), 
                 foreground="blue").grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Typ złota (tylko do wyświetlenia)
        ttk.Label(main_frame, text="Typ Złota:", font=("Arial", 12)).grid(row=1, column=0, sticky=tk.W, pady=15)
        self.gold_combo = ttk.Combobox(main_frame, width=45, state="readonly", font=("Arial", 11))
        self.gold_combo.grid(row=1, column=1, pady=15, padx=(15, 0), sticky="ew")
        
        # Pobierz typy złota
        gold_types = self.db.get_gold_types()
        type_names = []
        self.gold_data = {}
        
        for gold_id, cat, gt, pur, unit in gold_types:
            display_name = f"{cat} - {gt} ({pur:.1f}%)"
            type_names.append(display_name)
            self.gold_data[display_name] = gold_id
        
        self.gold_combo['values'] = type_names
        
        # Typ transakcji (tylko do wyświetlenia)
        ttk.Label(main_frame, text="Typ Transakcji:", font=("Arial", 12)).grid(row=2, column=0, sticky=tk.W, pady=15)
        self.trans_type_combo = ttk.Combobox(main_frame, width=45, state="readonly", font=("Arial", 11))
        self.trans_type_combo['values'] = ("Kupno", "Sprzedaż")
        self.trans_type_combo.grid(row=2, column=1, pady=15, padx=(15, 0), sticky="ew")
        
        # Ilość
        ttk.Label(main_frame, text="Ilość:", font=("Arial", 12)).grid(row=3, column=0, sticky=tk.W, pady=15)
        self.quantity_entry = ttk.Entry(main_frame, width=45, font=("Arial", 11))
        self.quantity_entry.grid(row=3, column=1, pady=15, padx=(15, 0), sticky="ew")
        
        # Cena za jednostkę
        ttk.Label(main_frame, text="Cena za Jednostkę (zł):", font=("Arial", 12)).grid(row=4, column=0, sticky=tk.W, pady=15)
        self.price_entry = ttk.Entry(main_frame, width=45, font=("Arial", 11))
        self.price_entry.grid(row=4, column=1, pady=15, padx=(15, 0), sticky="ew")
        
        # Data transakcji
        ttk.Label(main_frame, text="Data Transakcji:", font=("Arial", 12)).grid(row=5, column=0, sticky=tk.W, pady=15)
        self.date_entry = ttk.Entry(main_frame, width=45, font=("Arial", 11))
        self.date_entry.grid(row=5, column=1, pady=15, padx=(15, 0), sticky="ew")
        
        # Opis
        ttk.Label(main_frame, text="Opis:", font=("Arial", 12)).grid(row=6, column=0, sticky=tk.W, pady=15)
        self.description_entry = ttk.Entry(main_frame, width=45, font=("Arial", 11))
        self.description_entry.grid(row=6, column=1, pady=15, padx=(15, 0), sticky="ew")
        
        # Informacja o dostępności (dla sprzedaży)
        self.info_label = ttk.Label(main_frame, text="", font=("Arial", 11, "bold"))
        self.info_label.grid(row=7, column=0, columnspan=2, pady=15)
        
        # Przyciski
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=8, column=0, columnspan=2, pady=25)
        
        ttk.Button(button_frame, text="ZAPISZ ZMIANY", command=self.save_changes, 
                  width=15, style="Big.TButton").pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="USUŃ", command=self.delete_transaction, 
                  width=15, style="Big.TButton").pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="ANULUJ", command=self.dialog.destroy, 
                  width=15, style="Big.TButton").pack(side=tk.LEFT, padx=10)
        
        # Obsługa klawiszy
        self.dialog.bind('<Return>', lambda event: self.save_changes())
        self.dialog.bind('<Escape>', lambda event: self.dialog.destroy())
        
        # Bind dla sprawdzania dostępności
        self.trans_type_combo.bind('<<ComboboxSelected>>', self.update_availability_info)
        self.quantity_entry.bind('<KeyRelease>', self.update_availability_info)
        self.gold_combo.bind('<<ComboboxSelected>>', self.update_availability_info)
    
    def load_transaction_data(self):
        """Wczytuje dane transakcji do formularza."""
        _, gold_type_id, category, gold_type, purity, trans_type, quantity, price, date, description = self.transaction_data
        
        # Ustaw typ złota
        display_name = f"{category} - {gold_type} ({purity:.1f}%)"
        self.gold_combo.set(display_name)
        
        # Ustaw typ transakcji
        self.trans_type_combo.set(trans_type)
        
        # Ustaw pozostałe pola
        self.quantity_entry.insert(0, str(quantity))
        self.price_entry.insert(0, str(price))
        self.date_entry.insert(0, date)
        self.description_entry.insert(0, description or "")
        
        # Aktualizuj informację o dostępności
        self.update_availability_info()
    
    def update_availability_info(self, event=None):
        """Aktualizuje informację o dostępności złota."""
        trans_type = self.trans_type_combo.get()
        gold_type = self.gold_combo.get()
        
        if trans_type == "Sprzedaż" and gold_type and gold_type in self.gold_data:
            gold_id = self.gold_data[gold_type]
            available = self.db.get_gold_quantity(gold_id)
            
            # Sprawdź ile użytkownik chce sprzedać
            try:
                quantity_str = self.quantity_entry.get().strip()
                if quantity_str:
                    requested = float(quantity_str)
                    if requested > available:
                        self.info_label.config(text=f"⚠️ Dostępne: {available:.1f} - NIEWYSTARCZAJĄCE!", 
                                              foreground="red")
                    else:
                        remaining = available - requested
                        self.info_label.config(text=f"✓ Dostępne: {available:.1f} - Po sprzedaży zostanie: {remaining:.1f}", 
                                              foreground="green")
                else:
                    self.info_label.config(text=f"Dostępne w magazynie: {available:.1f}", 
                                          foreground="blue")
            except ValueError:
                self.info_label.config(text=f"Dostępne w magazynie: {available:.1f}", 
                                      foreground="blue")
        else:
            self.info_label.config(text="", foreground="black")
    
    def save_changes(self):
        """Zapisuje zmiany w transakcji."""
        try:
            # Walidacja danych
            gold_type = self.gold_combo.get()
            if not gold_type:
                messagebox.showerror("Błąd", "Wybierz typ złota!")
                return
            
            trans_type = self.trans_type_combo.get()
            if not trans_type:
                messagebox.showerror("Błąd", "Wybierz typ transakcji!")
                return
            
            quantity = float(self.quantity_entry.get())
            if quantity <= 0:
                messagebox.showerror("Błąd", "Ilość musi być dodatnia!")
                return
            
            price = float(self.price_entry.get())
            if price <= 0:
                messagebox.showerror("Błąd", "Cena musi być dodatnia!")
                return
            
            date = self.date_entry.get().strip()
            if not date:
                messagebox.showerror("Błąd", "Wprowadź datę!")
                return
            
            description = self.description_entry.get().strip()
            gold_id = self.gold_data[gold_type]
            
            # Aktualizuj transakcję
            if self.db.update_transaction(self.transaction_id, gold_id, trans_type, quantity, price, date, description):
                messagebox.showinfo("Sukces", "Transakcja została zaktualizowana!")
                self.result = True
                
                # Odśwież główne okno
                if self.main_app:
                    self.main_app.refresh_inventory()
                
                self.dialog.destroy()
            else:
                messagebox.showerror("Błąd", "Nie można zaktualizować transakcji!\nSprawdź czy masz wystarczającą ilość w magazynie.")
        
        except ValueError:
            messagebox.showerror("Błąd", "Ilość i cena muszą być liczbami!")
        except Exception as e:
            messagebox.showerror("Błąd", f"Wystąpił błąd: {str(e)}")
    
    def delete_transaction(self):
        """Usuwa transakcję."""
        if messagebox.askyesno("Potwierdzenie", 
                              "Czy na pewno chcesz usunąć tę transakcję?\nTa operacja jest nieodwracalna!"):
            if self.db.delete_transaction(self.transaction_id):
                messagebox.showinfo("Sukces", "Transakcja została usunięta!")
                self.result = True
                
                # Odśwież główne okno
                if self.main_app:
                    self.main_app.refresh_inventory()
                
                self.dialog.destroy()
            else:
                messagebox.showerror("Błąd", "Nie można usunąć transakcji!")


class TransactionHistoryWindow:
    """Okno historii transakcji."""
    
    def __init__(self, parent, db: GoldDatabase):
        self.db = db
        
        # Tworzenie okna
        self.window = tk.Toplevel(parent)
        self.window.title("Historia Transakcji")
        self.window.geometry("1100x650")
        self.window.resizable(True, True)
        
        # Konfiguracja stylów dla tego okna
        style = ttk.Style()
        style.configure("History.Treeview", font=("Arial", 11), rowheight=50)
        style.configure("History.Treeview.Heading", font=("Arial", 12, "bold"), padding=(8, 10))
        
        # Centrowanie okna
        self.window.transient(parent)
        self.center_window()
        
        self.create_widgets()
        self.load_transactions()
    
    def center_window(self):
        """Centruje okno na ekranie."""
        self.window.update_idletasks()
        width = 1600
        height = 850
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_widgets(self):
        """Tworzy interfejs okna."""
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Tytuł
        ttk.Label(main_frame, text="Historia Transakcji", 
                 font=("Arial", 14, "bold")).pack(pady=(0, 10))
        
        # Frame dla tabeli
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Treeview z scrollbarami - większe czcionki
        self.tree = ttk.Treeview(table_frame, 
                                columns=("date", "gold_type", "transaction_type", "quantity", "price", "total_value", "description"), 
                                show="headings", height=15, style="History.Treeview")
        
        # Nagłówki kolumn z większymi czcionkami
        self.tree.heading("date", text="DATA")
        self.tree.heading("gold_type", text="TYP ZŁOTA")
        self.tree.heading("transaction_type", text="TYP TRANSAKCJI")
        self.tree.heading("quantity", text="ILOŚĆ")
        self.tree.heading("price", text="CENA JEDNOSTKOWA")
        self.tree.heading("total_value", text="CAŁKOWITA WARTOŚĆ")
        self.tree.heading("description", text="OPIS")
        
        # Szerokość kolumn i wyrównanie - większe dla większych czcionek
        self.tree.column("date", width=110, anchor="center")
        self.tree.column("gold_type", width=160, anchor="w")
        self.tree.column("transaction_type", width=120, anchor="center")
        self.tree.column("quantity", width=90, anchor="center")
        self.tree.column("price", width=130, anchor="center")
        self.tree.column("total_value", width=140, anchor="center")
        self.tree.column("description", width=220, anchor="w")
        
        # Scrollbary
        v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Umieszczenie elementów
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Konfiguracja siatki
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        
        # Przycisk zamknij
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="Zamknij", command=self.window.destroy, width=12).pack()
        
        # Obsługa klawisza Escape
        self.window.bind('<Escape>', lambda event: self.window.destroy())
    
    def load_transactions(self):
        """Ładuje transakcje do tabeli."""
        transactions = self.db.get_transactions()
        
        # Dodaj informację o ilości transakcji
        if not transactions:
            # Dodaj pustą linię z informacją
            self.tree.insert("", "end", values=("", "Brak transakcji", "", "", ""))
            return
        
        for transaction in transactions:
            # Formatowanie wartości dla lepszej czytelności
            date, gold_type, trans_type, quantity, price, total_value, description = transaction
            formatted_transaction = (
                date,
                gold_type,
                trans_type,
                str(quantity),
                f"{price:.2f} zł",
                f"{total_value:.2f} zł",
                description or ""
            )
            self.tree.insert("", "end", values=formatted_transaction)


def main():
    """Główna funkcja programu."""
    try:
        app = GoldVaultApp()
        app.run()
    except Exception as e:
        messagebox.showerror("Błąd krytyczny", f"Wystąpił nieoczekiwany błąd:\n{str(e)}")
        print(f"Błąd: {e}")


if __name__ == "__main__":
    main()
