# SuperPy – Technisch Rapport

## Inleiding+
super.py is een Python commandline applicatie die inkoop, verkoop en rapportage van een supermarkt mogelijk maakt.

---

## 1. **Datumbeheer met simulatie-functionaliteit**
Een onderdeel van het project is het ophalen van de huidige datum.
`--advance-time` maakt het mogelijk om door de tijd heen te reizen en handelingen in de toekomst/verleden uit te voeren zonder dat je tot die specefieke datum moet wachten.
Ik gebruik `datetime` en sla de virtuele datum op in een `current_date.txt`.

---

## 2. **Automatisch verwijderen van verlopen producten**
Het opschonen van die over de datum zijn is een van de vereisten van dit project.
Bij iedere actie wordt er gekeken in `bought.csv` door alle producten te verwijderen waarvan de `expiration_date` kleiner is dan de huidige ingevoerde datum.

---

## 3. **Command-line interface met argparse**
Omdat ik mijn eigen commando's/ syntax moest gaan maken hebben we `argparse` bibliotheek gebruikt. Deze maakt het mogelijk om mijn eigen CLI commando's te maken.
o.a. (`buy`, `sell`, `inventory`, `report`) zijn hierin aangemaakt.

---

## Conclusie
Deze drie onderdelen – datumlogica, automatische opschoning, en CLI commando's maken dit een werkend voorraadbeheer systeem van een supermarkt.
