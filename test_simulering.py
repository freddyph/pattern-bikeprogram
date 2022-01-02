"""Testning av simuleringsfilen"""
#from simulering import simulera
from threading import Thread
import asyncio
import simulering

async def main():
    simulering.simulera("61a76026bb53f131584de9b1",5)
    await other_function()
    print("1")

async def other_function():
    simulering.simulera("61a76026bb53f131584de9b1",5)
    print("2")
asyncio.run(main())

Thread(target = simulering.simulera("61a76026bb53f131584de9b1",5)).start()
Thread(target = simulering.simulera("61a76026bb53f131584de9b1",5)).start()  
