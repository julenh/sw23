#Julen Hernando Martin
import json
import os
import signal
import sys
import urllib
import requests
import psutil
import time

user_API_key = "5N5KQVAFEADQ22VA"
nombreCanal = "mi Canal"

#Lectura de CPU y RAM
def cpu_ram():
    return psutil.cpu_percent(), psutil.virtual_memory().percent

#subprograma handler
def handler(sig_num, frame):
    print('\nSignal handler called with signal ' + str(sig_num))
    print('\nExiting gracefully')
    sys.exit()

if __name__ == "__main__":
    #cpu_ram()
    while True:
        print(cpu_ram())
        time.sleep(5)