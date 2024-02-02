"""
Gets current pollen news from an API of Deutscher Wetterdienst (DWD)
It formats the result in html and sends it by mail formats and sends out results by email
email sender-address, sender-password and recipient must be provided as environment variables
  *  PollenEmailSender
  *  PollenEmailSenderPassword
  *  PollenEmailRecipient

The program was created as proof-of-concept and is not optimized.
2024, M.Renken
"""
# pylint: disable=C0103

import datetime as dt
import os
import smtplib
import ssl
import sys
from email.message import EmailMessage

import requests

print("Start reading pollen info from DWD")
# set to true if emails shall be sent out
SEND_EMAIL = True

DWD_URL = 'https://opendata.dwd.de/climate_environment/health/alerts/s31fg.json'
day_matching = {"dayafter_to": "gestern", "today": "heute", "tomorrow": "morgen"}

color_assignment = {
    "0": "<div class='kreis gruen'></div>",
    "0-1": "<div class='kreis gruengruengelb'></div>",
    "1": "<div class='kreis gruengelb'></div>",
    "1-2": "<div class='kreis gelb'></div>",
    "2": "<div class='kreis gelbgelbrot'></div>",
    "2-3": "<div class='kreis gelbrot'></div>",
    "3": "<div class='kreis rot'></div>",
}
# try to read email info from environment
try:
    email_sender = os.environ["PollenEmailSender"]
    email_password = os.environ["PollenEmailSenderPassword"]
    email_receipient = os.environ["PollenEmailRecipient"]
except KeyError as error_message:
    print(
        "Configuration environment variables not found. Please set "
        "environment variables \n- PollenEmailSender \n"
        "- PollenEmailSenderPassword \n- PollenEmailRecipient")
    print("\n Missing: ", error_message)
    sys.exit(1)

# read pollen info from DWD page
response = requests.get(url=DWD_URL)
response.raise_for_status()
data = response.json()

# transform update date to local version
last_updated = data["last_update"]
read_time = dt.datetime.strptime(last_updated, "%Y-%m-%d %H:%M Uhr")
local_time_updated = str(read_time.strftime("%d.%m.%Y, %H.%M"))

# get descriptions
legend = data["legend"]

# start html output message
msg_text = """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <font face="arial,helvetica">
    <title>Pollenflugvorhersage</title>
  <style>
    .kreis {
      width: 10px;
      height: 10px;
      border-radius: 50%;
      margin: 1px;
    }

    .gruen {
      background-color: green;
    }
    
    .gruengruengelb {
      background-color: yellowgreen;
    }    

    .gruengelb {
      background-color: Gold;
    }    

    .gelb {
      background-color: yellow;
    }

    .gelbgelbrot {
      background-color: Orange;
    }

    .gelbrot {
      background-color: OrangeRed;
    }


    .rot {
      background-color: red;
    }
  </style>

</head>
<body>"""
msg_text += f"<p>Pollenflugvorhersage vom {local_time_updated}Uhr</p>"

msg_text += """
    <table>
        <tr>
            <td></td>
            <td width=60 align=center>Gestern</td>
            <td width=60 align=center>Heute</td>
            <td width=60 align=center>Morgen</td>
        </tr>
"""


def load_description(desc):
    """
    get human readible decription of a pollen load id
    :param desc: numer version of read load
    :return: human readible version of load
    """
    for id_value, id_description in legend.items():
        if id_description == desc:
            return legend.get(id_value + "_desc")
        else:
            return "N/A"


print("Creating html output")
message_text = ""
# read out values for a specific region and add lines to html output
for region in data["content"]:
    if (region["region_id"] == 30) and (region["partregion_id"] == 32):
        all_pollen = region["Pollen"]
        output_line = ""
        for pollen, loads in all_pollen.items():
            sort_days = sorted(loads)
            message_text += pollen + ": "
            output_line = f"        <tr><td>{pollen}</td> "
            for day in sort_days:
                output_line += f"<td align=center>{color_assignment.get(loads[day])}</td>"
                message_text += day_matching[day] + ": " + str(loads[day]) + '/3 '
            message_text += "\n"
            output_line += "</tr>\n"
            msg_text += output_line

# finalize html output
msg_text += """
    </table> 
    <p> <font size=-2>Erzeugt aus DWD Daten von Matthias</font></p>
  </body>
</html>
"""

# send an email
print("Sending email")
if SEND_EMAIL:
    msg = EmailMessage()
    msg.add_header('Content-Type', 'text/html')
    msg.set_content(msg_text, subtype="html")

    msg['Subject'] = "Pollenreport vom " + local_time_updated
    msg['From'] = "Matthias Pollen Report"
    msg['To'] = email_receipient
    context = ssl.create_default_context()
    with smtplib.SMTP("smtp.gmail.com") as connection:
        connection.starttls(context=context)
        connection.login(user=email_sender, password=email_password)
        connection.send_message(msg)

print("Finished")
