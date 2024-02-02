# pollen_alert

This is a proof-of-concept program to send pollen load of one region by email.
The load values are read from an open available API from Deutscher Wetterdienst (DWD) at

https://opendata.dwd.de/climate_environment/health/alerts/s31fg.json

The values are converted into a html file and load values are depicted by colored circles
from green (no load) to red (maximum load).

The html-file is sent out by email where the usernames and passwords are read from
system environment.
To do so, these environments variables have to be set:

* PollenEmailSender
* PollenEmailSenderPassword
* PollenEmailRecipient
