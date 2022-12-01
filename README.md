# DomainSwitchOver
This is a small framework for switching over between 2 different Active Directory domains without having to manually go to each computer in remote locations to perform the switch over task.

## Requirements
- Remote access to each computer in the Domain (outside of the domain controller itself)
- Local Admin account credentials
- A little bit of pre-planning.

## Step 1 - Prepping the Configuration
In the `SwitchDomains` directory, edit the `config.ini` file with the old DC and new DC's credentials and save it. Copy the `SwitchDomains` directory to `c:\`.

## Step 2 - Encrypting your credentials
Run the `CreateKeysEncrypt.exe` file.  This will create a SHA256 key pair found in `private_key.pem` and `public_key.pem`.  It will also encrypt `config.ini` in a new file called `config.encrypted`.

## Step 3 - Create A Folder Group Policy
`C:\SwitchDomain` will be required on all the remote computers you wish to switch over. Here is a link on how to create that: https://techexpert.tips/windows/gpo-create-folder/

Remember that the current `C:\SwitchDomain` directory on your own local computer you dont want to push out just yet.

## Step 4 - Create A File Push Group Policy
In preparation for your switch over to the new domain controller, you will want to push `config.encrypted` as well as `JoinDomain.exe` and `UnjoinDomain.exe` to all machines in your domain to `C:\Switchdomain`. Here's a tutorial on how that is done: http://woshub.com/copy-files-on-all-computers-group-policy/

