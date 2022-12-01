""" decrypt config file and join domain """
import os
import logging
import ctypes
import sys
import io
from datetime import datetime
from subprocess import check_call, CalledProcessError
from configparser import ConfigParser
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

SCRIPT_ROOT = "C:\\SwitchDomain"
ENCRYPTED_CONFIG = SCRIPT_ROOT+"\\config.encrypted"
PRIV_KEY = SCRIPT_ROOT+"\\private_key.pem"
PUB_KEY = SCRIPT_ROOT+"\\public_key.pem"
LEAVE_DOMAIN = SCRIPT_ROOT+"\\LeaveDomain.ps1"
JOIN_DOMAIN = SCRIPT_ROOT+"\\JoinDomain.ps1"

logging.basicConfig(filename=SCRIPT_ROOT+"\\join_domain.log", encoding="utf-8", level=logging.DEBUG)
logging.info("New run:"+ datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

if os.path.exists(LEAVE_DOMAIN) == True:
    logging.error(LEAVE_DOMAIN+" exists... Removing")
    os.remove(LEAVE_DOMAIN)

if os.path.exists(JOIN_DOMAIN) == True:
    logging.error(JOIN_DOMAIN+" exists... Removing")
    os.remove(JOIN_DOMAIN)

if ctypes.windll.shell32.IsUserAnAdmin() == 0:
    logging.error("User is does not have Windows Admin Privileges")
    sys.exit(1)

if os.path.exists(SCRIPT_ROOT) == False:
    logging.error("Path"+SCRIPT_ROOT+"Doesn't Exist")
    sys.exit(1)

if os.path.exists(ENCRYPTED_CONFIG) == False:
    logging.error("Config file doesn't exist")
    sys.exit(1)

if os.path.exists(PRIV_KEY) == False:
    logging.error("Keyfile doesn't exist")
    sys.exit(1)

with open(PRIV_KEY, "rb") as key_file:
    private_key = serialization.load_pem_private_key(
    key_file.read(),
    password=None,
    backend=default_backend()
    )

## I WANT TO CHECK SIGNATURES OF THE FILES TO MAKE SURE THEY HAVEN'T BEEN MODIFIED HERE ##

with open(ENCRYPTED_CONFIG, 'rb') as encrypted_file:
    encrypted_data = encrypted_file.read()
    encrypted_file.close()

CONFIG_DECRYPTED = private_key.decrypt(
    encrypted_data,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)
CONFIG_FILE = io.StringIO(CONFIG_DECRYPTED.decode('utf-8'))
CONFIG_PARSED = ConfigParser()
CONFIG_PARSED.read_string(CONFIG_FILE.getvalue())

PS_JOINSCRIPT = str(
    "if ((get-dnsclientserveraddress | where-object {$_.InterfaceAlias -eq \"Ethernet\"}) -ne $null) "
    +"{ set-dnsclientserveraddress \"Ethernet\" -serveraddresses (\""+CONFIG_PARSED['credentials']['NEWDNS']+"\") }"
    +"\nif ((get-dnsclientserveraddress | where-object {$_.InterfaceAlias -eq \"Wi-Fi\"}) -ne $null) "
    +"{ set-dnsclientserveraddress \"Wi-Fi\" -serveraddresses (\""+CONFIG_PARSED['credentials']['NEWDNS']+"\") }"
    +"\nclear-dnsclientcache"
    +"\nadd-computer -domainname "+CONFIG_PARSED['credentials']['NEWDOMAIN']+" -credential "
    +"(new-object -typename System.Management.Automation.PSCredential -argumentlist \""+CONFIG_PARSED['credentials']['NEWUSER']+"\", "
    +"(convertto-securestring -string \""+CONFIG_PARSED['credentials']['NEWPASS']+"\" -asplaintext -force))"
    +"\nif ($?) { exit 0} else { exit 1 }"
    )

with open(JOIN_DOMAIN, "w") as ps_join:
    ps_join.write(PS_JOINSCRIPT)
    ps_join.close()

CONFIG_FILE.close()

PS_JOINCOMMAND = "powershell.exe -noprofile -executionpolicy bypass -file "+JOIN_DOMAIN

try:
    check_call(PS_JOINCOMMAND.split(" "))
    logging.info("successfully joined domain")
    os.remove(PRIV_KEY)
    os.remove(JOIN_DOMAIN)
except CalledProcessError:
    logging.error("failed to join from domain")
    os.remove(JOIN_DOMAIN)
    #os.remove(PRIV_KEY)
    sys.exit(1)
PS_REBOOT = "powershell.exe -noprofile -executionpolicy bypass -command restart-computer -force"
try:
    check_call(PS_REBOOT.split(" "))
except CalledProcessError:
    sys.exit(1)
