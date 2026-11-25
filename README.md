# Pulse · Diagnostyka komputera

Pulse to aplikacja do monitorowania komputera z systemem Windows. Pokazuje obciążenie procesora, wykorzystanie pamięci RAM, zajętość dysków i lokalne adresy IP. Pozwala sprawdzić, które procesy działają, kiedy zostały uruchomione oraz kiedy system Windows rozpoczął pracę lub zamykanie. Interfejs jest w języku polskim i obsługuje jasny oraz ciemny motyw.

## Uruchomienie

Na komputerze, na którym projekt jest już skonfigurowany, kliknij dwukrotnie **Start.cmd** w folderze projektu.

Aby uruchomić Pulse na innym komputerze z systemem Windows i zainstalowanym Pythonem 3.12, otwórz PowerShell w folderze projektu i wykonaj polecenia:

```powershell
py -3.12 -m pip install -r requirements.txt
py -3.12 monitor.py
```

## Funkcje

### Przegląd

- **Procesor.** Wskaźnik pokazuje bieżące obciążenie CPU w procentach. Pod nim znajduje się liczba rdzeni logicznych.
- **Pamięć RAM.** Panel pokazuje procent wykorzystanej pamięci oraz ilość zajętej i całkowitej pamięci w GiB.
- **Wykres aktywności.** Dwie linie przedstawiają obciążenie CPU i wykorzystanie RAM na wspólnej skali od 0 do 100%. Nowe próbki pojawiają się mniej więcej co dwie sekundy. Wykres obejmuje ostatnie 60 sekund pracy aplikacji.
- **Dyski.** Wskaźnik pierścieniowy pokazuje łączny procent zajętego miejsca. Poniżej można sprawdzić system plików, pojemność, wolne miejsce i procent zajętości każdego dostępnego woluminu.
- **Sieć.** Lista zawiera nazwy aktywnych interfejsów sieciowych i przypisane do nich lokalne adresy IPv4.

### Procesy

Lista procesów jest uporządkowana malejąco według wykorzystania pamięci fizycznej. Aby znaleźć program, wpisz fragment jego nazwy lub pełny identyfikator PID. Przy każdym procesie widać jego nazwę, PID, zajętą pamięć w MiB i czas uruchomienia. Kreska w kolumnie czasu oznacza, że Windows nie udostępnił tej informacji.

### Historia zasilania

Pulse odczytuje do 200 ostatnich pasujących zdarzeń z dziennika **System** i odświeża listę raz na minutę. Tabela zawiera czas wpisu, opis zdarzenia, jego identyfikator oraz źródło.

| Identyfikator | Źródło | Znaczenie |
| --- | --- | --- |
| 12 | Microsoft-Windows-Kernel-General | Uruchomienie systemu Windows. |
| 13 | Microsoft-Windows-Kernel-General | Rozpoczęcie zamykania systemu. |
| 41 | Microsoft-Windows-Kernel-Power | Ponowne uruchomienie po nieprawidłowym zamknięciu. |
| 6008 | EventLog | System wykrył, że poprzednie zamknięcie było nieoczekiwane. |

Przy zdarzeniach **41** i **6008** tabela pokazuje czas zarejestrowania wpisu. Windows może zapisać go dopiero przy następnym uruchomieniu, dlatego dokładna chwila awarii może być wcześniejsza. Zakres dostępnej historii zależy od wpisów zachowanych w dzienniku systemowym.

### Raport systemowy

Wybierz **Zapisz raport** u dołu panelu bocznego i wskaż miejsce zapisu. Aplikacja proponuje nazwę pliku zawierającą datę i godzinę, na przykład `Pulse-20261120-143000.json`.

Raport zawiera czas pomiaru, nazwę komputera, informacje o systemie, czas ostatniego uruchomienia, odczyty CPU i RAM, dane o dyskach, lokalne adresy IPv4, listę procesów i dostępną historię zasilania.

## Budowa projektu

| Plik | Przeznaczenie |
| --- | --- |
| `Start.cmd` | Uruchamia aplikację z folderu projektu. |
| `monitor.py` | Tworzy okno, obsługuje nawigację, aktualizuje wykres i tabele oraz zapisuje raport JSON. |
| `metrics.py` | Zbiera dane o zasobach komputera i procesach. Odczytuje dziennik zdarzeń Windows przez PowerShell. |
| `strings.py` | Zawiera polskie napisy interfejsu. |
| `requirements.txt` | Zawiera listę bibliotek Pythona potrzebnych do uruchomienia aplikacji. |

Interfejs korzysta z **CustomTkinter**, wykres z **Matplotlib**, a pomiary systemowe z **psutil**. Moduły `platform` i `socket` dostarczają informacji o systemie i komputerze. Pliki WPF i skrypty PowerShell w głównym folderze projektu pochodzą z wcześniejszego prototypu.

Pomiary zasobów i odczyt dziennika działają w osobnych wątkach, dzięki czemu można korzystać z menu podczas pobierania danych. Przy powrocie do wcześniej otwartej sekcji aplikacja ponownie wykorzystuje istniejący widok.

## Plan prac i przypomnienia · 7–20 listopada 2026

Orientacyjny dwutygodniowy plan projektu do portfolio.

| Termin | Zadanie | Co sprawdzić |
| --- | --- | --- |
| 7–8 listopada | Przygotować szkic panelu, układ nawigacji i palety kolorów. | Sprawdzić czytelność etykiet, wskaźników i aktywnej pozycji menu w obu motywach. |
| 9–10 listopada | Dodać odczyty CPU, RAM, dysków i sieci. | Sprawdzić listę woluminów oraz adresy IP na komputerze z kilkoma interfejsami sieciowymi. |
| 11–12 listopada | Dodać wykres i pobieranie pomiarów w tle. | Pozostawić aplikację otwartą ponad minutę i sprawdzić, czy najstarsze próbki przesuwają się poza lewą krawędź wykresu. |
| 13–14 listopada | Przygotować listę procesów wraz z wyszukiwaniem. | Uruchomić Notatnik, znaleźć go po nazwie i PID, a następnie zamknąć i sprawdzić, czy wpis znika z listy. |
| 15–16 listopada | Dodać historię uruchomień i zamknięć systemu. | Porównać czas, identyfikator i źródło wybranego zdarzenia z dziennikiem System w Podglądzie zdarzeń Windows. |
| 17–18 listopada | Dopracować polskie komunikaty i eksport raportu. | Anulować zapis, ponownie otworzyć okno zapisu, zapisać plik JSON i sprawdzić jego zawartość. |
| 19–20 listopada | Sprawdzić nawigację i przygotować demonstrację. | Uruchomić aplikację przez `Start.cmd`, otworzyć wszystkie sekcje, zmienić motyw i porównać raport z danymi widocznymi na ekranie. |