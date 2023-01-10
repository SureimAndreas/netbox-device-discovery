import pynetbox
import nmap
from napalm import get_network_driver
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

API_TOKEN = "TOKEN"
NB_URL = "URL"

def add_device_to_netbox(driver, device_name):
    # create a new device in Netbox
    nb = pynetbox.api(f'{NB_URL}',token=f'{API_TOKEN}')
    nb.http_session.verify = False

    existing_device = nb.dcim.devices.get(name=device_name)
    if existing_device:
        print(f"\nThe device {device_name} already exists..")
        # Gather the serial number using NAPALM
        facts = driver.get_facts()
        serial_number = facts["serial_number"]
        
        # check if the serial number already exists 
        if serial_number != existing_device.serial:
            print(f"Updating the serial number for {device_name}")
            existing_device.update(dict(serial=serial_number))
        else:
            print(f"The device {device_name} already exists with correct serial number.. ")
        return existing_device.id
    else:
        # Gather the serial number using NAPALM
        facts = driver.get_facts()
        serial_number = facts["serial_number"]
        
        # Define the attributes of the new device
        print(f"\nAdding the device: {device_name} to netbox with {serial_number}")
        nb.dcim.devices.create(
            name=device_name,
            device_role=3,
            device_type=2,
            site=3,
            serial=serial_number, 
        )
        return nb.dcim.devices.get(name=device_name).id


    

def add_interfaces_to_netbox(device_id, interfaces):
    nb = pynetbox.api(f'{NB_URL}',token=f'{API_TOKEN}')
    nb.http_session.verify = False
    print(f"Trying to add a total of {len(interfaces)} interfaces to the device\n")
    for interface in interfaces:
        existing_interface = nb.dcim.interfaces.get(device=device_id, name=interface)
        if existing_interface is None:
            try:
                # create a new interface in Netbox
                nb.dcim.interfaces.create(
                    name=interface,
                    device=device_id,
                    type="1000base-t"
                )
                print(f"Adding interface: {interface}..")
            except pynetbox.core.query.RequestError as error:
                print(f"Interface {interface} already exists.. skipping")         
            


def main() -> None:
    # use Nmap to scan the network and get a list of active devices
    nm = nmap.PortScanner()
    nm.scan(hosts="SUBNET/MASK", arguments="-sV")
    for host in nm.all_hosts():
        hostname = nm[host]["hostnames"][0]["name"]
        if nm[host].state() == "up":
            vendor = "Juniper" # just while testing, as nmap cant find vendor when the device is a vm in eve-ng
#            vendor = nm[host]["vendor"]["name"]
        # determine the device's operating system
        if vendor == "Juniper":
            os_type = "junos"
        elif vendor == "Cisco":
            os_type = "ios"
        else:
            continue

        # create a Napalm driver object and use it to connect to the device
        driver = get_network_driver(os_type)        
        device_conn = driver(
            hostname=host,
            username="USERNAME",
            password="PASSWORD",
        )
        device_conn.open()

        # get the device's interface information
        if os_type == "ios":
            interfaces = device_conn.get_interfaces()
            interface_names = [name for name in interfaces]
        elif os_type == "junos":
            interfaces = device_conn.get_interfaces_counters()
            interface_names = list(interfaces.keys())
            #print(interface_names)
            
        neighbors = device_conn.get_lldp_neighbors()    
        # add the device to Netbox
        device_id = add_device_to_netbox(device_conn, hostname)

        add_interfaces_to_netbox(device_id, interface_names)

        for local_interface, neighbor_info in neighbors.items():
            # get the remote device name and interface
            remote_device_name = neighbor_info[0]['hostname']
            remote_interface = neighbor_info[0]['port']
            # use pynetbox to get the local and remote interface objects
            nb = pynetbox.api(f'{NB_URL}',token=f'{API_TOKEN}')
            nb.http_session.verify = False
            local_interface_obj = nb.dcim.interfaces.get(device_id=device_id,name=local_interface)
            remote_device_obj = nb.dcim.devices.get(name=remote_device_name)
            try:
                nb.dcim.interfaces.get(device_id=remote_device_obj.id, name=remote_interface)
            except AttributeError:
                continue
            remote_interface_obj = nb.dcim.interfaces.get(device_id=remote_device_obj.id, name=remote_interface)
            # create a connection between the local and remote interfaces
            try:
                if local_interface_obj and remote_interface_obj:
                    nb.dcim.cables.create(
                    termination_a_type="dcim.interface",
                    termination_a_id=local_interface_obj.id,
                    termination_b_type="dcim.interface",
                    termination_b_id=remote_interface_obj.id
                    )
                    print(f"\nCreating Cabling between {local_interface_obj} on {hostname} and {remote_interface_obj} on {remote_device_obj}!\n")
            except pynetbox.core.query.RequestError as e:
                # code to handle the RequestError
                if "already has a cable attached" in str(e):
                # skip the current iteration if the error message contains this string
                    continue
                print(f"\nInterface {local_interface_obj} on {hostname} and {remote_interface_obj} on {remote_device_obj} is already connected\n")
            


if __name__ == "__main__":
    main()
