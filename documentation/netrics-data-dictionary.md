# Netrics Data Documentation & Data Dictionary

The measurement data that we collect from Netrics Internet measurement devices deployed across Chicago are currently available as a set of comma-separated values (CSV) files, broken out by month and measurement. We also include a dataset that contains geographic (community areas and tracts) and selected survey data (i.e., ISP and speed tier)) for each device.

Download the data (measurements and geographic and survey data) by going to our [releases](https://github.com/chicago-cdac/netrics-data/releases/tag/netrics-data-1-3) for this repository. Keep an eye on the releases for updates of the data. We plan to release new data monthly.

## Measurement Data

The measurement data is divided into 3 types of CSV files:

* Latency
* Speedtest
* Counters

#### Latency

The Latency measuments is structured as follows:

| time | deviceid | tool | direction | protocol | target | pktloss | method | zip | isp | value | topic | anonipaddr | ipaddrchanged |
| ---  | ---      | ---  | ---       | ---      | ---    | ---     | ---    | --- | --- | ---   | ---   | ---        | ---           |

The available tools for latency are:

| Tool | Description | Expected Frequency |
| ---  | --- | --- |
| [ping_latency](https://github.com/iputils/iputils) | This is an ICMP roundtrip time (RTT) measurement taken with a standard "ping" tool targeting multiple sites | Every 5 minutes |
| [dns_latency](https://github.com/iputils/iputils)  | This is an ICMP roundtrip time (RTT) measurement taken with a standard "ping" tool targeting common DNS sites (8.8.8.8, 1.1.1.1) | Every 5 minutes |
| [oplat](https://github.com/kyle-macmillan/OpLat)  | This is a tool designed to measure Latency-Under-Load (LUL) and it combines RTT "ping" with the network traffic load created by iperf | Along with Speedtest (1 to 5 times a day) |

#### Speedtest

The Speedtest measuments is structured as follows:

| time | deviceid | tool | direction | protocol | target | pktloss | retrans | zip | isp | value | topic | anonipaddr | ipaddrchanged |
| ---  | ---      | ---  | ---       | ---      | ---    | ---     | ---     | --- | --- | ---   | ---   | ---        | ---           |

The available tools for speedtest are:

| Tool | Description | Expected Frequency |
| ---  | --- | --- |
| [ndt7](https://www.measurementlab.net/tests/ndt/ndt7/) | Network Diagnostic Tool developed by MLab | 1 to 5 times a day |
| [ookla](https://www.speedtest.net/apps/cli)  | Ookla's Speedtest | 1 to 5 times a day |
| [iperf3](https://iperf.fr/iperf-download.php)  | The standard iperf3 tool | 1 to 5 times a day |
| [local_dash_client](https://github.com/chicago-cdac/netrics-dash) | Netrics Local Dashboard (Ndt7 client reading) | Eventually |
| [local_dash_server](https://github.com/chicago-cdac/netrics-dash) | Netrics Local Dashboard (Ndt7 server reading) | Eventually |

#### Counters

The Coutner measuments is structured as follows:

| time | deviceid | tool | method | target | zip | isp | value | topic | anonipaddr | ipaddrchanged |
| ---  | ---      | ---  | ---    | ---    | --- | --- | ---   | ---   | ---        | ---           | 

The available tools for counters are:

| Tool | Description | Expected Frequency |
| ---  | --- | --- |
| [hops_to_target](https://github.com/openbsd/src/blob/master/usr.sbin/traceroute/traceroute.c) | The number of network hops necessary to reach a network targeted  | Every 5 minutes |
| [connected_devices_arp](https://github.com/nmap/nmap)  | The number of connected devices connected to the network | Every 5 minutes |
| [score](https://github.com/chicago-cdac/netrics-dash)  | Subjective opinion score (*)| Eventually |

(*) 0 = Good, 1 = Slow, 2 = Unusable

<!--Each CSV contains one month of data for all deployed devices for one of the following measurements: -->

1. **Device Count** (`netrics_counter_20YYMMDD.csv, tool=="connected_devices_arp"`): The number of active devices on the network using Address Resolution Protocol (ARP). ARP allows us to map IP addresses to physical MAC addresses on a local network. In simple terms, this measurement allows us to ask the router within a residence how many devices it has had connect to it in recent history. Consequently, we can see for each network how many devices are actively connected to the Internet and use that number as a rough proxy of Internet usage at any given time within a household.

2. **DNS Latency** (`netrics_latency_20YYMMDD.csv, tool=="dns_latency"`): The latency to resolve Domain Name Service (DNS) queries to a set of popular websites using Cloudflare's public DNS resolver, `8.8.8.8`. When you visit a website on the Internet (for example, www.google.com), the *domain name*, "www.google.com", needs to be matched to an actual IP address before the network can know where to send your information over the Internet. You can think of a website's IP address as its mailing address, similar to the address of your house or apartment. The domain name "www.google.com" is a nice, human-readable moniker for the actual IP address where Google's servers are located. It takes time to look up and "resolve" a web domain name, which is what DNS latency measures—the amount of time in milliseconds that it takes to resolve a domain name into an IP address.

3. **Hops to Google** (`netrics_counter_20YYMMDD.csv, tool=="hops_to_target"`): The number of hops to Google using the standard traceroute utility. On the Internet, information travels across multiple networks, sometimes having to traverse numerous "nodes" across the network before reaching its intended final destination. In this measurement, we are collecting data about how many nodes information has to traverse, often referred to as "hops", before it reaches the intended final destination of www.google.com.

4. **LAN Bandwidth** (`netrics_speedtest_20YYMMDD.csv, tool=="local_dash_client", tool=="local_dash_server"`): The local network area (LAN) bandwidth in megabits per second (Mbps). We measure LAN bandwidth by conducting a speed test (Measurement Lab's NDT7 test) between a participant's device (laptop) and the Netrics device installed in their residence. This measurement allows us the test the capacity (or performance) of a household's WiFi network, which can then be compared to the capacity of the same household's wired Internet connection to determine whether WiFi serves as a performance bottleneck. This kind of measurement can also be useful for understanding WiFi coverage throughout your home.

5. **Latency Under Load** (`netrics_latency_20YYMMDD.csv, tool=="oplat"`): The average latency under load using both TCP and ICMP pings. Standard network latency is a measure of how long it takes (typically in milliseconds) to send information to a destination on the network and receive a response in return. Latency under load (or working latency) is another way to measure the same concept, but under network conditions that more accurately reflect the context in which you use the Internet. Typically, the average person does not use the Internet within a vacuum, which is the context in which latency is most commonly measured. Rather, there are usually multiple applications, devices, etc. generating network traffic and competing for available network bandwidth at any given moment you spend online. Latency under load measures latency under those kinds of network conditions, thus supplying a more realistic measure of latency than is given by traditional latency measures.

6. **Ping Latency** (`netrics_counter_20YYMMDD.csv, tool=="ping_lantency"`): The latency to a set of popular websites and geographically distributed servers. (See the description of latency in *Latency Under Load* in #5 above.) The ping latency is a standard measurement of latency. We collect ping latency data for:

   - www.google.com
   - www.amazon.com
   - www.youtube.com
   - www.facebook.com
   - www.wikipedia.com
   - www.chicagotribune.com
   - www.suntimes.com
   - Other servers
      - University of Chicago
      - last mile
      - Measurement Lab test servers in Washington, DC, Atlanta, and Denver

7. **Speed Tests** (`netrics_speedtest_20YYMMDD.csv, tool=="ookla", tool=="ndt7", tool=="iperf3"`): A household's wired Internet upload and download bandwidth in megabits per second (Mbps). Internet bandwidth is a measure of how fast your Internet connection is. The more bandwidth that your Internet connection has, the more information it can handle at any given time and the faster it can send that information. We measure Internet bandwidth using three popular tools—Ookla, NDT7, and iPerf3.

## Measurement Data Dictionary

In this section we describe each field of each CSV (measurement). **Note on time zones** All times in each file are in UTC standard format.


### [Latency (netrics_latency_20YYMMDD.csv)](#measurement-data):

1. `time`: The date and time at which the test was taken.
2. `deviceid`: The access network/participant's unique ID.
3. `tool`: Options are `ping_latency`, `oplat`, `dns_latency`.
4. `direction`: Options are `download`, `upload` and `rtt` (Round-Trip).
5. `protocol`: Options are `icmp`, `tcp` and `udp`. 
6. `target`: Options include 1.1.1.1, 8.8.8.8, www.google.com, www.facebook.com and cities like Atlanta, São Paulo, etc.
7. `pktloss`: % rate of packet loss, available for `ping_latency`.
8. `method`: Options are `avg`, `min`, `max` and `mdev`
9. `zip`: Zipcode of the measurement, mostly in Chicago area.
10. `isp`: Internet Service Provider, includes `xfinity`, `att`, `rcn`, `everywherewireless`
11. `value`: Measurement result in milliseconds
12. `topic`: Topic refers to the deployment. Options include `chicago` (chicago city), `schools` (Chicago Public Schools, aka CPS), etc.
13. `anonipaddr`: Anonymized IP address (eg. 1.2.3.4 -> 1.2.3.0).
14. `ipaddrchanged`: Boolean flag 1:true 0:false indicating whether the IP changed since the last measurement.


### [Speedtest (netrics_speedtest_20YYMMDD.csv)](#measurement-data):

1. `time`: The date and time at which the test was taken.
2. `deviceid`: The access network/participant's unique ID.
3. `tool`: Options are `ookla`, `ndt7`, `iperf3`, `local_dash_client` and `local_dash_server`.
4. `direction`: Options are `download` or `upload`.
5. `protocol`: Options `tcp` or `udp`. 
6. `target`: Options include Ookla servers, ndt7 servers, `netrics.local` and `abbott.cs.uchicago.edu`.
7. `pktloss`: % rate of packet loss, available for `ookla`.
8. `retrans`: % rate of TCP packet retransmission, avaiable for `ndt7`.
9. `zip`: Zipcode of the measurement, mostly in Chicago area.
10. `isp`: Internet Service Provider, includes `xfinity`, `att`, `rcn`, `everywherewireless`, etc.
11. `value`: Measurement result in milliseconds
12. `topic`: Topic refers to the deployment. Options include `chicago` (chicago city), `schools` (Chicago Public Schools, aka CPS), etc.
13. `anonipaddr`: Anonymized IP address (eg. 1.2.3.4 -> 1.2.3.0).
14. `ipaddrchanged`: Boolean flag 1:true 0:false indicating whether the IP changed since the last measurement.


### [Counters (netrics_counter_20YYMMDD.csv)](#measurement-data):


1. `time`: The date and time at which the test was taken.
2. `deviceid`: The access network/participant's unique ID.
3. `tool`: Options are `connected_devices_arp`, `hops_to_target` and `score`.
4. `method`: Options are `tr` (hops_to_target), `1day`, `1week`, `active`, `total` (connected_devices_arp) and `subjective` for `score`.
6. `target`: Options include `google` for `hops_to_target` only.
9. `zip`: Zipcode of the measurement, mostly in Chicago area.
10. `isp`: Internet Service Provider, includes `xfinity`, `att`, `rcn`, `everywherewireless`, etc.
11. `value`: Measurement result in milliseconds
12. `topic`: Topic refers to the deployment. Options include `chicago` (chicago city), `schools` (Chicago Public Schools, aka CPS), etc.
13. `anonipaddr`: Anonymized IP address (eg. 1.2.3.4 -> 1.2.3.0).
14. `ipaddrchanged`: Boolean flag 1:true 0:false indicating whether the IP changed since the last measurement.

## Geograhpic and Survey Data

The geographic and survey data contains one row for each `device_id`. Note that not all devices that appear in the measurement data have a corresponding row in this dataset. Not all of our devices have associated geographic information and/or survey responses.

We generate the geographic data for this dataset by using the Google Maps API to geocode address data that we collect from our study participants. The accuracy of this geocoding has not been verified. We then do a spatial join to the [Chicago community area boundaries](https://data.cityofchicago.org/Facilities-Geographic-Boundaries/Boundaries-Community-Areas-current-/cauq-8yn6) available from the Chicago Open Data Portal.

**WARNING** The data included in this dataset are collected through a survey that the research team administers through the study. Not all participants who enroll in the study and receive a device complete the survey. Devices may contain missing values for some of the survey fields.

## Geographic and Survey Data Dictionary

### `device_id`

The access network/participant's unique ID.

### `ISP`

The reported ISP that services the access network where the device was installed.

### `reported_speed_tier`

The reported speed tier for the access network where the device was installed. (**Note**: This reported speed tier might not accurately represent the true provisioned speed for the access network.)

### `access_technology`

The reported hardware that is used to access the Internet. Currently, we do not have more granular information beyond whether the subscriber uses a separate modem and router, only a router, or a combination router/modem.

### `has_wifi_extenders`

Whether the subscriber reported using WiFi extenders. A WiFi extender is used to amplify the WiFi signal coming from the access network's WiFi router to extend the range of the WiFi network.

### `num_wifi_extenders`

The number of extenders that the subscriber uses. This field is null if the subscriber did not report using any WiFi extenders.

### `internet_cost`

The per-month cost that the subscriber reported paying for their Internet service.

### `community`

The community area where the device was deployed.