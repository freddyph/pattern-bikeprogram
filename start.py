#!/usr/bin/env python3
"""
Cykelns program.
"""
import time as t
import sys
import requests
import funktioner
from decouple import config

#API-länkar
BIKE_ID = input("Ange cykel-id:")
USER_ID = input("Ange användar-id:")
#BIKE_ID = "61a8aec803d845a108c53774"
#USER_ID = "619f6ee3d0b6c914a2b58514"
LINK = "http://localhost:1337/v1/"
SUM = []
API_KEY = config('JWT_SECRET')
headers = {'x-access-token': API_KEY}
cykel = requests.get(LINK+"bikes/"+BIKE_ID,headers=headers).json()
TEXT = "I vilken riktning vill du åka? (norr, söder, öster, väster) (Avsluta med q/Q) "
cykel_info ={
    '_id': cykel['bike']['_id'],
    'city_id': cykel['bike']['city_id'],
    'charge_id': cykel['bike']['charge_id'],
    'parking_id': cykel['bike']['parking_id'],
    'bike_status': cykel['bike']['bike_status'],
    'battery_status': cykel['bike']['battery_status'],
    'coordinates': {
        'lat': cykel['bike']['coordinates']['lat'],
        'long': cykel['bike']['coordinates']['long']
    },
    'maintenance': cykel['bike']['maintenance'],
    'latest_trip': {
        'average_speed': cykel['bike']['latest_trip']['average_speed'],
        'distance':	cykel['bike']['latest_trip']['distance'],
        'price':	cykel['bike']['latest_trip']['price'],
        'charge_id': cykel['bike']['latest_trip']['charge_id'],
        'parking_id': cykel['bike']['latest_trip']['parking_id']
    }
    }
stad_cykel = cykel["bike"]["city_id"]
user = requests.get(LINK+"users/"+USER_ID,headers=headers).json()
stad = requests.get(LINK+"cities",headers=headers).json()
priser = requests.get(LINK+"prices",headers=headers).json()
kontroller_stad = LINK+"cities/stations/"+stad_cykel
parkeringar = requests.get(kontroller_stad,headers=headers).json()

#Kunduppgifter
kundens_id = user["user"]["_id"]
balans_konto = user["user"]["balance"]
status_batteri =float(cykel["bike"]["battery_status"])

#Kostnadsuppgifter
pris_per_minut = priser["prices"][0]["price_per_minute"]
start_avgift = priser["prices"][0]["starting_fee"]
straffavgift = priser["prices"][0]["penalty_fee"]
avdrag_bra_parkering = priser["prices"][0]["discount"]
rese_tid = balans_konto / pris_per_minut
tid_att_resa = funktioner.travel_time(pris_per_minut,BIKE_ID,USER_ID)

