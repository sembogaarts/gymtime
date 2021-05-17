# Reserveer Gymtime

Reserveer eenvoudig via je CLI een sessie bij je favoriete Basic-Fit vestiging. Zit je sessie vol? Geen probleem, we controleren steeds opnieuw of er al een plekje vrij is gekomen.

**Disclaimer:** _Gebruik van de tool is op eigen risico! Het kan zijn dat de tool geen reservering kan maken: dit gebeurt vaak bij drukke Basic-Fit vestigingen._

## Vereisten
* Python 3
* Pip 3

## Cookie
Momenteel is alleen inloggen via je Cookie mogelijk. Om je cookie te bemachtigen doorloop je de volgende stappen:

1. Login op https://my.basic-fit.com/
2. Open je ontwikkel tools, ga naar netwerk en zoek het het `visits` verzoek.
3. Kopieer de gehele cookie uit het `request` **(dus niet het response)**
4. Gebruik deze Cookie om in te loggen via de tool

## Installeren

```
pip install -r requirements.txt
```

## Uitvoeren
Als je alle dependencies hebt geinstalleerd via pip kan je de tool starten met:

```
python main.py 
```

Vul vervolgens je cookie in die je eerder hebt verzameld.
