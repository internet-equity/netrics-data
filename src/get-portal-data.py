import yaml
import datetime
import pandas as pd
import numpy as np
import argparse
from influxdb_client import InfluxDBClient
import os


class Client:

    def __init__(self, config, start, stop):

        # Initialize client to query DB
        with open(config, "r") as f:
            c = yaml.safe_load(f)

        self.client = InfluxDBClient(url=f'https://wilson.cs.uchicago.edu:{c["port"]}',
                                     token=c['token'], org=c['org'])

        self.base_query = (f'from(bucket:"netrics-prod0")'
                       f'|> range(start: {start}T00:00:00Z, stop: {stop}T00:00:00Z)')


    def ookla(self):
        """ Returns ookla speedtest data between 'start' and 'stop' for all devices
            or a single device. TODO: allow to give list of devices """

        query = self.base_query + """
                    |> filter(fn: (r) => (r._field == "speedtest_ookla_download" or r._field == "speedtest_ookla_upload"))
                    |> drop(columns:["meta_extended", "meta_extended_debhash", "meta_extended_dataver", "env", "_start","_stop"])
                 """

        df = self.exec_query(query)

        df["_field"].replace({"speedtest_ookla_download": "download",
                              "speedtest_ookla_upload": "upload"}, inplace=True)

        df = df.rename(columns={"_time": "Time", "_value": "Speed",
                                "_field": "Direction", "_measurement": "Tool", 
                                "install": "ID"})

        df['Tool'] = df['Tool'].replace(['oplat'], 'iPerf3 (TCP)')
        df['Tool'] = df['Tool'].replace(['iperf'], 'iPerf3 (UDP)')

        return df

    def ndt(self):
        """ Returns ndt speedtest data between 'start' and 'stop' for all devices
            or a single device. TODO: allow to give list of devices """


        query = self.base_query + """
                    |> filter(fn: (r) => (r._field == "speedtest_ndt7_download" or r._field == "speedtest_ndt7_upload"))
                    |> drop(columns:["meta_extended", "meta_extended_debhash", "meta_extended_dataver", "env", "_start","_stop"])
                 """

        df = self.exec_query(query)

        df["_field"].replace({"speedtest_ndt7_download": "download",
                              "speedtest_ndt7_upload": "upload"}, inplace=True)

        df = df.rename(columns={"_time": "Time", "_value": "Speed",
                                "_field": "Direction", "_measurement": "Tool"})

        return df

    def iperf(self):
        """ Returns iperf speedtest data between 'start' and 'stop' for all devices
            or a single device. TODO: allow to give list of devices """

        query = self.base_query + """
                    |> filter(fn: (r) => (r._field == "iperf_udp_download" or r._field == "iperf_udp_upload"))
                    |> drop(columns:["meta_extended", "meta_extended_debhash", "meta_extended_dataver", "env", "_start","_stop"])
                 """

        df = self.exec_query(query)
        df["_field"].replace({"iperf_udp_download": "download",
                              "iperf_udp_upload": "upload"}, inplace=True)

        df = df.rename(columns={"_time": "Time", "_value": "Speed",
                                "_field": "Direction", "_measurement": "Tool"})

        return df


    def speedtest(self):
        """ Returns all speedtest data between 'start' and 'stop' for all devices
            or a single device. TODO: allow to give list of devices """

        query = self.base_query + """
                    |> filter(fn: (r) => (r._field == "iperf_udp_download" or r._field == "iperf_udp_upload" or
                                          r._field == "speedtest_ndt7_download" or r._field == "speedtest_ndt7_upload" or
                                          r._field == "speedtest_ookla_download" or r._field == "speedtest_ookla_upload") or
                                          r._field == "avg_rate_icmp_probes_dl" or r._field == "avg_rate_icmp_probes_ul")
                    |> map(fn:(r) => ({ r with _time: time(v:r._time) }))
                    |> drop(columns:["meta_extended", "meta_extended_debhash", "meta_extended_dataver", "env", "_start","_stop"])
                 """

        df = self.exec_query(query)

        df["_field"].replace({"iperf_udp_download": "download",
                              "iperf_udp_upload": "upload",
                              "speedtest_ndt7_download": "download",
                              "speedtest_ndt7_upload": "upload",
                              "speedtest_ookla_download": "download",
                              "speedtest_ookla_upload": "upload",
                              "avg_rate_icmp_probes_dl": "download",
                              "avg_rate_icmp_probes_ul": "upload"}, inplace=True)
        df = df.rename(columns={"_time": "Time", "_value": "Speed",
                                "_field": "Direction", "_measurement": "Tool", 
                                "install": "ID"})

        df['Tool'] = df['Tool'].replace(['oplat'], 'iPerf3 (TCP)')
        df['Tool'] = df['Tool'].replace(['iperf'], 'iPerf3 (UDP)')

        return df

    def ping_latency(self):
        """ Returns latency/ping data between 'start' and 'stop'"""

        query = self.base_query + ('|> filter(fn: (r) => (r._field == "Cloudflare_DNS_last_mile_ping_rtt_min_ms" or '
                                        'r._field == "google_rtt_min_ms" or '
                                        'r._field == "google_rtt_avg_ms" or '
                                        'r._field == "uchicago_rtt_avg_ms" or '
                                        'r._field == "amazon_rtt_avg_ms" or '
                                        'r._field == "youtube_rtt_avg_ms" or '
                                        'r._field == "facebook_rtt_avg_ms" or '
                                        'r._field == "wikipedia_rtt_avg_ms" or '
                                        'r._field == "tribune_rtt_avg_ms" or '
                                        'r._field == "suntimes_rtt_avg_ms" or '
                                        'r._field == "Washington_DC_rtt_avg_ms" or '
                                        'r._field == "Atlanta_rtt_avg_ms" or '
                                        'r._field == "Denver_rtt_avg_ms"))'
                                    '|> filter(fn: (r) => (r._measurement == "ping_latency" or r._measurement == "last_mile_rtt"))'
                                    '|> drop(columns:["meta_extended", "meta_extended_debhash", "meta_extended_dataver", "env", "_start","_stop"])')

        df = self.exec_query(query)

        df = df.rename(columns={"_time": "Time", "_value": "RTT",
                                "_measurement": "Measurement",
                                "install": "ID"})
        df['Destination'] = df['_field'].apply(lambda x: 'Last Mile' if "Cloudflare" in x else x.split('_')[0])
        df['Method'] = df['_field'].apply(lambda x: 'Avg' if 'avg' in x else 'Min')
        df.drop(['_field'], axis=1, inplace=True) 

        return df

    def dns_latency(self):
        """ Returns DNS latency data between 'start' and 'stop' """

        query = self.base_query + ('|> filter(fn: (r) => (r._field == "dns_query_avg_ms" or '
                                       'r._field == "dns_query_max_ms"))'
                  '|> drop(columns:["meta_extended", "meta_extended_debhash", "meta_extended_dataver", "env", "_start","_stop"])')

        df = self.exec_query(query)

        df = df.rename(columns={"_time": "Time", "_value": "Query Time",
                                "_measurement": "Measurement", 
                                "install": "ID"})
        df['Type'] = df['_field'].apply(lambda x: 'Avg' if 'avg' in x else 'Max')
        df.drop('_field', axis=1, inplace=True)
        return df

    def lan_bw(self):
        """ Returns DNS latency data between 'start' and 'stop' """

        query = self.base_query + ('|> filter(fn: (r) => (r._field == "lan_bw_server_mbps" or '
                                       'r._field == "lan_bw_client_mbps"))'
                  '|> drop(columns:["meta_extended", "meta_extended_debhash", "meta_extended_dataver", "env", "_start","_stop"])')

        df = self.exec_query(query).drop("_measurement", axis=1)

        df = df.rename(columns={"_time": "Time", "_value": "Speed",
                                "_field": "Measurement",
                                "install": "ID"})
        df['Origin'] = df['Measurement'].apply(lambda x: "Client" if "client" in x else "Netrics")


        return df

    def hops_to_google(self):
        """ Returns number of hops to google between 'start' and 'stop' """

        query = self.base_query + ('|> filter(fn: (r) => r._field == "hops_to_google")'
                  '|> drop(columns:["meta_extended", "meta_extended_debhash", "meta_extended_dataver", "env", "_start","_stop"])')

        df = self.exec_query(query).drop("_measurement", axis=1)

        df = df.rename(columns={"_time": "Time", "_value": "Hops",
                                "_field": "Measurement", 
                                "install": "ID"})

        return df

    def device_count(self, period="active"):
        """
        Returns the number of unique devices on the network between
        'start' and 'stop' for the given 'period'. There are 4 options for the
        period: 'active', '1day', '1week', 'total'. Default is 'active'.

        """
        if period not in ['active', '1day', '1week', 'total']:
            print(f'Error: Unrecognized "period": {period}')
            return None

        query = self.base_query + (f'|> filter(fn: (r) => r._field == "devices_{period}")'
                  '|> drop(columns:["meta_extended", "meta_extended_debhash", "meta_extended_dataver", "env", "_start","_stop"])')

        df = self.exec_query(query)

        df = df.rename(columns={"_time": "Time", "_value": "No. of Devices",
                                "_field": "Period", "_measurement": "Measurement",
                                "install": "ID"})
        df.drop(['Period'], axis=1, inplace=True)

        return df

    def latency_under_load(self):
        """
        Returns latency under load data between 'start' and 'stop'

        """

        query = self.base_query + ('|> filter(fn: (r) => (r._field == "loaded_icmp_abbot.cs.uchicago.edu_avg_rtt_ms_dl" or '
                  'r._field == "loaded_icmp_abbott.cs.uchicago.edu_avg_rtt_ms_ul" or '
                  'r._field == "loaded_tcp_abbott.cs.uchicago.edu_avg_rtt_ms_ul" or '
                  'r._field == "loaded_tcp_abbott.cs.uchicago.edu_avg_rtt_ms_dl"))'
                  '|> drop(columns:["meta_extended", "meta_extended_debhash", "meta_extended_dataver", "env", "_start", "_stop", "name"])')

        df = self.exec_query(query)

        df = df.rename(columns={"_time": "Time", "_value": "RTT",
                                "_field": "Test", "_measurement": "Measurement",
                                "install": "ID"})

        df['Protocol'] = df.apply(process_oplat_proto, axis=1)
        df['Direction'] = df.apply(process_oplat_dir, axis=1)
        df.drop(['Test'], axis=1, inplace=True)

        df['Destination'] = 'abbott.cs.uchicago.edu'

        return df

    def get_installs(self):
        """ Returns list of devices operating between 'start' and 'stop'"""

        query = self.base_query + ('|> filter(fn: (r) => r._measurement == "ping_latency")'
                  '|> filter(fn: (r) => r._field == "google_rtt_min_ms")'
                  '|> drop(columns:["meta_extended", "meta_extended_debhash", "meta_extended_dataver", "env", "_start", "_stop", "name"])'
                  '|> distinct(column: "install")'
                  '|> drop(columns:["result", "table", "_field", "_measurement", "_value"])')

        df = self.exec_query(query)

        return df

    def exec_query(self, query):
        """ Executes 'query' and returns dataframe """

        df = self.client.query_api().query_data_frame(query).drop(["result", "table"], axis=1)
        return df


