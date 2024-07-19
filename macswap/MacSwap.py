import subprocess
import optparse
import re
import os
import json

def get_user_input():
    parse_object = optparse.OptionParser()
    parse_object.add_option("-i", "--interface", dest="interface", help="Interface that you want to change")
    parse_object.add_option("-m", "--mac", dest="mac_address", help="New MAC address that you want")
    parse_object.add_option("-o", "--original", action="store_true", dest="original", help="Revert to original MAC address")
    return parse_object.parse_args()

def get_current_mac(interface):
    ifconfig = subprocess.check_output(["ifconfig", interface])
    current_mac = re.search(r"\w\w:\w\w:\w\w:\w\w:\w\w:\w\w", str(ifconfig))
    if current_mac:
        return current_mac.group(0)
    else:
        return None

def change_mac_address(interface, mac_address):
    subprocess.call(["ifconfig", interface, "down"])
    subprocess.call(["ifconfig", interface, "hw", "ether", mac_address])
    subprocess.call(["ifconfig", interface, "up"])

def save_original_mac(interface, mac_address):
    filename = f"{interface}_original_mac.json"
    original_macs = {}
    if os.path.exists(filename):
        with open(filename, "r") as file:
            original_macs = json.load(file)
    original_macs[interface] = mac_address
    with open(filename, "w") as file:
        json.dump(original_macs, file)

def get_saved_mac(interface):
    filename = f"{interface}_original_mac.json"
    if os.path.exists(filename):
        with open(filename, "r") as file:
            original_macs = json.load(file)
        return original_macs.get(interface)
    return None

print("MacSwap is started!")
(user_input, arguments) = get_user_input()

if not user_input.interface:
    print("Please specify an interface using the -i option.")
    exit()

if user_input.original:
    original_mac = get_saved_mac(user_input.interface)
    if original_mac:
        change_mac_address(user_input.interface, original_mac)
        finalized_mac = get_current_mac(user_input.interface)
        if finalized_mac == original_mac:
            print("MAC address is back to original!")
        else:
            print("Error going back to original MAC address!")
    else:
        print("Original MAC address not found! Please run the script with a new MAC address first to save the original MAC.")
elif user_input.mac_address:
    original_mac = get_current_mac(user_input.interface)
    save_original_mac(user_input.interface, original_mac)
    change_mac_address(user_input.interface, user_input.mac_address)
    finalized_mac = get_current_mac(user_input.interface)
    if finalized_mac == user_input.mac_address:
        print("MAC address has been swapped!")
    else:
        print("Error swapping MAC address!")
else:
    print("Please specify a MAC address using the -m option.")
