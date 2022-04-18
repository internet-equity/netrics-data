# Portal Data Docs
Netrics data is currently available as a set of CSVs. Each CSV contains one
month of data for one of the following measurements:
1. **Device Count**: We measure the number of active devices on the network
   using ARP. 

2. **DNS Latency**: We measure the latency to resolve DNS queries to a set of
   popular website's using Cloudflare's public DNS resolver, `8.8.8.8`.

3. **Hops to Google**: We measure the number of hops to Google using the
   standard traceroute utility.

4. **LAN Bandwidth**: We measure the available bandwidth between a participant's
   device (laptop) and the netrics device.

5. **Latency Under Load**: We measure the average latency under load using both
   TCP and ICMP pings.

6. **Ping Latency**: We measure the latency to a set of popular websites and
   geographically distributed desinations.

7. **Speed Tests**: We measure the available bandwidth using several popular
   tools, including Ookla, NDT, and iPerf3.

## Measurement Datasheet
In this section we describe each field of each CSV (measurement).

### Device Count:
1. `Time`: The date and time at which the test was taken.
2. `n_devs`: The number of active devices.
3. `Measurement`: The measurement identifier.
4. `ID`: The network/participant's unique ID

### DNS Latency:
1. `Time`: The date and time at which the test was taken. 
2. `RTT`: The aggregated query time in milliseconds.
3. `Measurement`: The measurement identifier.
4. `ID`: The network/participant's unique ID
5. `Type`: The aggregation method (either max or average).

### Hops to Google
1. `Time`: The date and time at which the test was taken. 
2. `Hops`: The number of hops to Google.
3. `Measurement`: The measurement identifier.
4. `ID`: The network/participant's unique ID

### LAN Bandwidth
1. `Time`: The date and time at which the test was taken.
2. `Speed`: The bandwidth in Mbps.
3. `Origin`: The sender. (not sure if this is correct)
4. `Measurement`: The measurement identifier.
5. `ID`: The network/participant's unique ID.

### Latency Under Load
1. `Time`: The date and time at which the test was taken.
2. `RTT`: The average round-trip time to the destination in milliseconds.
3. `Measurement`: The measurement identifier.
4. `ID`: The network/participant's unique ID.
5. `Protocol`: The ping protocol used (ICMP or TCP)
6. `Direction`: The direction (uplink or downlink) that is saturated.
7. `Destination`: The destination we ping.

### Ping Latency
1. `Time`: The date and time at which the test was taken.
2. `RTT`: The latency in milliseconds to the destination.
3. `Destination`: The ping destination. (Need to be more specific for cities). 
4. `Method`: Aggregation method of pings (either average or min)
5. `Measurement`: The measurement identifier.
6. `ID`: The network/participant's unique ID.

### Speed Tests
1. `Time`: The date and time at which the tset was taken.
2. `Direction`: The direction (upload/download) of the test.
3. `Tool`: The tool used to measure available bandwidth.
4. `Speed`: The measured speed in Mbps.
5. `ID`: The network/participant's unqique ID.

