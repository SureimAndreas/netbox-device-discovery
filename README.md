# netbox-device-discovery
A tool to discover devices and adds them to netbox. 

The tool will also connect to the device using napalm and collect the interfaces and make connections.

Currently supports Cisco IOS and JUNOS. 

Check https://napalm.readthedocs.io/en/latest/support/index.html#getters-support-matrix for what other devices that can be supported.

Change these variables in the code before running it:

API_TOKEN = "_TOKEN_"

NB_URL = "https://_IP_ADDRESS_"

nm.scan(hosts="_SUBNET/MASK_", arguments="-sV")

username="_USERNAME_",
password="_PASSWORD_",
