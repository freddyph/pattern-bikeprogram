#!/usr/bin/env python3
"""
Simuleringsprogram för skapandet av personer, cyklar och simulera körning.
"""
import concurrent.futures
import sys
from decouple import config
import requests
#from requests.api import head
import funktioner

LINK = config('SERVER')
SUM = []

API_KEY = config('JWT_SECRET')
headers = {'x-access-token': API_KEY}
#simuleringar = int(input("Hur många simuleringar vill du göra? "))

def starta_simulering(job):
    """Simulering per jobb"""
    print(f"--- Starta simulering nr {job[0]} ----")
    simulera(job[1], 1)
    print(f"--- Simulering nr {job[0]} avslutad ----")

def start_simulations(jobb):
    """Användning av concurrent futures"""
    with concurrent.futures.ProcessPoolExecutor() as executor:
        executor.map(starta_simulering, jobb)

def simulera(stad,antal_simuleringar):
    """Simulering i specifik stad samt antal simuleringar som ska köras"""
    priser = requests.get(LINK+"prices",headers=headers).json()
    pris_per_minut = priser["prices"][0]["price_per_minute"]
    #print(pris_per_minut)
    start_avgift = priser["prices"][0]["starting_fee"]
    #print(start_avgift)
    straffavgift = priser["prices"][0]["penalty_fee"]
    #print(straffavgift)
    minimum_tid =pris_per_minut+start_avgift+straffavgift
    #print(minimum_tid)
    #print(priser)
    j = 1
    while j < antal_simuleringar+1:
        #Välj person
        person_id = funktioner.välj_en_person()
        person = requests.get(LINK+"users/"+person_id, headers=headers).json()

        #Skapa lista över staden
        lista_stad =funktioner.skapa_lista_stad(stad)

        #Hämta parkeringar i staden
        kontroller_stad = LINK+"cities/stations/"+stad
        parkeringar = requests.get(kontroller_stad, headers=headers).json()

        #Välj cykel
        cykel_id = funktioner.välj_en_cykel_i_stad(lista_stad)
        #Kontrollera cykelns status
        cykel = requests.get(LINK+'bikes/'+cykel_id, headers=headers).json()
        #Kontrollera om ledig
        try:
            bike_status = cykel["bike"]["bike_status"]
            status_batteri =float(cykel["bike"]["battery_status"])
            balans_konto = person["user"]["balance"]
        #Kontrollera batteri och saldo
            if bike_status == "available" and status_batteri > 1.2 and balans_konto > minimum_tid:
                print("Grönt ljus")

            #Sätt lat och long

                lat = cykel["bike"]["coordinates"]["lat"]
                long = cykel["bike"]["coordinates"]["long"]
                parkering = funktioner.kontroll_plats_parkering(lat,long,parkeringar)
                laddning = funktioner.kontroll_plats_laddstation(lat,long,parkeringar)
                #print("Start-coordinater: ", lat, long)
                #Starta resan
                id_resan = funktioner.starta_resan(person_id,cykel_id,lat,long)
                response_resa = requests.get(LINK+'trips/'+id_resan, headers=headers).json()
                #priser = requests.get(LINK+"prices", headers=headers).json()
                #info = {
                #    "person_id":person_id,
                #    "cykel_id": cykel_id,
                #    "balans_konto": balans_konto,
                #    "id_resan": id_resan,
                #    "response_resa": response_resa,
                #    "priser": priser,
                #    "parkeringar": parkeringar,
                #    "parkering": parkering,
                #    "laddning": laddning
                #}
                #print(info)
                funktioner.slumpa_riktning(
                    person_id,
                    cykel_id,
                    balans_konto,
                    id_resan,
                    response_resa,
                    priser,
                    parkeringar,
                    parkering,
                    laddning,
                    pris_per_minut,
                    minimum_tid)

                #Avsluta resa
                cykel = requests.get(LINK+'bikes/'+cykel_id, headers=headers).json()
                lat = cykel["bike"]["coordinates"]["lat"]
                long = cykel["bike"]["coordinates"]["long"]
                batteri_status = cykel["bike"]["battery_status"]
                hastighet = cykel["bike"]["latest_trip"]["average_speed"]
                sträcka = cykel["bike"]["latest_trip"]["distance"]
                #print("lat inför avslutning:",lat)
                parkering = funktioner.kontroll_plats_parkering(lat,long,parkeringar)
                laddning = funktioner.kontroll_plats_laddstation(lat,long,parkeringar)
                summa = funktioner.calculate_trip(priser,1, parkering, laddning)
                SUM.append(summa)
                funktioner.avslutning_cykel(
                batteri_status,
                lat,
                long,
                cykel_id,
                hastighet,
                sträcka,
                summa,
                laddning,
                parkering)
                funktioner.avsluta_resa(id_resan,lat,long)
                balans_konto -= summa
                funktioner.uppdatera_saldo(person_id,balans_konto)
            else:
                print("Nu blev det tokigt")
        except: # pylint: disable=bare-except
            print("Uppfyller ej kraven")
        print("Simulering klar")
        j += 1

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
            simuleringar = int(input("Hur många simuleringar vill du göra? "))
            jobs = []
            for i in range(1,simuleringar+1):
                jobs.append((i, STAD))
            start_simulations(jobs)
            #simulera(STAD, 1)
        elif OPTION == 3:
            print('Avslutar simuleringsprogrammet')
            sys.exit()
        else:
            print('Du måste ange ett nummer!')
