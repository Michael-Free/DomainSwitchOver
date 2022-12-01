""" decrypt config file and unjoin domain """
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

logging.basicConfig(filename=SCRIPT_ROOT+"\\unjoin_log.txt", encoding="utf-8", level=logging.DEBUG)
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

PS_UNJOINSCRIPT= str(
    "remove-computer -UnjoinDomainCredential "
    +"(new-object -typename System.Management.Automation.PSCredential -argumentlist \""
    +CONFIG_PARSED['credentials']['OLDUSER']+"\", (convertto-securestring -string \""
    +CONFIG_PARSED['credentials']['OLDPASS']+"\" -asplaintext -force)) -Force"
    +"\nif ($?) { exit 0 } else { exit 1 }"
    )

with open(LEAVE_DOMAIN, "w", encoding="utf-8") as ps_unjoin:
    ps_unjoin.write(PS_UNJOINSCRIPT)
    ps_unjoin.close()

CONFIG_FILE.close()

PS_UNJOINCOMMAND = "powershell.exe -noprofile -executionpolicy bypass -file "+LEAVE_DOMAIN

try:
    check_call(PS_UNJOINCOMMAND)
    logging.info("successfully left domain")
    os.remove(LEAVE_DOMAIN)
except CalledProcessError:
    logging.error("failed to unjoin from domain")
    os.remove(LEAVE_DOMAIN)
    os.remove(PRIV_KEY)
    sys.exit(1)

PS_JOINCOMMAND = r"powershell.exe -noprofile -executionpolicy bypass -command Set-ItemProperty -Path 'HKLM:\Software\Microsoft\Windows\CurrentVersion\RunOnce' -Name '!NewDomainJoin' -Value 'C:\SwitchDomain\JoinDomain.exe'"
PS_REBOOT = "powershell.exe -noprofile -executionpolicy bypass -command restart-computer -force"

try:
    check_call(PS_JOINCOMMAND.split(" "))
    check_call(PS_REBOOT.split(" "))
except CalledProcessError:
    logging.error("failed to set JoinDomain.exe to run on the next boot.")
    sys.exit(1)
