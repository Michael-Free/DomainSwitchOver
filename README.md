# DomainSwitchOver
This is a small framework for switching over between 2 different Active Directory domains without having to manually go to each computer in remote locations to perform the switch over task.

## Requirements
- Remote access to each computer in the Domain (outside of the domain controller itself)
- Local Admin account credentials
- A little bit of pre-planning.

## Step 1
In the `SwitchDomains` directory, edit the `config.ini` file with the old DC and new DC's credentials and save it.

## Step 2
