# Netrics Data - Continuous Measurements of Internet Performance at the Access Network

<p align='center'><img src='assets/images/netrics-data-hero.jpg' width='750' height='400' alt='Image of a map with data displayed on it and a heat map of Netrics device deployments with some charts of netrics data displayed on a Grafana dashboard and accompanying text that says Internet Equity Initiative data about and analysis of Internet performance and reliability with actionable insights to address inequity in communities across the United States.' vertical-align='middle'></p>

This repository contains documentation about and links to datasets collected by Netrics Internet measurement devices which the [Internet Equity Initiative](https://internetequity.uchicago.edu/) research team at the [Data Science Institute](http://datascience.uchicago.edu/) deployed across Chicago starting in late 2021. Supporting resources to assist those that want to use the data are also available.

This repository is organized as follows:
- **[documentation](documentation)**: Find documentation about the data, the deployment of Netrics devices, and the pipeline that moves data from devices to a central data store.
- **[example-notebooks](example-notebooks)**: Find Jupyter notebooks with example code for working with the Netrics data and notebooks containing the analysis underlying some of the data stories on the portal.
- **[data](data)**: Find datasets used in some of the data stories featured on the portal.
- **[src](src)**: Find scripts used to pull data from InfluxDB.

## Download the Data

<!--
### [*Version 1.0*](https://github.com/chicago-cdac/netrics-data/releases/tag/netrics-data-1-0) (May 9, 2022)
### [*Version 1.1*](https://github.com/chicago-cdac/netrics-data/releases/tag/netrics-data-1-1) (July 22, 2022)
### [*Version 1.2*](https://github.com/chicago-cdac/netrics-data/releases/tag/netrics-data-1-2) (August 29, 2022)
### [*Version 1.3*](https://github.com/chicago-cdac/netrics-data/releases/tag/netrics-data-1-3) (October 3, 2022)
-->

#### Chicago

| Quarter | Speedtest | Latency | Counters |
| ---     | ---       | ---     | ---      |
| 2021Q4  | [csv.tgz](https://abbott.cs.uchicago.edu:8081/chicago/netrics_speedtest_2021Q4.tgz) | [csv.tgz](https://abbott.cs.uchicago.edu:8081/chicago/netrics_latency_2021Q4.tgz) | [csv.tgz](https://abbott.cs.uchicago.edu:8081/chicago/netrics_counter_2021Q4.tgz) |
| 2022Q1  | [csv.tgz](https://abbott.cs.uchicago.edu:8081/chicago/netrics_speedtest_2022Q1.tgz) | [csv.tgz](https://abbott.cs.uchicago.edu:8081/chicago/netrics_latency_2022Q1.tgz) | [csv.tgz](https://abbott.cs.uchicago.edu:8081/chicago/netrics_counter_2022Q1.tgz) |
| 2022Q2  | [csv.tgz](https://abbott.cs.uchicago.edu:8081/chicago/netrics_speedtest_2022Q2.tgz) | [csv.tgz](https://abbott.cs.uchicago.edu:8081/chicago/netrics_latency_2022Q2.tgz) | [csv.tgz](https://abbott.cs.uchicago.edu:8081/chicago/netrics_counter_2022Q2.tgz) |
| 2022Q3  | [csv.tgz](https://abbott.cs.uchicago.edu:8081/chicago/netrics_speedtest_2022Q3.tgz) | [csv.tgz](https://abbott.cs.uchicago.edu:8081/chicago/netrics_latency_2022Q3.tgz) | [csv.tgz](https://abbott.cs.uchicago.edu:8081/chicago/netrics_counter_2022Q3.tgz) |
| 2022Q4  | [csv.tgz](https://abbott.cs.uchicago.edu:8081/chicago/netrics_speedtest_2022Q4.tgz) | [csv.tgz](https://abbott.cs.uchicago.edu:8081/chicago/netrics_latency_2022Q4.tgz) | [csv.tgz](https://abbott.cs.uchicago.edu:8081/chicago/netrics_counter_2022Q4.tgz) | 
| 2023Q1  | [csv.tgz](https://abbott.cs.uchicago.edu:8081/chicago/netrics_speedtest_2023Q1.tgz) | [csv.tgz](https://abbott.cs.uchicago.edu:8081/chicago/netrics_latency_2023Q1.tgz) | [csv.tgz](https://abbott.cs.uchicago.edu:8081/chicago/netrics_counter_2023Q1.tgz) |

Get all files with this [script](https://abbott.cs.uchicago.edu:8081/chicago/wgetall.sh).

## Additional Links

- Visit our [portal](https://internetequity.uchicago.edu/) for the initiative
- View the open-source code for the Netrics [software](https://github.com/chicago-cdac/nm-exp-active-netrics)

Please [create an issue](https://github.com/chicago-cdac/netrics-data/issues) if you want to flag errors in the data or make suggestions on how to improve the data for the research team.

For questions about the above, contact us at [broadband-equity@lists.uchicago.edu](mailto:broadband-equity@lists.uchicago.edu).

## License

<a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-sa/4.0/88x31.png" /></a><br /><span xmlns:dct="http://purl.org/dc/terms/" property="dct:title">Netrics Data</span> by <a xmlns:cc="http://creativecommons.org/ns#" href="https://internetequity.uchicago.edu/" property="cc:attributionName" rel="cc:attributionURL">Internet Equity Initiative</a> is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/">Creative Commons Attribution-ShareAlike 4.0 International License</a>.
