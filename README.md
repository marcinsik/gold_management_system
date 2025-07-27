# Magazyn Złota - Aplikacja Desktopowa

## Opis
Aplikacja desktopowa do zarządzania magazynem złota, napisana w Pythonie z wykorzystaniem bibliotek Tkinter (GUI) i SQLite3 (baza danych). Program działa offline i pozwala na pełne zarządzanie stanami złota oraz historią transakcji.

## Funkcjonalności

### Główne okno (Magazyn)
- Wyświetla tabelę z aktualnym stanem magazynu złota
- Kolumny: Typ Złota, Waga Jednostkowa (g), Czystość (%), Ilość, Łączna Waga (g)
- Przyciski: Dodaj Nowe Złoto, Kup Złoto, Sprzedaj Złoto, Pokaż Historię Transakcji, Wyjdź

### Zarządzanie typami złota
- Dodawanie nowych typów złota (sztabki, monety, itp.)
- Walidacja unikalności typów
- Kontrola poprawności danych (waga, czystość)

### Transakcje
- **Kupno złota**: Dodawanie złota do magazynu
- **Sprzedaż złota**: Usuwanie złota z magazynu (z kontrolą dostępności)
- Automatyczne aktualizowanie stanów magazynu
- Zapisywanie pełnej historii transakcji

### Historia transakcji
- Pełna historia wszystkich transakcji
- Wyświetlanie: Data, Typ Złota, Typ Transakcji, Ilość, Cena, Wartość, Opis
- Sortowanie chronologiczne (najnowsze na górze)

## Wymagania
- Python 3.7+
- Biblioteki: tkinter, sqlite3 (wbudowane w Python)

## Instalacja i uruchomienie

1. Skopiuj pliki `gold_vault.py` i `database.py` do jednego katalogu
2. Uruchom program:
   ```bash
   python gold_vault.py
   ```

## Struktura bazy danych

### Tabela `inventory`
- `id`: Klucz główny
- `type`: Typ złota (unikalny)
- `unit_weight`: Waga jednostkowa w gramach
- `purity`: Czystość w procentach
- `quantity`: Ilość w magazynie

### Tabela `transactions`
- `id`: Klucz główny
- `gold_type_id`: Odniesienie do typu złota
- `transaction_type`: "Kupno" lub "Sprzedaż"
- `quantity`: Ilość transakcji
- `price_per_unit`: Cena za jednostkę
- `transaction_date`: Data transakcji
- `description`: Opis transakcji

## Plik bazy danych
Baza danych jest automatycznie tworzona w pliku `gold_vault.db` w katalogu programu.

## Obsługa błędów
- Walidacja wszystkich pól wprowadzania
- Kontrola dostępności przy sprzedaży
- Komunikaty o błędach dla użytkownika
- Bezpieczne operacje na bazie danych


