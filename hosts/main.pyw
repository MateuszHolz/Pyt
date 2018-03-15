import time
from datetime import datetime as dt

hosts_temp = r"hosts"
hosts_path = r"c:\windows\system32\drivers\etc\hosts"
redirect = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQBEWuA4M1BEmGgq_iFZlm2_uJlAtz78M_TiEh61YSlBixO5zhP"
website_list = [ "www.facebook.com", "facebook.com" ]
startHours = dt( dt.now( ).year, dt.now( ).month, dt.now( ).day, 17, 27 ) # 8am
finishHours = dt( dt.now( ).year, dt.now( ).month, dt.now( ).day, 17, 28 ) # 4pm
banList = [ ]
tempHostsList = [ ]
cleanHostList= [ ]
for i in range( len( website_list ) ):
    banList.append( "{} {}\n".format( redirect, website_list[i] ) ) #tworzenie banned listy
with open( hosts_temp, 'r' ) as f:
    for i in f.readlines():
        tempHostsList.append( i )#tworzenie listy ze wszystkimi liniami z pliku hosts
with open( hosts_temp, 'w' ) as f:
    for i in tempHostsList:
        if i not in banList:
            f.write( i )
            cleanHostList.append( i )#tworzenie pliku hosts bez żadnych elementów z banned listy
while True:
    if( startHours < dt.now( ) < finishHours ):
        with open( hosts_temp, 'r+' ) as f:
            for i in banList:
                if i in f.read( ):
                    pass
                else:
                    f.write( i )
    else:
        with open( hosts_temp, 'w' ) as f:
            for i in cleanHostList:
                f.write( i )
    time.sleep( 5 )