def resa(text_för_riktning,info_cykel,tid):
    """För resor"""
    cykel_länk = requests.get(LINK+"bikes/"+BIKE_ID,headers=headers).json()
    usern = requests.get(LINK+"users/"+USER_ID,headers=headers).json()
    konto_balans = usern["user"]["balance"]
    #lat = info_cykel["coordinates"]["lat"]
    #print(lat)
    #info_cykel["coordinates"]["lat"]+= 0.001
    lat = cykel_länk["bike"]["coordinates"]["lat"]
    #lat += 0.001
    long = cykel_länk["bike"]["coordinates"]["long"]
    #long = info_cykel["coordinates"]["lat"]
    #print(info_cykel["coordinates"]["lat"])
    #batteri_status =float(cykel_länk["bike"]["battery_status"])
    batteri_status = info_cykel["battery_status"]
    id_resan= funktioner.starta_resan(USER_ID,BIKE_ID,lat,long)
    response_resa = requests.get(LINK+'trips/'+id_resan,headers=headers).json()
    vädersträck = ["norr", "söder", "öster", "väster"]
    riktning = input(text_för_riktning)
    sträcka = 0

    while True:
        print("Check av batteri & konto")
        if batteri_status < 1.2 or konto_balans < 63:
            funktioner.avsluta_resa(id_resan,lat,long)
            break
        if riktning in vädersträck:
            print(f"Du färdas {riktning}")
            if riktning == "norr":
                lat+= 0.001
                lat = round(lat,6)
                lat = funktioner.kontrollera_lat(lat,cykel["bike"]["city_id"])
                batteri_status -= 1.2
                sträcka += 57
                minuter =funktioner.räkna_minuter(response_resa)
                hastighet = funktioner.räkna_och_sätt_medelhastighet(sträcka,minuter)
                pris = funktioner.calculate_trip(priser, minuter)

                if funktioner.kontroll_tid_batteri_saldo(tid,batteri_status,pris,konto_balans):
                    print("Avslutar resa då du har för lite batteri/pengar på ditt saldo")
                    funktioner.avsluta_resa(id_resan,lat,long)
                    konto_balans -= pris
                    funktioner.uppdatera_saldo(USER_ID,konto_balans)
                    break
                t.sleep(1)
                parkering = funktioner.kontroll_plats_parkering(lat,long,parkeringar)
                laddning = funktioner.kontroll_plats_laddstation(lat,long,parkeringar)
                funktioner.uppdatera_cykel(
                batteri_status,
                lat,
                long,
                BIKE_ID,
                hastighet,
                sträcka,
                pris,laddning,parkering)
            elif riktning == "söder":
                lat-= 0.001
                lat = round(lat,6)
                lat = funktioner.kontrollera_lat(lat,cykel["bike"]["city_id"])
                batteri_status -= 1.2
                sträcka += 57
                minuter =funktioner.räkna_minuter(response_resa)
                hastighet = funktioner.räkna_och_sätt_medelhastighet(sträcka,minuter)
                pris = funktioner.calculate_trip(priser, minuter)
                konto_balans -= pris
                if funktioner.kontroll_tid_batteri_saldo(tid,batteri_status,pris,konto_balans):
                    print("Avslutar resa då du har för lite batteri/pengar på ditt saldo")
                    funktioner.avsluta_resa(id_resan,lat,long)
                    konto_balans -= pris
                    funktioner.uppdatera_saldo(USER_ID,konto_balans)
                    break
                t.sleep(1)
                funktioner.uppdatera_cykel(
                batteri_status,
                lat,
                long,
                BIKE_ID,
                hastighet,
                sträcka,
                pris)
            elif riktning == "öster":
                long += 0.001
                long = round(long,6)
                long = funktioner.kontrollera_long(long,cykel["bike"]["city_id"])
                batteri_status -= 1.2
                sträcka += 57
                minuter =funktioner.räkna_minuter(response_resa)
                hastighet = funktioner.räkna_och_sätt_medelhastighet(sträcka,minuter)
                pris = funktioner.calculate_trip(priser, minuter)

                if funktioner.kontroll_tid_batteri_saldo(tid,batteri_status,pris,konto_balans):
                    print("Avslutar resa då du har för lite batteri/pengar på ditt saldo")
                    funktioner.avsluta_resa(id_resan,lat,long)
                    konto_balans -= pris
                    funktioner.uppdatera_saldo(USER_ID,konto_balans)
                    break
                t.sleep(1)
                funktioner.uppdatera_cykel(
                batteri_status,
                lat,
                long,
                BIKE_ID,
                hastighet,
                sträcka,
                pris)
            elif riktning == "väster":
                long -= 0.001
                long = round(long,6)
                long = funktioner.kontrollera_long(long,cykel["bike"]["city_id"])
                batteri_status -= 1.2
                sträcka += 57
                minuter =funktioner.räkna_minuter(response_resa)
                hastighet = funktioner.räkna_och_sätt_medelhastighet(sträcka,minuter)
                pris = funktioner.calculate_trip(priser, minuter)

                if funktioner.kontroll_tid_batteri_saldo(tid,batteri_status,pris,konto_balans):
                    print("Avslutar resa då du har för lite batteri/pengar på ditt saldo")
                    funktioner.avsluta_resa(id_resan,lat,long)
                    konto_balans -= pris
                    funktioner.uppdatera_saldo(USER_ID,konto_balans)
                    break
                t.sleep(1)
                funktioner.uppdatera_cykel(
                batteri_status,
                lat,
                long,
                BIKE_ID,
                hastighet,
                sträcka,
                pris)
            text_riktning="I vilken riktning vill du åka?(norr, söder, öster, väster) (Avslut q/Q) "
            riktning = input(text_riktning)

        elif riktning in ('q', 'Q'):
            #Avsluta resa
            #cykel_ny = requests.get(LINK+'bikes/'+BIKE_ID,headers=headers).json()
            #lat = cykel_ny["bike"]["coordinates"]["lat"]
            #long = cykel_ny["bike"]["coordinates"]["long"]
            response_resa = requests.get(LINK+'trips/'+id_resan,headers=headers).json()
            print(response_resa)
            minuter =funktioner.räkna_minuter(response_resa)
            parkering = funktioner.kontroll_plats_parkering(lat,long,parkeringar)
            laddning = funktioner.kontroll_plats_laddstation(lat,long,parkeringar)
            summa = funktioner.calculate_trip(priser,minuter, parkering, laddning)
            konto_balans -= summa
            hastighet = funktioner.räkna_och_sätt_medelhastighet(sträcka,minuter)
            funktioner.avsluta_resa(id_resan,lat,long)
            funktioner.uppdatera_cykel(
                batteri_status,
                lat,
                long,
                BIKE_ID,
                hastighet,
                sträcka,
                summa,
                laddning,
                parkering)
            funktioner.uppdatera_saldo(USER_ID,konto_balans)
            break
        else:
            print("Fel riktning, testa igen")
            text_riktning="I vilken riktning vill du åka?(norr, söder, öster, väster) (Avslut q/Q) "
            riktning = input(text_riktning)

if __name__=='__main__':
    while True:
        funktioner.print_menu()
        OPTION = ''
        try:
            OPTION = int(input('Gör ett val: '))
        except: # pylint: disable=bare-except
            print('Du angav inte en giltig siffra ...')
        #Kontrollera val
        if OPTION == 1:
            resa(TEXT,cykel_info,tid_att_resa)
        elif OPTION == 2:
            print('Avslutar cykelns program')
            sys.exit()
        else:
            print('Du måste ange ett nummer!')
