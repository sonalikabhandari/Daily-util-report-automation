import csv
from netmiko import ConnectHandler
import sys
import pandas as pd
import re
from bs4 import BeautifulSoup as Soup
#import inquirer

devices = []
response = ""
data = []
data_cisco = []
Hostname = []
df_new = pd.DataFrame()
df_cisco = pd.DataFrame()
#questions = [
#  inquirer.List('type',
#                message="Filename?",
#                choices=['CHARTER', 'TWC'],
#            ),
#]
#answers = inquirer.prompt(questions)
#print (answers)
fileinput = str(input("Filename:")).upper()
if not ".csv" in fileinput:
    fileinput += ".csv"
if (fileinput == "CHARTER.csv"):
    with open("CHARTER.csv", "r") as file_h:
        for record in csv.DictReader(file_h):
            devices.append(record)

    for device in devices:
        with ConnectHandler(ip=device["IP"],
                               # port=device["ssh_port"],
                                username=device["username"],
                                password=device["password"],
                                device_type=device["device_type"]) as connect_h:
                                if (device["device_type"] == 'juniper_junos'):
                                    response =  connect_h.send_command_expect("show bgp summary | display xml")
                                    hostname = connect_h.find_prompt()
                                    m = re.findall('@([\w\[\]`!@#$%\^&*()={}:;<>+-]*)>',hostname)
                                    fd = open('junos-bgp_new.xml', 'w')
                                    fd.write(response.strip())
                                    fd.close()
                                    with open('junos-bgp_new.xml') as fd:
                                        cmdout = fd.read()

                                    modnum = 0

                                    soup = Soup(cmdout, 'xml')
                                    Peer = []
                                    AS = []
                                               # InPkt = []
                                               # OutPkt = []
                                                #OutQ = []
                                    Flap = []
                                    Up_Down = []
                                    Peer_State = []
                                    Name = []
                                    Active_prefix_count = []
                                    Received_prefix_count = []
                                    Accepted_prefix_count = []
                                    Suppressed_prefix_count = []
                                #    Hostname = []
                                    for mod in soup.find_all('bgp-peer'):
                                        modnum += 1

                                        peer= mod.find('peer-address').text
                                        as_number = mod.find('peer-as').text
                                            #InPkt = mod.find('input-messages').text
                                            #OutPkt = mod.find('output-messages').text
                                            #OutQ = mod.find('route-queue-count').text
                                        flap = mod.find('flap-count').text
                                        up_Down = mod.find('elapsed-time').text
                                           # Peer_State.append(mod.find('peer-state').get('junos:format')
                                        peer_State = mod.find('peer-state').text
                                        name = None
                                        active_prefix_count = None
                                        received_prefix_count = None
                                        accepted_prefix_count = None
                                        suppressed_prefix_count = None

                                        children = mod.findChildren("bgp-rib" , recursive=False)
                                        for child in children:
                                            name = child.find('name').text
                                            active_prefix_count = child.find('active-prefix-count').text
                                            received_prefix_count = child.find('received-prefix-count').text
                                            accepted_prefix_count = child.find('accepted-prefix-count').text
                                            suppressed_prefix_count = child.find('suppressed-prefix-count').text

                                        Peer.append(peer)
                                        Hostname.append(m[0])
                                        AS.append(as_number)
                                        Flap.append(flap)
                                        Up_Down.append(up_Down)
                                        Peer_State.append(peer_State)
                                        Name.append(name)
                                        Active_prefix_count.append(active_prefix_count)
                                        Received_prefix_count.append(received_prefix_count)
                                        Accepted_prefix_count.append(accepted_prefix_count)
                                        Suppressed_prefix_count.append(suppressed_prefix_count)
                                        data = [Hostname, Peer,AS,Flap,Up_Down, Peer_State,Name,Active_prefix_count,Received_prefix_count,Accepted_prefix_count,Suppressed_prefix_count]
                                        df = pd.DataFrame(data)

                                        df = df.T

                                    df_new = df_new.append(df)
                                    df_new.columns = ['Hostname','Peer', 'AS','Flap','Up_Down','Peer_State','Name','Active_prefix_count','Received_prefix_count','Accepted_prefix_count','Suppressed_prefix_count']

                                elif (device["device_type"] == 'cisco_xr'):
                                    response =  connect_h.send_command_expect("admin show platform",use_textfsm=True)
                                    data_cisco.append(response)
                                    df_cisco = pd.DataFrame(data_cisco).stack().apply(pd.Series)
                                        #Juniper_data.append(data)
                                        #print(df)
    print(df_new)
    print(df_cisco)


