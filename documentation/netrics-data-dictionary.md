# Netrics Data Documentation & Data Dictionary

The measurement data that we collect from Netrics Internet measurement devices deployed across Chicago are currently available as a set of comma-separated values (CSV) files, broken out by month and measurement. We also include a dataset that contains geographic (community areas and tracts) and selected survey data (i.e., ISP and speed tier)) for each device.

Download the data (measurements and geographic-survey data) by going to our [releases](https://github.com/chicago-cdac/netrics-data/releases/tag/netrics-data-1-0) for this repository. Keep an eye on the releases for updates of the data. We plan to release new data monthly.

## Measurement Data

Each CSV contains one month of data for all deployed devices for one of the following measurements:

1. **Device Count** (`device_count.csv`): The number of active devices on the network using Address Resolution Protocol (ARP). ARP allows us to map IP addresses to physical MAC addresses on a local network. In simple terms, this measurement allows us to ask the router within a residence how many devices it has had connect to it in recent history. Consequently, we can see for each network how many devices are actively connected to the Internet and use that number as a rough proxy of Internet usage at any given time within a household.

2. **DNS Latency** (`dns_latency.csv`): The latency to resolve Domain Name Service (DNS) queries to a set of popular websites using Cloudflare's public DNS resolver, `8.8.8.8`. When you visit a website on the Internet (for example, www.google.com), the *domain name*, "www.google.com", needs to be matched to an actual IP address before the network can know where to send your information over the Internet. You can think of a website's IP address as its mailing address, similar to the address of your house or apartment. The domain name "www.google.com" is a nice, human-readable moniker for the actual IP address where Google's servers are located. It takes time to look up and "resolve" a web domain name, which is what DNS latency measures—the amount of time in milliseconds that it takes to resolve a domain name into an IP address.

3. **Hops to Google** (`hops_to_google.csv`): The number of hops to Google using the standard traceroute utility. On the Internet, information travels across multiple networks, sometimes having to traverse numerous "nodes" across the network before reaching its intended final destination. In this measurement, we are collecting data about how many nodes information has to traverse, often referred to as "hops", before it reaches the intended final destination of www.google.com.

4. **LAN Bandwidth** (`lan_bw.csv`): The local network area (LAN) bandwidth in megabits per second (Mbps). We measure LAN bandwidth by conducting a speed test (Measurement Lab's NDT7 test) between a participant's device (laptop) and the Netrics device installed in their residence. This measurement allows us the test the capacity (or performance) of a household's WiFi network, which can then be compared to the capacity of the same household's wired Internet connection to determine whether WiFi serves as a performance bottleneck. This kind of measurement can also be useful for understanding WiFi coverage throughout your home.

5. **Latency Under Load** (`lul.csv`): The average latency under load using both TCP and ICMP pings. Standard network latency is a measure of how long it takes (typically in milliseconds) to send information to a destination on the network and receive a response in return. Latency under load (or working latency) is another way to measure the same concept, but under network conditions that more accurately reflect the context in which you use the Internet. Typically, the average person does not use the Internet within a vacuum, which is the context in which latency is most commonly measured. Rather, there are usually multiple applications, devices, etc. generating network traffic and competing for available network bandwidth at any given moment you spend online. Latency under load measures latency under those kinds of network conditions, thus supplying a more realistic measure of latency than is given by traditional latency measures.

6. **Ping Latency** (`ping_latency.csv`): The latency to a set of popular websites and geographically distributed servers. (See the description of latency in *Latency Under Load* in #5 above.) The ping latency is a standard measurement of latency. We collect ping latency data for:

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

7. **Speed Tests** (`speedtest.csv`): A household's wired Internet upload and download bandwidth in megabits per second (Mbps). Internet bandwidth is a measure of how fast your Internet connection is. The more bandwidth that your Internet connection has, the more information it can handle at any given time and the faster it can send that information. We measure Internet bandwidth using three popular tools—Ookla, NDT7, and iPerf3.

## Measurement Data Dictionary

In this section we describe each field of each CSV (measurement). **Note on time zones** All times in each file are in US/Central time.

### [Device Count](#data-documentation):

1. `Time`: The date and time at which the test was taken.
2. `No. of Devices`: The number of devices actively connected to a household's local network.
3. `Measurement`: The measurement identifier.
4. `ID`: The access network/participant's unique ID.

### [DNS Latency](#data-documentation):

1. `Time`: The date and time at which the test was taken. 
2. `RTT`: The aggregated query time in milliseconds.
3. `Measurement`: The measurement identifier.
4. `ID`: The access network/participant's unique ID.
5. `Type`: The aggregation method (either max or average).

### [Hops to Google](#data-documentation):

1. `Time`: The date and time at which the test was taken. 
2. `Hops`: The number of hops to Google.
3. `Measurement`: The measurement identifier.
4. `ID`: The access network/participant's unique ID.

### [LAN Bandwidth](#data-documentation):

1. `Time`: The date and time at which the test was taken.
2. `Speed`: The bandwidth in Mbps.
3. `Origin`: Whether the measurement was collected by the server or the client of the test.
4. `Measurement`: The measurement identifier.
5. `ID`: The access network/participant's unique ID.

### [Latency Under Load](#data-documentation):

1. `Time`: The date and time at which the test was taken.
2. `RTT`: The average round-trip time to the destination in milliseconds.
3. `Measurement`: The measurement identifier.
4. `ID`: The access network/participant's unique ID.
5. `Protocol`: The ping protocol used (ICMP or TCP).
6. `Direction`: The direction (uplink or downlink) that was saturated for the test.
7. `Destination`: The destination pinged in the test.

### [Ping Latency](#data-documentation):

1. `Time`: The date and time at which the test was taken.
2. `RTT`: The latency in milliseconds to the destination.
3. `Destination`: The ping destination. (Need to be more specific for cities). 
4. `Method`: Aggregation method of pings (either average or minimum).
5. `Measurement`: The measurement identifier.
6. `ID`: The access network/participant's unique ID.

### [Speed Tests](#data-documentation):

1. `Time`: The date and time at which the test was taken.
2. `Direction`: The direction (upload/download) of the test.
3. `Tool`: The tool used to measure available bandwidth.
4. `Speed`: The bandwidth in Mbps.
5. `ID`: The access network/participant's unique ID.

## Geograhpic and Survey Data

The geographic and survey data contains one row for each `device_id`. Note that not all devices that appear in the measurement data have a corresponding row in this dataset. Not all of our devices have associated geographic information and/or survey responses.

We generate the geographic data for this dataset by using the Google Maps API to geocode address data that we collect from our study participants. The accuracy of this geocoding has not been verified. We then do a spatial join to the [Chicago community area boundaries](https://data.cityofchicago.org/Facilities-Geographic-Boundaries/Boundaries-Community-Areas-current-/cauq-8yn6) available and a spatial join to the [2010 US Census tracts](https://data.cityofchicago.org/Facilities-Geographic-Boundaries/Boundaries-Census-Tracts-2010/5jrd-6zik) from the Chicago Open Data Portal.

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