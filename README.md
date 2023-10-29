# Sojourner Scanning Node

## About
This is the repository for the Sojourner web scanner.  Currently a private project for doing information gathering.

## Installation

Create a new user called 'sojourner' for the node to run as.  Generally:
```
sudo useradd sojourner
sudo mkdir /home/sojourner
sudo chown sojourner:sojourner /home/sojourner
```

Change to that user using:
```
sudo su sojourner
```

Clone the repository into the home directory:
```
cd ~
git clone https://github.com/briffy/sojourner
```
**Please note**:  the following two steps will need to be carried out every 30 days to re-authenticate your account for the time being.

Login to your node account on Sojourner and copy your API key by clicking on the key icon next to the logout icon.

Paste the provided text into a file stored in **/home/sojourner/sojourner/cookie**


Set it to run as a service (systemd):
```
sudo cp ~/sojourner/systemd/sojourner.service /etc/systemd/system
sudo systemctl daemon-reload
sudo systemctl enable sojourner
sudo systemctl start sojourner
```

If you get a permissions related error when trying to start the service then make sure it is owned by root and permissions are set correctly:

```
sudo chown root:root /etc/systemd/system/sojourner.service
sudo chmod 755 /etc/systemd/system/sojourner.service
```

You can keep an eye on the logs with:
```
sudo journalctl -f -u sojourner
```