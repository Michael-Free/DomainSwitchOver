# DomainSwitchOver
This is a small framework for switching over between 2 different Active Directory domains without having to manually go to each computer in remote locations to perform the switch over task.

## Requirements
- Remote access to each computer in the Domain (outside of the domain controller itself)
- Local Admin account credentials
- A little bit of pre-planning.

## Step 1 - Prepping the Configuration
In the `SwitchDomains` directory, edit the `config.ini` file with the old DC and new DC's credentials and save it. Copy the `SwitchDomains` directory to `c:\`.

## Step 2 - Encryption
Run the `CreateKeysEncrypt.exe` file.  This will create a SHA256 key pair found in `private_key.pem` and `public_key.pem`.  It will also encrypt `config.ini` in a new file called `config.encrypted`.