def process_oplat_proto(row):
    if "icmp" in row['Test']:
        return "icmp"
    elif "tcp" in row['Test']:
        return "tcp"


def process_oplat_dir(row):
    if "dl" in row['Test']:
        return 'download'
    elif "ul" in row['Test']:
        return "upload"


def convert_time(df):
    df["Time"] = pd.to_datetime(df["Time"])
    df = df.set_index("Time")
    return df.tz_convert('US/Central').reset_index()

def main(start, stop):

    # Initialize client to query DB
    print("Configuring client...\n")
    c = Client("src/config.yaml", start, stop)
    print("Client established.\n")

    print("Checking existence of output directory...\n")
    data_path = f"data/netrics/{start}-{stop}"
    if not os.path.exists(data_path):
        print(f"Output directory does not exist. Creating directory: {data_path}")
        os.mkdir(data_path)

    print("Pulling speed test data...\n")
    convert_time(c.speedtest()).to_csv(f"data/netrics/{start}-{stop}/speedtest.csv", index=False)
    print("Speed test data pulled. Pulling latency under load data...\n")
    convert_time(c.latency_under_load()).to_csv(f"data/netrics/{start}-{stop}/lul.csv", index=False)
    print("Latency under load data pulled. Pulling ping latency data...\n")
    convert_time(c.ping_latency()).to_csv(f"data/netrics/{start}-{stop}/ping_latency.csv", index=False)
    print("Ping latency data pulled. Pulling DNS latency data...\n")
    convert_time(c.dns_latency()).to_csv(f"data/netrics/{start}-{stop}/dns_latency.csv", index=False)
    print("DNS latency data pulled. Pulling device count data...\n")
    convert_time(c.device_count()).to_csv(f"data/netrics/{start}-{stop}/device_count.csv", index=False)
    print("Device count data pulled. Pulling hops data...\n")
    convert_time(c.hops_to_google()).to_csv(f"data/netrics/{start}-{stop}/hops_to_google.csv", index=False)
    print("Hops data pulled. Pulling LAN bandwidth data...\n")
    convert_time(c.lan_bw()).to_csv(f"data/netrics/{start}-{stop}/lan_bw.csv", index=False)
    print("LAN bandwidth data pulled. Files saved. Done.\n")


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='Pull Netrics data from InfluxDB and write to CSV files.')
    
    parser.add_argument('-b', '--start_month', default="2021-10-01", help='Start date of the query')
    parser.add_argument('-e', '--stop_month', default="2021-11-01", help='Stop date of the query')
    args = parser.parse_args()
    print(f"Pulling data from {args.start_month} to {args.stop_month}...\n")

    main(args.start_month, args.stop_month)
