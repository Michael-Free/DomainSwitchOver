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

## Step 5 - The Big Switch
On the day of your big switch-over, create one last file push group policy with `private_key.pem` going to `C:\SwitchDomain`... preferably in off-hours. Use the link in Step 4 handle that.

Once this file has propogated out to all machines in your domain - you will want to create one last Group Policy to run a scheduled task of `UnjoinDomain.exe`.  Once it starts to run, it will immediately unjoin the domain, and set `JoinDomain.exe` to run once on the next boot and restart the computer.

`JoinDomain.exe` will run, join the domain and restart the computer again.  If it doesn't kick in - try logging into each machine as the Local Administrator and it should start executing.

## Step 6 - Ask for a raise
congrats! you've saved yourself from having to drive out to a bajillion remote locations and manually switch over each computer.  You've saved yourself a bunch of headaches.  You've also saved your organization a bunch of time and money. Thank me later.
