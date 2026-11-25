

Настільна панель діагностики Windows. Кільцеві індикатори показують поточне навантаження, а графік CPU та RAM допомагає побачити, чи був стрибок короткочасним. Інтерфейс доступний українською, англійською та польською у світлій і темній темах.
Pulse is a Windows desktop dashboard for monitoring system performance. Ring gauges show current usage, while a CPU and RAM chart shows how long a spike lasts. The interface supports English, Polish, and Ukrainian in both light and dark themes.

## Запуск
## Getting started

На цьому комп’ютері відкрийте **Start.cmd** подвійним клацанням. Для іншого комп’ютера з Windows і Python 3.12 виконайте в папці проєкту:
On this computer, double-click **Start.cmd**. On another Windows computer with Python 3.12 installed, open PowerShell in the project folder and run these commands:


## Що можна перевірити
## Features

- **Огляд.** CPU і RAM оновлюються приблизно кожні дві секунди. Два графіки на спільній шкалі показують останні 60 секунд. Для кожного доступного тому видно файлову систему, відсоток використання, вільне місце та місткість. Панель мережі показує локальні IPv4-адреси активних інтерфейсів.
- **Процеси.** Перелік упорядковано за використанням фізичної пам’яті. Введіть частину назви або PID. Прочерк у стовпці часу означає, що Windows не надала час запуску.
- **Журнал живлення.** До 200 останніх записів із системного журналу, з оновленням раз на хвилину. Події 12 і 13 позначають запуск Windows та початок вимкнення. Для 41 і 6008 таблиця показує час реєстрації збою, який може припадати на наступне завантаження. Глибина історії залежить від збережених записів Windows.
- **Звіт.** Кнопка внизу бічної панелі зберігає поточний знімок та доступний журнал у JSON з датою в назві файлу. Звіт містить ім’я ПК, локальні IP-адреси та перелік процесів. Назви полів однакові для всіх мов інтерфейсу.
- **Overview.** CPU and RAM readings update roughly every two seconds. The chart plots both on the same percentage scale over the last 60 seconds. For each available volume, the dashboard shows the file system, percentage used, free space, and total capacity. The network panel lists local IPv4 addresses for active interfaces.
- **Processes.** The list shows running processes in descending order of physical memory usage. Search by part of a process name or by its PID. A dash in the start-time column means Windows did not provide a start time.
- **Power history.** Pulse displays up to 200 recent power events from the Windows System log and refreshes the list once a minute. Event 12 marks Windows startup. Event 13 marks the start of shutdown. For events 41 and 6008, the timestamp shows when Windows recorded the problem, which may be during the next boot. The available history depends on which records Windows has retained.
- **System report.** Select **Save report** at the bottom of the sidebar to export the current snapshot and available power history to a dated JSON file. The report includes the computer name, local IP addresses, and running processes. JSON field names stay the same across interface languages.

## Будова
## Project structure

Поточна версія запускається через `monitor.py`. CustomTkinter відповідає за вікно, Matplotlib малює графіки, а psutil читає лічильники. Модуль `metrics.py` збирає вимірювання та читає журнал Windows через PowerShell. Переклади зібрано у `strings.py`. Файли WPF і PowerShell у корені належать до початкового прототипу.
The entry point is `monitor.py`. CustomTkinter provides the desktop interface, Matplotlib draws the chart, and psutil reads system counters. The `metrics.py` module collects measurements and reads the Windows event log through PowerShell. Interface translations are in `strings.py`. The WPF and PowerShell files in the project root belong to the original prototype.

## План розробки й нагадування · 7–20 листопада 2026
## Development plan and reminders · 7–20 November 2026

Орієнтовний двотижневий план для портфоліо.
Proposed two-week schedule for the portfolio project.

| Дати | Завдання | Нагадування для перевірки |
| Dates | Task | What to check |
| --- | --- | --- |
| 7–8 листопада | Ескіз, структура огляду, палітри | Перевірити читабельність відсотків і підписів у двох темах. |
| 9–10 листопада | CPU, RAM, томи й мережа | Перевірити ПК із кількома інтерфейсами та порожнім кардридером. |
| 11–12 листопада | Ковзне вікно графіка, фонове опитування | Потримати програму відкритою понад хвилину та простежити за лівим краєм графіка. |
| 13–14 листопада | Процеси, PID і час запуску | Відкрити Блокнот, знайти його за назвою, закрити та перевірити оновлення. |
| 15–16 листопада | Історія живлення | Зіставити час, код і джерело запису з журналом System. |
| 17–18 листопада | Переклади та експорт JSON | Перемкнути три мови, скасувати діалог збереження та зберегти звіт повторно. |
| 19–20 листопада | Перевірка запуску й підготовка демонстрації | Запустити через Start.cmd, відкрити всі розділи та звірити звіт із панеллю. |
| 7–8 November | Sketch the dashboard, lay out the overview, and choose the color palettes. | Check that percentages and labels are easy to read in both themes. |
| 9–10 November | Collect CPU, RAM, volume, and network data. | Test on a PC with multiple network interfaces and an empty card reader. |
| 11–12 November | Add the rolling chart and background polling. | Leave the app open for over a minute and check that old samples move off the left edge. |
| 13–14 November | List processes, PIDs, and start times. | Open Notepad, find it by name, then close it and check that its entry disappears. |
| 15–16 November | Add power history. | Compare an entry’s timestamp, event ID, and source with the Windows System log. |
| 17–18 November | Add translations and JSON export. | Switch through all three languages, cancel the save dialog, then reopen it and save a report. |
| 19–20 November | Test startup and prepare the demo. | Launch the app with `Start.cmd`, open each section, and compare the saved report with the dashboard. |