elif (fileinput == "TWC.csv"):
    with open("TWC.csv", "r") as file_h:
        for record in csv.DictReader(file_h):
            devices.append(record)

    for device in devices:
        with ConnectHandler(ip=device["IP"],
                               # port=device["ssh_port"],
                                username=device["username"],
                                password=device["password"],
                                device_type=device["device_type"]) as connect_h:
                                if (device["device_type"] == 'juniper_junos'):
                                    response =  connect_h.send_command_expect("show bgp summary | display xml")
                                    hostname = connect_h.find_prompt()
                                    print(hostname)
                                    m = re.findall('@([\w\[\]`!@#$%\^&*()={}:;<>+-]*)>',hostname)
                                    fd = open('junos-bgp_new.xml', 'w')
                                    fd.write(response.strip())
                                    fd.close()
                                    with open('junos-bgp_new.xml') as fd:
                                        cmdout = fd.read()

                                    modnum = 0

                                    soup = Soup(cmdout, 'xml')
                                    Peer = []
                                    AS = []
                                               # InPkt = []
                                               # OutPkt = []
                                                #OutQ = []
                                    Flap = []
                                    Up_Down = []
                                    Peer_State = []
                                    Name = []
                                    Active_prefix_count = []
                                    Received_prefix_count = []
                                    Accepted_prefix_count = []
                                    Suppressed_prefix_count = []
                                    Hostname = []
                                    for mod in soup.find_all('bgp-peer'):
                                        modnum += 1

                                        peer= mod.find('peer-address').text
                                        as_number = mod.find('peer-as').text
                                            #InPkt = mod.find('input-messages').text
                                            #OutPkt = mod.find('output-messages').text
                                            #OutQ = mod.find('route-queue-count').text
                                        flap = mod.find('flap-count').text
                                        up_Down = mod.find('elapsed-time').text
                                           # Peer_State.append(mod.find('peer-state').get('junos:format')
                                        peer_State = mod.find('peer-state').text
                                        name = None
                                        active_prefix_count = None
                                        received_prefix_count = None
                                        accepted_prefix_count = None
                                        suppressed_prefix_count = None

                                        children = mod.findChildren("bgp-rib" , recursive=False)
                                        for child in children:
                                            name = child.find('name').text
                                            active_prefix_count = child.find('active-prefix-count').text
                                            received_prefix_count = child.find('received-prefix-count').text
                                            accepted_prefix_count = child.find('accepted-prefix-count').text
                                            suppressed_prefix_count = child.find('suppressed-prefix-count').text

                                        Peer.append(peer)
                                        Hostname.append(m[0])
                                        AS.append(as_number)
                                        Flap.append(flap)
                                        Up_Down.append(up_Down)
                                        Peer_State.append(peer_State)
                                        Name.append(name)
                                        Active_prefix_count.append(active_prefix_count)
                                        Received_prefix_count.append(received_prefix_count)
                                        Accepted_prefix_count.append(accepted_prefix_count)
                                        Suppressed_prefix_count.append(suppressed_prefix_count)
                                        data = [Hostname, Peer,AS,Flap,Up_Down, Peer_State,Name,Active_prefix_count,Received_prefix_count,Accepted_prefix_count,Suppressed_prefix_count]
                                        df = pd.DataFrame(data)

                                        df = df.T

                                    df_new = df_new.append(df)
                                    df_new.columns = ['Hostname','Peer', 'AS','Flap','Up_Down','Peer_State','Name','Active_prefix_count','Received_prefix_count','Accepted_prefix_count','Suppressed_prefix_count']

                                elif (device["device_type"] == 'cisco_xr'):
                                    response  =  connect_h.send_command_expect("admin show platform",use_textfsm = True)
                                    hostname2 = connect_h.find_prompt()
                                    #print(hostname2)
                                    m = re.findall('(?<=>)[^<:]+(?=:?<)',hostname2)
                                    print(m)
                                    #Hostname.append(m)
                                    data_cisco.append(response)
                                    df_cisco = pd.DataFrame(data_cisco).stack().apply(pd.Series)
                                    df =

                                    #print(Hostname)
                                    #hostname = connect_h.find_prompt()
                                    #m = re.findall('@([\w\[\]`!@#$%\^&*()={}:;<>+-]*)>',hostname)
                                    #Hostname = []
                                    #Hostname.append(m)
                                    #print(Hostname)
                                    #df_cisco['Hostname'] = Hostname   #Juniper_data.append(data)
                                        #print(df)
    print(df_new)
    print(df_cisco)




#df_new.to_csv('Juniper_output24.csv')
#df_cisco.to_csv('Juniper_output34.csv')
                                    #Hostname.append(hostname)

                              #df =  df.append(data)
                                        #data.append(df)
