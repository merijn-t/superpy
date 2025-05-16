# Dit is een Python-script dat een command-line interface (CLI) biedt voor het beheren van een supermarktproductensysteem.
import argparse  # Module voor zelf gemaakte CLI's
import csv  # Module voor het lezen en schrijven van CSV-bestanden
from datetime import date, timedelta, datetime  # Voor datumberekeningen (zoals vandaag of een week geleden)
from rich.table import Table  # Voor het weergeven van mooie tabellen in de terminal (een van de twee extra's die je moet gebruiken)
from rich.console import Console  # Mooier maken van de Console output (een van de twee extra's die je moet gebruiken)

# Winc Academy controle-gegevens (niet aanpassen)
__winc_id__ = "a2bc36ea784242e4989deb157d527ba0"
__human_name__ = "superpy"

# -------------------------------
# Functies voor het beheren van de datum
# -------------------------------

def get_current_date():
    """
    Haalt de huidige datum uit het current_date.txt bestand.
    Dit bestand wordt gebruikt om de huidige datum op te slaan.
    Als het bestand leeg of afwezig is, dan wordt hierin de datum van vandaag weggeschreven.
    """
    try:
        with open("current_date.txt", "r") as file:
            content = file.read().strip()
            if not content:
                today = date.today()
                save_current_date(today)
                return today
            return datetime.strptime(content, "%Y-%m-%d").date()
    except FileNotFoundError:
        today = date.today()
        save_current_date(today)
        return today

def save_current_date(new_date):
    """
    Functie om de datum weg te schrijven naar het bestand current_date.txt.
    """
    with open("current_date.txt", "w") as file:
        file.write(new_date.strftime("%Y-%m-%d"))

# -------------------------------
# CLI: Command-line interface instellen
# -------------------------------

