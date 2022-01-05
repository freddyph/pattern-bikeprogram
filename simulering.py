#!/usr/bin/env python3
"""
Simuleringsprogram för skapandet av personer, cyklar och simulera körning.
"""
import requests
import funktioner

LINK = "http://localhost:1337/v1/"
SUM = []
simuleringar = int(input("Hur många simuleringar vill du göra? "))

def simulera(stad,antal_simuleringar):
    """Simulering i specifik stad samt antal simuleringar som ska köras"""
    i = 1
    while i < antal_simuleringar+1:
        #Välj person
        person_id = funktioner.välj_en_person()
        person = requests.get(LINK+"users/"+person_id).json()

        #Skapa lista över staden
        lista_stad =funktioner.skapa_lista_stad(stad)

        #Hämta parkeringar i staden
        kontroller_stad = LINK+"cities/stations/"+stad
        parkeringar = requests.get(kontroller_stad).json()
        #Välj cykel
        cykel_id = funktioner.välj_en_cykel_i_stad(lista_stad)

        #Kontrollera cykelns status
        cykel = requests.get(LINK+'bikes/'+cykel_id).json()

        #Kontrollera om ledig
        try:
            bike_status = cykel["bike"]["bike_status"]
            status_batteri =float(cykel["bike"]["battery_status"])
            balans_konto = person["user"]["balance"]

        #Kontrollera batteri och saldo
            if bike_status == "available" and status_batteri > 0 and balans_konto > 0:
                print("Grönt ljus")

            #Sätt lat och long

            lat = cykel["bike"]["coordinates"]["lat"]
            long = cykel["bike"]["coordinates"]["long"]
            print("Start-coordinater: ", lat, long)
            #Starta resan
            id_resan = funktioner.starta_resan(person_id,cykel_id,lat,long)
            print(id_resan)
            response_resa = requests.get(LINK+'trips/'+id_resan).json()
            priser = requests.get(LINK+"prices").json()
            #Hämta distans-start, för senare beräkningar

            #Slumpa riktning
            funktioner.slumpa_riktning(
            lat,
            long,
            person_id,
            cykel_id,
            balans_konto,
            id_resan,
            response_resa,
            priser)
            #Kontrollera cykelns status, om illa avsluta direkt

            #Avsluta resa
            cykel = requests.get(LINK+'bikes/'+cykel_id).json()
            lat = cykel["bike"]["coordinates"]["lat"]
            long = cykel["bike"]["coordinates"]["long"]
            print("lat inför avslutning:",lat)
            parkering = funktioner.kontroll_plats_parkering(lat,long,parkeringar)
            laddning = funktioner.kontroll_plats_laddstation(lat,long,parkeringar)
            summa = funktioner.calculate_trip(priser,1, parkering, laddning)
            SUM.append(summa)
            funktioner.avsluta_resa(id_resan,lat,long)
        except: # pylint: disable=bare-except
            pass
        print("Simulering",i,"klar")
        i += 1

if __name__=='__main__':
    while True:
        funktioner.print_menu_simulering()
        OPTION = ''
        try:
            OPTION = int(input('Gör ett val: '))
        except: # pylint: disable=bare-except
            print('Du angav inte en giltig siffra ...')
        #Kontrollera val
        if OPTION == 1:
            STAD = funktioner.välja_stad()
            funktioner.skapa_data_personer(STAD)
            funktioner.skapa_data_cyklar(STAD)
        elif OPTION == 2:
            STAD = funktioner.välja_stad()
            simulera(STAD, simuleringar)
        elif OPTION == 3:
            print('Avslutar simuleringsprogrammet')
            exit()
        else:
            print('Du måste ange ett nummer!')
