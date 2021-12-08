#!/usr/bin/python3
#Cykelns program

#Klass för en cykel
class Bike:
    def __init__(self, id, city_id, charge_id, parking_id, bike_status, battery_status, maintenance, coordinates):
        self.id = id
        self.city_id = city_id
        self.charge_id = charge_id
        self.parking_id = parking_id
        self.bike_status = bike_status
        self.battery_status = battery_status
        self.maintenance = maintenance
        self.coordinates = coordinates


    # Instans metoder
    def position():
        """Position på cykeln"""
        #Cykeln meddelar dess position med jämna mellanrum.
        pass

    def bikestatus():
        """Status för cykeln"""
        #Cykeln meddelar om den kör eller står stilla och vilken hastighet den rör sig i.
        pass

    def on_off():
        """Läge av/på"""
        #Man skall kunna stänga av/stoppa en cykel så att den inte kan köras längre.
        pass

    def activate():
        """Aktivera cykeln"""
        #När en kund hyr cykeln är det möjligt att starta den och köra.
        pass

    def drop_of_bike():
        """Lämna tillbaka cykeln efter användning"""
        #Kunden kan lämna tillbaka en cykel och släppa kontrollen över den.
        pass

    def batterystatus():
        """Batteristatus"""
        #Cykeln varnar när den behöver laddas.
        pass

    def bike_logg():
        """Logg för cykeln"""
        #Cykeln sparar en logg över sina resor med 
        #start (plats, tid) och slut (plats, tid) samt kund.
        pass

    def service_mode():
        """Uträkning när service behövs"""
        #När cykeln tas in för underhåll eller laddning 
        #så markeras det att cykeln är i underhållsläge. 
        #En cykel som laddas på en laddstation kan inte 
        #hyras av en kund och en röd lampa visar att den 
        #inte är tillgänglig.
        pass