import requests
import names
import random as rand
from datetime import *
from funktioner import *

link = "http://localhost:1337/"

def simulera(stad):
    
    antal_simuleringar = int(input("Hur många simuleringar vill du göra? "))
    i = 1
    
    while i < antal_simuleringar+1:
        #Välj person
        person_id = välj_en_person()
        person = requests.get(link+"users/"+person_id).json()

        #Skapa lista över staden
        lista_stad =skapa_lista_stad(stad)

        #Välj cykel
        cykel_id = välj_en_cykel_i_stad(lista_stad)

        #Kontrollera cykelns status
        cykel = requests.get(link+'bikes/'+cykel_id).json()
        
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
            id_resan = starta_resan(person_id,cykel_id,lat,long)

            #Hämta distans-start, för senare beräkningar

            #Slumpa riktning
            slumpa_riktning(lat, long, cykel_id)
            #Kontrollera cykelns status, om illa avsluta direkt

            #Avsluta resa
            cykel = requests.get(link+'bikes/'+cykel_id).json()
            lat = cykel["bike"]["coordinates"]["lat"]
            long = cykel["bike"]["coordinates"]["long"]
            plats = kontroll_plats(lat,long,stad)
            summa = calculate_trip(1, plats)
            avsluta_resa(id_resan,lat,long,summa)
        except:
            pass
        print("Simulering",i,"klar")
        i += 1

def skapa_listor_personer_cyklar(stad):
    user = requests.get(link+"users/").json()
    person_id = user["users"][0]["_id"]
    bikes = requests.get(link+"bikes/").json()
    cykel_id = bikes["bikes"][0]["_id"]
    cykel = requests.get(link+'bikes/'+cykel_id).json()
    #Kontrollera om ledig
    bike_status = bikes["bikes"][0]["bike_status"]
    status_batteri =float(cykel["bike"]["battery_status"])
    balans_konto = user["users"][0]["balance"]
    

    #Kontrollera batteri och saldo
    if bike_status == "available" and status_batteri > 0 and balans_konto > 0:
        print("Grönt ljus")
    
    #Sätt lat och long
    lat = bikes["bikes"][0]["coordinates"]["lat"]
    long = bikes["bikes"][0]["coordinates"]["long"]

    #Starta resa
    id_resan = starta_resan(person_id,cykel_id,lat,long)
    
    
    #Slumpa riktning
    slumpa_riktning(lat,long, cykel_id,bikes)
    #Uppdatera batteri, saldo
    #Kontrollera batteri saldo, ev avsluta
    user = requests.get(link+"users/").json()
    bikes = requests.get(link+"bikes/").json()
    cykel = requests.get(link+'bikes/'+cykel_id).json()
    bike_status = bikes["bikes"][0]["bike_status"]
    status_batteri =float(cykel["bike"]["battery_status"])
    balans_konto = user["users"][0]["balance"]
    if status_batteri < 0 or balans_konto < 0:
        print("Slut på det roliga")
        plats = kontroll_plats(lat,long,stad)
        calculate_trip(1,plats)

        

    plats = kontroll_plats(lat,long,stad)
    calculate_trip(1,plats)
    print("En omgång klar.")

if __name__=='__main__':
    while(True):
        print_menu_simulering()
        option = ''
        try:
            option = int(input('Gör ett val: '))
        except:
            print('Du angav inte en giltig siffra ...')
        #Kontrollera val
        if option == 1:
            stad = välja_stad()
            skapa_data_personer(stad)
            skapa_data_cyklar(stad)
        elif option == 2:
            stad = välja_stad()
            simulera(stad)
        elif option == 3:
            print('Avslutar simuleringsprogrammet')
            exit()
        else:
            print('Du måste ange ett nummer!')