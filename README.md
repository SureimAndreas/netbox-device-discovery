# netbox-device-discovery
A tool to discover devices using nmap and adds them to netbox

The tool will also connect to the device using napalm and collect the interfaces and make connections.

Currently supports Cisco IOS and JUNOS. 

Check https://napalm.readthedocs.io/en/latest/support/index.html#getters-support-matrix for what other devices that can be supported.

Its important that the devices are in dns, or you have a hostname in the host file. (have not made any error handling for that yet)

# Change these variables in the code before running it:
API_TOKEN = "_TOKEN_"

NB_URL = "https://_IP_ADDRESS_"

nm.scan(hosts="_SUBNET/MASK_", arguments="-sV")

username="_USERNAME_",
password="_PASSWORD_",

# JUNOS SPESIFIC

For the devices to be able to gather lldp data for the remote interfaces, you have to have these settings configured:

set protocols lldp port-id-subtype interface-name
set protocols lldp interface all

output:

JUNOS> show lldp neighbors 
Local Interface    Parent Interface    Chassis Id          Port info          System Name
ge-0/0/0           -                   2c:6b:f5:57:7e:c0   ge-0/0/0           vennesla-pe1        
ge-0/0/1           -                   2c:6b:f5:57:7e:c0   ge-0/0/1           vennesla-pe1        
ge-0/0/2           -                   2c:6b:f5:57:7e:c0   ge-0/0/2           vennesla-pe1  

Otherwise the port info would only show a port id.

- Changes to come:
