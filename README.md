
Скрипт, который при запуске из командной строки без параметров выводит
список жестких дисков с их размерами, присутствующих в системе. При
запуске с одним числовым параметром скрипт должен выводить список
партиций с их размерами, содержащихся на диске с указанным номером.
Требуется реализовать указанный функционал через класс-абстракцию и
конкретные имплементации для ОС Windows + Linux.

---
#### Запуск скрипта

Выводит список жестких дисков с их размерами
```
python idisk.py

Device                               Size               Number
sda                                931.5G                    1
sdb                                 14.9G                    2
```

Выводит список партиций с их размерами, содержащихся на диске с указанным номером
```
python idisk.py 1
Device                              Total
sda1                               931.5G
```

Выводит список жестких дисков или партиций с указанной единицой измерения объёма информации
```
# -u ключ указывает единицу измерения
python idisk.py -u M
Device                               Size               Number
sda                             953869.7M                    1
sdb                              15272.1M                    2

```

```
python idisk.py 1 -u M
Device                              Total
sda1                            953868.7M
```

---
#### Запуск тестов
```
pytest
```
---
#### При разработке использовались
- Python 3.6.0
- Windows 7 x86_64
- Linux 4.10.8-1 ArchLinux x86_64