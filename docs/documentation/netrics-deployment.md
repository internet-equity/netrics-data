# Deployment

Starting in October 2021, the Internet Equity research team began shipping Netrics devices to residential locations around the City of Chicago to residents who had enrolled in a study to measure the Internet connection in their residence. The data that users can find in this repository is collected by these deployed study devices. In this document, we describe how the measurement devices work, the type of information they collect, and historical deployments of devices around Chicago since October 2021.

## Netrics Internet Measurement Device

Netrics devices are [Raspberry Pi 4](https://www.raspberrypi.com/products/raspberry-pi-4-model-b/specifications/) (4 or 8 GB) single-board computers packaged in a kit that includes a power cord, power switch, and Ethernet cable. To activate a Netrics device, the research team flashes the Netrics base image on to a microSD card, which is inserted into the Raspberry Pi. Software packages, including [Netrics measurement software](https://github.com/chicago-cdac/nm-exp-active-netrics) and Netrics data collection software, are then installed on the device, which is then packaged and shipped to the residence in which it will be installed.

<h3 align='center'>Netrics Device Setup</h3>
<p align='center'>
    <img src='https://github.com/chicago-cdac/nm-exp-active-netrics/raw/main/docs/images/attached3.png' width='500' height='300' alt='Diagram of a Netrics device installed at an Internet access point' vertical-align='middle'>
</p>

Once the device arrives at the residence where it will be installed, the participant connects the device to their Internet router, modem, or combination modem/router (depending on their particular setup) using the Ethernet cord and plugs the device into a power source, as shown in the diagram above. Once the device is connected to the Internet and powered on, it will automatically begin running network measurements multiple times per day. For example, ping latency tests are scheduled to run every 5 minutes to multiple destinations on the Internet, including facebook.com and google.com. Speed tests (Ookla, ndt7, and iPerf3) are scheduled to run once per hour. Device status and state is regularly monitored and updated using [Salt Stack](https://saltproject.io/), a fleet management system. That system also generates alerts when devices go offline to prompt action to have the offline device reconnected as soon as possible.

Participants keep the devices installed for any where between one month and seven months, and possibly longer. When the participant decides to exit the study, the device is returned to the research team and repurposed for future deployments.

## Netrics Deployments To Date

As of September 2022, the research team has conducted five deployments of Netrics devices in Chicago since October 2021, totaling over 100 devices deployed across 31 community areas. The map below shows which community areas in Chicago we have deployed devices and the total number of devices deployed since October 2021. Not all the devices that were deployed since October 2021 are still active. As of September 2022, we have approximately 60 devices active across Chicago. Neighborhoods with the greatest coverage of devices include South Shore, Logan Square, and Lake View.

<p align='center'>
    <!-- <h3>Netrics Device Deployments by Community Area - May 2022</h3> -->
    <img src='../assets/images/device_map_22JULY22.png' width='600' height='500'>
</p>

A major focus of this initiative's research is to evaluate whether Internet performance differs across neighborhoods and, if so, in what ways. The research team aims to compare the state of the Internet in historically marginalized communities to that of wealthier, more affluent communities. To compare the online experiences of residents across such neighborhoods, sufficient sampling of the Internet infrastructure within each neighborhood is needed. For that reason, recruitment for the study has focused on obtaining a sufficient number of participants (approximately 25) in three target neighborhoods as well as a baseline sample of Internet performance across Chicago. The three specific neighborhoods of focus include South Shore, Englewood, and Logan Square. The team has made significant progress with deployments in South Shore and Logan Square and continues to build relationships with community organizations in Englewood to increase participation in that area. The research team has also obtain a sufficient baseline sample of Chicago as a whole. We plan to continue deploying devices in Chicago and beyond in the coming year.