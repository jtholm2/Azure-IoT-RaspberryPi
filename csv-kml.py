import csv, sys, re
import pandas as pd
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobClient, ContainerClient

def format_csv(fileToFormat):
    list = []
    with open(fileToFormat, mode='r') as csv_file:
        keys = csv_file.readline().strip().split(',')
        for line in csv_file:
            line = line.strip()
            row = re.split(r'(?!\s),(?!\s)',line)
            list.append(dict(zip(keys, row)))

    formattedCsv = pd.DataFrame(list)

    return (formattedCsv.drop_duplicates(subset=[' BSSID', ' Latitude', ' Longitude']))

def makeKml():
    data = format_csv(sys.argv[1])
    f = open(f'{sys.argv[1]}.kml', 'w')

    #Writing the kml file.
    f.write("<?xml version='1.0' encoding='UTF-8'?>\n")
    f.write("<kml xmlns='http://earth.google.com/kml/2.1'>\n")
    f.write("<Document>\n")
    f.write("   <name>" + 'test.kml' +"</name>\n")
    for index, row, in data.iterrows():
        if(row[' Latitude'] != '0.000000' and row[' Longitude']!= '0.000000'):
            f.write("   <Placemark>\n")
            f.write("       <name>" + str(row[3]) + "</name>\n")
            f.write("       <description>" + str(row[3]) + "</description>\n")
            f.write("       <Point>\n")
            f.write("           <coordinates>" + str(row[7]) + "," + str(row[6]) + "</coordinates>\n")
            f.write("       </Point>\n")
            f.write("   </Placemark>\n")
    f.write("</Document>\n")
    f.write("</kml>\n")
    f.close()

def uploadFileToAzure():
    conn_string = '{storage connection string}'
    kmlContainer = BlobClient.from_connection_string(conn_string, container_name='rpi-kmls', blob_name=f'{sys.argv[1]}.kml')
    csvContainer = BlobClient.from_connection_string(conn_string, container_name='rpi-csvs', blob_name=f'{sys.argv[1]}')
    with open(f'./{sys.argv[1]}.kml', "rb") as data:
        kmlContainer.upload_blob(data)
    with open(f'./{sys.argv[1]}', "rb") as csvData:
        csvContainer.upload_blob(csvData)

makeKml()
uploadFileToAzure()