def parser_setup():
    """
    Dit is de module de gebruikt is om mijn eigen CLI te maken met eigen commando;s.
    Via deze commandos's kunnen gebruikers kopen, verkopen, voorraad bekijken, en rapporten opvragen.
    """
    parser = argparse.ArgumentParser(
        prog='superpy',
        description='Command line tool voor het bijhouden van supermarktproducten',
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument('--advance-time', help='Verschuif de tijd met aantal dagen', type=int, default=0)
    subparsers = parser.add_subparsers(dest="command", help='Beschikbare opdrachten')

    # Subcommando: kopen
    buy_parser = subparsers.add_parser('buy', help='Koop een product')
    buy_parser.add_argument('--product-name', type=str, required=True, help='Naam van het product')
    buy_parser.add_argument('--price', type=float, required=True, help='Aankoopprijs van het product')
    buy_parser.add_argument('--expiration-date', type=str, required=True, help='Vervaldatum (formaat: YYYY-MM-DD)')

    # Subcommando: verkopen
    sell_parser = subparsers.add_parser('sell', help='Verkoop een product')
    sell_parser.add_argument('--product-name', type=str, required=True, help='Naam van het product')
    sell_parser.add_argument('--price', type=float, required=True, help='Verkoopprijs')
    sell_parser.add_argument('--expiration-date', type=str, required=True, help='Vervaldatum van het product')

    # Subcommando: voorraad tonen
    subparsers.add_parser('inventory', help='Toon huidige voorraad')

    # Subcommando: winst rapportage
    report_parser = subparsers.add_parser('report', help='Toon winstrapportage')
    report_parser.add_argument('--date', type=str, help='Specifieke datum voor rapportage (YYYY-MM-DD)')
    report_parser.add_argument('--today', action='store_true', help='Rapporteer voor vandaag')
    report_parser.add_argument('--week', action='store_true', help='Rapporteer voor de afgelopen 7 dagen')

    # geeft de eventueel gekozen argumenten terug zoda we er later mee kunnen werken.
    return parser.parse_args()

# -------------------------------
# Aankoop opslaan in bought.csv
# -------------------------------

def save_purchased_product_to_csv(product_name, price, expiration_date, current_date):
    """
    Slaat gegevens van een gekocht product op in het bestand bought.csv met de gevraagde velden zoals in de opdracht beschreven:
    ID, naam, aankoopdatum, prijs en vervaldatum.
    """
    try:
        with open('data/bought.csv', mode='r', newline='') as file:
            reader = csv.reader(file)
            rows = [row for row in reader if row and row[0].isdigit()]
            last_id = int(rows[-1][0]) if rows else 0
    except FileNotFoundError:
        last_id = 0

    new_id = last_id + 1
    buy_date = current_date.strftime('%Y-%m-%d')

    with open('data/bought.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        if last_id == 0:
            writer.writerow(['id', 'product_name', 'buy_date', 'buy_price', 'expiration_date'])
        writer.writerow([new_id, product_name, buy_date, price, expiration_date])

    print(f"Aankoop opgeslagen: ID {new_id}, {product_name}, €{price}, vervalt op {expiration_date}")

# -------------------------------
# Verkoop opslaan in sold.csv
# -------------------------------

def save_sold_product_to_csv(bought_id, sell_date, sell_price):
    """
    Slaat gegevens van een verkocht product op in het bestand sold.csv met de gevraagde velden zoals in de opdracht beschreven:
    ID, gekoppelde aankoop-ID en verkoopdatum.
    """
    try:
        with open('data/sold.csv', mode='r', newline='') as file:
            reader = csv.reader(file)
            rows = [row for row in reader if row and row[0].isdigit()]
            last_id = int(rows[-1][0]) if rows else 0
    except FileNotFoundError:
        last_id = 0

    new_id = last_id + 1
    sell_date_str = sell_date.strftime('%Y-%m-%d')

    with open('data/sold.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        if last_id == 0:
            writer.writerow(['id', 'bought_id', 'sell_date', 'sell_price'])
        writer.writerow([new_id, bought_id, sell_date_str, sell_price])

    print(f"Verkoop opgeslagen: verkoop-ID {new_id}, gekoppeld aan aankoop-ID {bought_id}, verkocht voor €{sell_price} op {sell_date_str}")

# -------------------------------
# Hulpfuncties voor het lezen van bestanden
# -------------------------------
    """
    Deze twee onderstaande functies zijn voor het lezen van de CSV-bestanden bought.csv en sold.csv.
    Zodat we deze gegevens weer kunnen gaan aftrekken van elkaar zodat we de winst en o.a voorraad kunnen berekenen.
    """
def read_bought_products():
    """Leest het bestand bought.csv en retourneert een lijst met aangekochte producten."""
    try:
        with open('data/bought.csv', mode='r', newline='') as file:
            return list(csv.DictReader(file))
    except FileNotFoundError:
        return []

def read_sold_products():
    """Leest het bestand sold.csv en retourneert een lijst met verkochte producten."""
    try:
        with open('data/sold.csv', mode='r', newline='') as file:
            return list(csv.DictReader(file))
    except FileNotFoundError:
        return []

# -------------------------------
# Verlopen producten opruimen
# -------------------------------

def clean_expired_products(today):
    """
    Zodra je een buy of sell hebt gedaan, kijkt deze functie meteen of er producten zijn die over de datum zijn.
    Als dat zo is, dan worden deze producten uit de voorraad gehaald.
    """
    try:
        with open('data/bought.csv', mode='r', newline='') as file:
            reader = csv.DictReader(file)
            products = list(reader)
    except FileNotFoundError:
        print("Bestand bought.csv niet gevonden.")
        return

    filtered = []
    verwijderd = []

    for product in products:
        try:
            exp_date = datetime.strptime(product['expiration_date'], "%Y-%m-%d").date()
            if exp_date >= today:
                filtered.append(product)
            else:
                verwijderd.append(product)
        except ValueError:
            print(f"Fout in datumformaat bij product ID {product['id']}")

    with open('data/bought.csv', mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['id', 'product_name', 'buy_date', 'buy_price', 'expiration_date'])
        writer.writeheader()
        writer.writerows(filtered)

    print(f"{len(verwijderd)} verlopen producten verwijderd.")

# -------------------------------
# Voorraad tonen (alles wat niet verkocht is)
# -------------------------------

def get_inventory():
    """Geeft een lijst terug van producten die nog niet verkocht zijn.
    Dit zijn de producten die nog in de voorraad zitten en dus niet ook al in de sold.csv staan.
    (of te wel de producten zijn nog niet verkocht en staan enkel nog in bought.csv)"""
    bought = read_bought_products()
    sold_ids = {item['bought_id'] for item in read_sold_products()}
    return [product for product in bought if product['id'] not in sold_ids]

# -------------------------------
# Koopprijzen ophalen per ID
# -------------------------------

def read_buy_prices(filename='data/bought.csv'):
    """
    Deze functie leest het bought.csv bestand en maakt een dictonary waarin elke sleutel een ID is en de waarde de bijbehorende aankoopprijs.
    """
    prijzen = {}
    try:
        with open(filename, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                prijzen[row['id']] = float(row['buy_price'])
    except FileNotFoundError:
        print(f"{filename} niet gevonden.")
    return prijzen

# -------------------------------
# Winst berekenen tussen 2 datums
# -------------------------------

def calculate_profit(start_date, end_date=None):
    """
    Deze functie berekent de winst van verkochte producten tussen de opgegeven datums.
    Het leest de verkoopprijs uit sold.csv en de aankoopprijs uit bought.csv.
    en laat vervolgens de winst zien in een tabel(met de rich bibliotheek).
    """
    if end_date is None:
        end_date = start_date

    prijzen = read_buy_prices()
    totaal_winst = 0.0
    regels = []

    try:
        with open('data/sold.csv', mode='r', newline='') as file:
            for row in csv.DictReader(file):
                verkoopdatum = datetime.strptime(row['sell_date'], "%Y-%m-%d").date()
                if start_date <= verkoopdatum <= end_date:
                    koopprijs = prijzen.get(row['bought_id'])
                    verkoopprijs = float(row['sell_price'])

                    if koopprijs is None:
                        continue

                    winst = verkoopprijs - koopprijs
                    totaal_winst += winst
                    regels.append({
                        "id": row['id'],
                        "sell_price": verkoopprijs,
                        "buy_price": koopprijs,
                        "profit": winst
                    })
        toon_winst_tabel(regels, totaal_winst)
    except FileNotFoundError:
        print("Verkoopgegevens niet gevonden (sold.csv ontbreekt).")

def toon_winst_tabel(regels, totaal):
    """Toont een nette tabel in de terminal met winsten per product.
        Dit is een van de twee extra's die je moet gebruiken.(rich bibliotheek)
    """
    console = Console()
    table = Table(title="Winstoverzicht")

    table.add_column("Verkoop ID", style="cyan")
    table.add_column("Verkoopprijs", justify="right")
    table.add_column("Aankoopprijs", justify="right")
    table.add_column("Winst", justify="right", style="green")

    for r in regels:
        table.add_row(str(r["id"]),
                      f"€{r['sell_price']:.2f}",
                      f"€{r['buy_price']:.2f}",
                      f"€{r['profit']:.2f}")

    table.add_row("", "", "Totaal:", f"€{totaal:.2f}", end_section=True)
    console.print(table)

# -------------------------------
# De hoofdcode (wordt uitgevoerd als script)
# -------------------------------

def main():
    args = parser_setup()
    current_date = get_current_date()

    # Als de gebruiker de tijd wil vooruitspoelen
    if args.advance_time:
        current_date += timedelta(days=args.advance_time)
        save_current_date(current_date)
        print(f"Datum aangepast naar: {current_date}")
    else:
        save_current_date(current_date)

    # Verlopen producten verwijderen voor we verder gaan
    clean_expired_products(current_date)

    # Afhandeling van elke opdracht
    if args.command == "buy":
        save_purchased_product_to_csv(args.product_name, args.price, args.expiration_date, current_date)

    elif args.command == "sell":
        bought_id = input("Voer het aankoop-ID in van het product dat je wilt verkopen: ")
        save_sold_product_to_csv(int(bought_id), current_date, args.price)

    elif args.command == "inventory":
        voorraad = get_inventory()
        if voorraad:
            console = Console()
            table = Table(title="Huidige Voorraad")
            table.add_column("ID")
            table.add_column("Product")
            table.add_column("Gekocht op")
            table.add_column("Prijs")
            table.add_column("THT")

            for p in voorraad:
                table.add_row(p['id'], p['product_name'], p['buy_date'], f"€{p['buy_price']}", p['expiration_date'])

            console.print(table)
        else:
            print("Geen producten op voorraad.")

    elif args.command == "report":
        if args.today:
            calculate_profit(date.today())
        elif args.date:
            try:
                d = datetime.strptime(args.date, "%Y-%m-%d").date()
                calculate_profit(d)
            except ValueError:
                print("Gebruik het formaat YYYY-MM-DD voor de datum.")
        elif args.week:
            eind = date.today()
            begin = eind - timedelta(days=6)
            calculate_profit(begin, eind)
        else:
            print("Gebruik --today, --date of --week om een rapportage te genereren.")



# -------------------------------
# Hier roepen we de main functie aan om het script uit te voeren.
# -------------------------------
if __name__ == "__main__":
    main()
