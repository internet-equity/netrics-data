#!/usr/bin/env python3
import os, sys, gzip
import json, csv, re
import traceback
from os import path
from datetime import datetime, timezone
from dateutil import tz
from dateutil import parser as duparser
import sqlite3
from anonymizeip import anonymize_ip
from collections import OrderedDict
from threading import Thread, Lock
### json2influx
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

date_to_process_after = "20230401"

influxclient = None
if os.environ.get("INFLUXDB_TOKEN") is not None:
    bucket = "netrics-prod0"
    token = os.environ.get("INFLUXDB_TOKEN")
    org = "DSI"
    url = "https://us-east-1-1.aws.cloud2.influxdata.com"
    influxclient = InfluxDBClient(url=url, token=token, org=org)

    write_api = influxclient.write_api(write_options=SYNCHRONOUS)
    query_api = influxclient.query_api()


DNS_LATENCY_TARGET = "8.8.8.8"

mutex = Lock()

conn = sqlite3.connect('json2csv.db')

from_zone = tz.gettz('UTC')
to_zone = tz.gettz('America/Chicago')
csvdir = "csvdata"

conn.execute('''
CREATE TABLE IF NOT EXISTS processed(
         NAME TEXT NOT NULL PRIMARY KEY
);''')


c = conn.cursor().execute("""SELECT count(*) FROM processed""").fetchall()
 
processed = int(c[0][0])
processed_error = 0

c = conn.cursor().execute("""SELECT name FROM processed""",)\
              .fetchall()

processed_list = [i[0] for i in c]

visited = OrderedDict()
for i in processed_list:
    k=i[:25]
    if k not in visited.keys(): visited[k] = {}
    visited[k][i[26:]]=None

'''
id_isp_zip2.csv in the format of 

short_device_id,isp,zipcode
faac,att,60615
1bba,xfinity,60623
... 
'''
mapf = r'id_isp_zip3.csv'
mapd = {}
speedtest_csvfile_prefix = "netrics_speedtest"
latency_csvfile_prefix = "netrics_latency"
counter_csvfile_prefix = "netrics_counter"

iperf3_target = 'abbott.cs.chicago.edu'

def t_zip(d):
    r = None
    try:
      r =  mapd[(d[len(d) - 4:])][1]
    except Exception as e:
        return "0"
    return r

def t_isp(d):
    r = None
    try:
      r =  mapd[(d[len(d) - 4:])][0]
    except Exception as e:
        return "None"
    return r

def t_topic(d):
    r = None
    try:
      r =  mapd[(d[len(d) - 4:])][2]
    except Exception as e:
        return "None"
    return r



with open(mapf, 'r') as f:
  reader = csv.reader(f)
  for r in reader:
    try:
      mapd[r[0]]=[ r[1], r[2], r[3] ]
    except IndexError as ie:
        print(f"ERROR: {ie} [{r}]")

### speedtest
#  time        TIMESTAMPTZ       NOT NULL,
#  deviceid    TEXT              NOT NULL,
#  tool        TEXT              NOT NULL,
#  direction   TEXT              NOT NULL,
#  protocol    TEXT              NULL,
#  target      TEXT              NULL,
#  pktloss     DOUBLE PRECISION  NULL,
#  retrans     DOUBLE PRECISION  NULL,
#  zip         INT               NULL,
#  isp         TEXT              NULL,
#  value       DOUBLE PRECISION  NULL

### latency
#  time        TIMESTAMPTZ       NOT NULL,  
#  deviceid    TEXT              NOT NULL,
#  tool        TEXT              NOT NULL,
#  direction   TEXT		NULL, 
#  protocol    TEXT              NOT NULL,
#  target      TEXT		NOT NULL,
#  pktloss     DOUBLE PRECISION  NULL, ## NEW
#  method      TEXT		NOT NULL,
#  zip         INT		NULL,
#  isp         TEXT              NULL,
#  value       DOUBLE PRECISION  NULL

def clean(msg):
    if msg is not None:
        msg=msg.replace("\n"," ")
        msg=msg.replace("\r"," ")
    return msg

def netrics_csvwrite_encrypteddns(latency_writer,
                                  mtime, id, topic, mjson,
                                  ipaddr_anon, ipaddr_changed):
  """
  Write CSV for Encrypted DNS test (dig command)

  :param latency_writer: csvwriter ref
  :param mtime: measurement timestamp
  :param id: device id
  :param m: measurement json
  """
  to_return = True
  target = None
  direction = "rtt"
  protocol = "dns"
  method = "dig"
  pktloss = None
  for k in mjson.keys():
    if k.endswith("_encrypted_dns_latency"):
      target=k.split("_encrypted_dns_latency")[0]

    try:
        float(mjson[k])
    except ValueError as ve:
        row = [mtime, id, 'encrypteddns', direction, protocol, target, pktloss,
              method, t_zip(id), t_isp(id), None, topic, ipaddr_anon, ipaddr_changed, 1, clean(mjson[k])]
        latency_writer.writerow(row)
        pass
        continue
 
    try:
        row = [mtime, id, 'encrypteddns', direction, protocol, target, pktloss,
              method, t_zip(id), t_isp(id), mjson[k], topic, ipaddr_anon, ipaddr_changed, 0, None]
        latency_writer.writerow(row)    
    except (KeyError, IndexError):
      pass
      continue 


def netrics_csvwrite_goresp(speedtest_writer,
                            counter_writer,
                            mtime, id, topic, mjson,
                            ipaddr_anon, ipaddr_changed):
  """
  Write CSV for GoResponsiveness measurement against abbott server

  :param speedtest_writer: csvwriter ref
  :param counter_writer: csvwriter ref
  :param mtime: measurement timestamp
  :param id: device id
  :param m: measurement json
  """
  for k in mjson.keys():

    target = iperf3_target
    if k.endswith('_error'):
      row = [mtime, id, 'goresponsiveness', None, target,
                          t_zip(id), t_isp(id), None, topic, ipaddr_anon, ipaddr_changed, 1, clean(mjson[k])]
      counter_writer.writerow(row)
      break
    if k == 'default_goresp_rpm_mean':
      method = "mean"
      row = [mtime, id, 'goresponsiveness', method, target,
                          t_zip(id), t_isp(id), mjson[k], topic, ipaddr_anon, ipaddr_changed, 0, None]
      counter_writer.writerow(row)
    if k == 'default_goresp_rpm_p90':
      method = "p90"
      row = [mtime, id, 'goresponsiveness', method, target,
                          t_zip(id), t_isp(id), mjson[k], topic, ipaddr_anon, ipaddr_changed, 0, None]
      counter_writer.writerow(row)
    if k == 'default_goresp_download_speed':
      row = [mtime, id, 'goresponsiveness', 'download', 'tcp', target, None,
                    None, t_zip(id), t_isp(id), mjson[k], topic, ipaddr_anon, ipaddr_changed, 0, None]
      speedtest_writer.writerow(row)
    if k == 'default_goresp_upload_speed':
      row = [mtime, id, 'goresponsiveness', 'upload', 'tcp', target, None,
                    None, t_zip(id), t_isp(id), mjson[k], topic, ipaddr_anon, ipaddr_changed, 0, None]
      speedtest_writer.writerow(row) 



def netrics_csvwrite_hopstotarget(counter_writer,
                                  mtime, id, topic, mjson,
                                  ipaddr_anon, ipaddr_changed):
  """
  Write CSV for hops to target data point,
  hops to google

  :param counter_writer: csvwriter ref
  :param mtime: measurement timestamp
  :param id: device id
  :param m: measurement json
  """
  for k in mjson.keys():
    if k.endswith("_error"):
      target = k.split("_")[0]
      row = [mtime, id, 'hops_to_target', None, target,
             t_zip(id), t_isp(id), None, topic, ipaddr_anon, ipaddr_changed, 1, clean(mjson[k])]
      counter_writer.writerow(row)


    if "hops_to_" in k:
      target = k.split("_")[2]
      method = "tr"
      row = [mtime, id, 'hops_to_target', method, target,
             t_zip(id), t_isp(id), mjson[k], topic, ipaddr_anon, ipaddr_changed, 0, None]
      counter_writer.writerow(row)

def netrics_csvwrite_connecteddev(counter_writer,
                                  mtime, id, topic, mjson,
                                  ipaddr_anon, ipaddr_changed):
  """
  Write CSV for connected devices data point,
  1day, 1week, active, total

  :param counter_writer: csvwriter ref
  :param mtime: measurement timestamp
  :param id: device id
  :param m: measurement json
  """
  for k in mjson.keys():
    if "devices_" in k:
      target = None
      method = k.split("_")[1]
      row = [mtime, id, 'connected_devices_arp', method, target,
             t_zip(id), t_isp(id), mjson[k], topic, ipaddr_anon, ipaddr_changed, 0, None]
      counter_writer.writerow(row)



def netrics_csvwrite_lastmile(latency_writer,
                                  mtime, id, topic, mjson,
                                  ipaddr_anon, ipaddr_changed):
  """
  Write CSV for IPerf3 data point, download/upload speed, jitter

  :param speedtest_writer: csvwriter ref
  :param latency_writer: csvwriter ref
  :param mtime: measurement timestamp
  :param id: device id
  :param m: measurement json
  """
  pktloss = None
  for k in mjson.keys():
    if "packet_loss" in k:
      pktloss = mjson[k]
      break
  
  for k in mjson.keys():
    direction = "rtt"
    protocol = "icmp"
     
    key=k.split("_")

    target = key[0]
    if k.endswith("_error"):
      row = [mtime, id, 'last_mile_rtt', direction, protocol, target, pktloss,
              None, t_zip(id), t_isp(id), None, topic, ipaddr_anon, ipaddr_changed, 1, clean(mjson[k])]
      latency_writer.writerow(row)
      continue
 
    try:
      method1 = key[len(key)-4] 
      method2 = key[len(key)-2]
      if method2 == "loss": continue
      method = method1 + "_" + method2
      try:
          float(mjson[k])
      except:
          print(f"WARNING: netrics_csvwrite_lastmile {mjson[k]}")
          return

      row = [mtime, id, 'last_mile_rtt', direction, protocol, target, pktloss,
              method, t_zip(id), t_isp(id), mjson[k], topic, ipaddr_anon, ipaddr_changed, 0, None]
      latency_writer.writerow(row)
    except IndexError:
      pass
      continue

def netrics_csvwrite_iperf3(speedtest_writer, latency_writer,
                                  mtime, id, topic, mjson,
                                  ipaddr_anon, ipaddr_changed):
  """
  Write CSV for IPerf3 data point, download/upload speed, jitter

  :param speedtest_writer: csvwriter ref
  :param latency_writer: csvwriter ref
  :param mtime: measurement timestamp
  :param id: device id
  :param m: measurement json
  """
  if 'error' in mjson.keys():
    if mjson['error']:
        errormsg = "unknown"
        if 'iperf_download_error' in mjson.keys():
           errormsg = mjson['iperf_download_error']
        if 'iperf_upload_error' in mjson.keys():
           errormsg = mjson['iperf_download_error']
        row = [mtime, id, 'iperf3', None, None, iperf3_target, None,
               None, t_zip(id), t_isp(id), None, topic, ipaddr_anon, ipaddr_changed, 1, clean(errormsg)]
        speedtest_writer.writerow(row)
        return

  for k in mjson.keys():
    key=k.split("_")
    try:
      if key[2] == "upload" and key[3] == "jitter":
        direction = key[2]
        protocol = key[1]
        target = iperf3_target
        method = key[3]
        row = [mtime, id, 'iperf3', direction, protocol, target, None,
              method, t_zip(id), t_isp(id), mjson[k], topic, ipaddr_anon, ipaddr_changed, 0, None]
        latency_writer.writerow(row)
        continue
      elif key[2] == "download" and key[3] == "jitter":
        direction = key[2]
        protocol = key[1]
        target = iperf3_target
        method = key[3]
        row = [mtime, id, 'iperf3', direction, protocol, target, None,
              method, t_zip(id), t_isp(id), mjson[k], topic, ipaddr_anon, ipaddr_changed, 0, None]
        latency_writer.writerow(row)
        continue
    except IndexError:
      pass
    try:
      if key[2] == "upload" and key[1] == "udp":
        row = [mtime, id, 'iperf3', 'upload', 'udp', iperf3_target, None,
                    None, t_zip(id), t_isp(id), mjson[k], topic, ipaddr_anon, ipaddr_changed, 0, None]
        speedtest_writer.writerow(row)
      elif key[2] == "download" and key[1] == "udp":
        row = [mtime, id, 'iperf3', 'download', 'udp', iperf3_target, None,
                    None, t_zip(id), t_isp(id), mjson[k], topic, ipaddr_anon, ipaddr_changed, 0, None]
        speedtest_writer.writerow(row)
    except IndexError:
      pass

def netrics_csvwrite_pinglatency(latency_writer,
                                  mtime, id, topic, mjson,
                                  ipaddr_anon, ipaddr_changed):
  """
  Write CSV for Ping Latency data point, icmp

  :param speedtest_writer: csvwriter ref
  :param latency_writer: csvwriter ref
  :param mtime: measurement timestamp
  :param id: device id
  :param m: measurement json
  """
  to_return = True
  pktloss = {}
  for k in mjson.keys():
    key=k.split("_")
    try:
      if key[1] == "packet":
        target = key[0]
        pktloss[target] = mjson[k]
        to_return = False
    except (KeyError, IndexError):
      pass
      continue

  if to_return: return

  for k in mjson.keys():
    key=k.split("_")
    try:
      if key[1] == "rtt":
        target = key[0]
        direction = "rtt"
        protocol = "icmp"
        error = 0
        errormsg = None
        value = mjson[k]
        if k.endswith("_error"):
            error = 1
            value = None
            errormsg = mjson[k]
        else:
            method = key[2]
        pktloss_csv = pktloss[target]
        row = [mtime, id, 'ping_latency', direction, protocol, target, pktloss_csv,
              method, t_zip(id), t_isp(id), value, topic, ipaddr_anon, ipaddr_changed, error, clean(errormsg)]
        latency_writer.writerow(row)    
    except (KeyError, IndexError):
      pass
      continue 

def netrics_csvwrite_dnslatency(latency_writer,
                                  mtime, id, topic, mjson,
                                  ipaddr_anon, ipaddr_changed):
  """
  Write CSV for DNS Latency data point, icmp

  :param speedtest_writer: csvwriter ref
  :param latency_writer: csvwriter ref
  :param mtime: measurement timestamp
  :param id: device id
  :param m: measurement json
  """
  for k in mjson.keys():
      try:
          target = DNS_LATENCY_TARGET
          direction = "rtt"
          protocol = "icmp"
          if k.endswith("_error"):
             row = [mtime, id, 'dns_latency', direction, protocol, target, None,
                    None, t_zip(id), t_isp(id), None, topic, ipaddr_anon, ipaddr_changed, 1, clean(mjson[k])]
             latency_writer.writerow(row)
             continue
 
          m=re.search(r"^dns_query_([a-z]+)_ms", k)
          if m is not None:
             method = m.group(1)
             row = [mtime, id, 'dns_latency', direction, protocol, target, None,
                    method, t_zip(id), t_isp(id), mjson[k], topic, ipaddr_anon, ipaddr_changed, 0, None]
             latency_writer.writerow(row)
      except (KeyError, IndexError):
          pass
          continue

def netrics_csvwrite_oplat(speedtest_writer, latency_writer,
                                  mtime, id, topic, mjson,
                                  ipaddr_anon, ipaddr_changed):
  """
  Write CSV for OpLat data point, loaded, unloaded, icmp, tcp

  :param speedtest_writer: csvwriter ref
  :param latency_writer: csvwriter ref
  :param mtime: measurement timestamp
  :param id: device id
  :param m: measurement json
  """

  if 'error' in mjson.keys():
    errormsg = 'unknown'
    target = None
    for k in mjson.keys():
      if k.endswith("_error"): 
          errormsg = mjson[k]
          target=k.split("_")[0]
      row = [mtime, id, 'oplat', None, None, target, None,
             None, t_zip(id), t_isp(id), None, topic, ipaddr_anon, ipaddr_changed, 1, clean(errormsg)]
      latency_writer.writerow(row)
      return

  to_return = True
  pktloss = {}
  for k in mjson.keys():
    key=k.split("_")
    if key[0] == "loaded" or key[0] == "unloaded":
      to_return = False
      if key[3] == "pkt":
        method = key[0]
        protocol = key[1]
        direction = "download" if key[len(key)-1] == "dl" else "upload"
        if method not in pktloss.keys():
          pktloss[method] = {}
        if protocol not in pktloss[method].keys():
          pktloss[method][protocol] = {}
        pktloss[method][protocol][direction] = mjson[k] 

  if to_return: return

  for k in mjson.keys():
    key=k.split("_")
    
    if key[0] == "loaded" or key[0] == "unloaded":
      if key[3] == "pkt": continue
      method = key[0]
      method_csv = key[0] + "_" + key[3]
      protocol = key[1]
      target = key[2]
      direction = "download" if key[len(key)-1] == "dl" else "upload" 
      pktloss_csv = pktloss[method][protocol][direction]
      row = [mtime, id, 'oplat', direction, protocol, target, pktloss_csv,
             method_csv, t_zip(id), t_isp(id), mjson[k], topic, ipaddr_anon, ipaddr_changed, 0, None]
      latency_writer.writerow(row)

def netrics_csvwrite_ndt7(speedtest_writer, latency_writer,
                                  mtime, id, topic, mjson,
                                  ipaddr_anon, ipaddr_changed):
  """
  Write CSV for Ndt7 data point, throughput (speedtest),
  latency and jitter 

  :param speedtest_writer: csvwriter ref
  :param latency_writer: csvwriter ref
  :param mtime: measurement timestamp
  :param id: device id
  :param m: measurement json
  """

  target = ""
  retrans = 0.0
  try:
      target = mjson['speedtest_ndt7_server']
  except:
      print(f"WARNING: speedtest_ndt7_server not present")
      pass
  try:
      retrans = mjson['speedtest_ndt7_downloadretrans']
  except:
      print(f"WARNING: speedtest_ndt7_downloadretrans not present")
      pass

  if 'ndt_error' in mjson.keys():
    if mjson['ndt_error']:
        row = [mtime, id, 'ndt7', None, None, target, None,
                      None, t_zip(id), t_isp(id),
                      None, topic, ipaddr_anon, ipaddr_changed, 1, clean(mjson['error'])]
        speedtest_writer.writerow(row)
        return


  if(mjson['speedtest_ndt7_download'] > 0.0):
    row = [mtime, id, 'ndt7', 'download', 'tcp', target, None,
                   retrans, t_zip(id), t_isp(id),
                   mjson['speedtest_ndt7_download'], topic, ipaddr_anon, ipaddr_changed, 0, None]
    speedtest_writer.writerow(row)
  else:
    print(f"WARNING: speedtest_ndt7_download == 0")

  if(mjson['speedtest_ndt7_upload'] > 0.0):
    row = [mtime, id, 'ndt7', 'upload', 'tcp', target, None,
                  retrans, t_zip(id), t_isp(id),
                  mjson['speedtest_ndt7_upload'], topic, ipaddr_anon, ipaddr_changed, 0, None]
    speedtest_writer.writerow(row)
  else:
    print(f"WARNING: speedtest_ndt7_upload == 0")

  if(mjson['speedtest_ndt7_downloadlatency'] > 0.0):
    row = [mtime, id, 'ndt7', 'rtt', 'tcp', target, None,
                  'avg', t_zip(id), t_isp(id),
                  mjson['speedtest_ndt7_downloadlatency'], topic, ipaddr_anon, ipaddr_changed, 0, None]
    latency_writer.writerow(row)
  else:
    print(f"WARNING: speedtest_ndt7_downloadlatency == 0")


def netrics_csvwrite_ookla(speedtest_writer, latency_writer,
                                    mtime, id, topic, mjson,
                                    ipaddr_anon, ipaddr_changed):
  """
  Write CSV for Ookla data point, throughput (speedtest),
  latency and jitter 

  :param speedtest_writer: csvwriter ref
  :param latency_writer: csvwriter ref
  :param mtime: measurement timestamp
  :param id: device id
  :param m: measurement json
  """
  target = ""
  pktloss = 0.0
  try:
      target = mjson['speedtest_ookla_server_host']
  except:
      print(f"WARNING: speedtest_ookla_server_host not present")
      pass
  try:
      pktloss = mjson['speedtest_ookla_pktloss2']
  except:
      print(f"WARNING: speedtest_ookla_pktloss2 not present")
      pass

  if 'ookla_error' in mjson.keys():
    if mjson['ookla_error']:
      if mjson['error'].startswith("==="): #license agreement, skip
          return
      else:
          row = [mtime, id, 'ookla', None, None, None, None,
                 None, t_zip(id), t_isp(id),
                 None, topic, ipaddr_anon, ipaddr_changed, 1, clean(mjson['error'])]
          speedtest_writer.writerow(row)
          return

  if(mjson['speedtest_ookla_download'] > 0.0):
    row = [mtime, id, 'ookla', 'download', 'tcp', target, pktloss,
                   None, t_zip(id), t_isp(id),
                   mjson['speedtest_ookla_download'], topic, ipaddr_anon, ipaddr_changed, 0, None]
    speedtest_writer.writerow(row)
  else:
    print(f"WARNING: speedtest_ookla_download == 0")

  if(mjson['speedtest_ookla_upload'] > 0.0):
    row = [mtime, id, 'ookla', 'upload', 'tcp', target, pktloss,
                  None, t_zip(id), t_isp(id),
                  mjson['speedtest_ookla_upload'], topic, ipaddr_anon, ipaddr_changed, 0, None]
    speedtest_writer.writerow(row)
  else:
    print(f"WARNING: speedtest_ookla_upload == 0")

  if(mjson['speedtest_ookla_latency'] > 0.0):
    row = [mtime, id, 'ookla', 'rtt', 'tcp', target, None,
                 'avg', t_zip(id), t_isp(id),
                  mjson['speedtest_ookla_latency'], topic, ipaddr_anon, ipaddr_changed, 0, None]
    latency_writer.writerow(row)
  else:
    print(f"WARNING: speedtest_ookla_latency == 0")

  if(mjson['speedtest_ookla_jitter'] > 0.0):
    row = [mtime, id, 'ookla', 'rtt', 'tcp', target, None,
                 'jitter', t_zip(id), t_isp(id),
                  mjson['speedtest_ookla_jitter'], topic, ipaddr_anon, ipaddr_changed, 0, None]
    latency_writer.writerow(row)
  else:
    print(f"WARNING: speedtest_ookla_jitter == 0")

########################### MAIN ############################

speedtest_header = ['time', 'deviceid', 'tool', 'direction',
                    'protocol', 'target', 'pktloss', 'retrans',
                    'zip', 'isp', 'value', 'topic', 'anonipaddr', 'ipaddrchanged', 'error', 'errormsg']
latency_header = ['time', 'deviceid', 'tool', 'direction',
                  'protocol', 'target', 'pktloss','method',
                  'zip', 'isp', 'value', 'topic', 'anonipaddr', 'ipaddrchanged', 'error', 'errormsg']

counter_header = ['time', 'deviceid', 'tool', 'method', 'target',
                                'zip', 'isp', 'value', 'topic', 'anonipaddr', 'ipaddrchanged', 'error', 'errormsg']


try:
    os.mkdir(csvdir)
except OSError as error:
    print(error)
    sys.exit(1)

csvwriter = {}
def gen_csvwriter(csvwriter,date, filedata):
    d=date[:6]
    if d not in csvwriter.keys():
       csvwriter[d] = {}
       speedtest_csvfile_name = os.path.join(csvdir, f"{speedtest_csvfile_prefix}_{d}.csv")
       speedtest_csvfile_exists = path.exists(speedtest_csvfile_name)
       speedtest_csvfile = open(speedtest_csvfile_name, 'a')
       speedtest_csvwriter = csv.writer(speedtest_csvfile)
       if not speedtest_csvfile_exists: speedtest_csvwriter.writerow(speedtest_header)
       csvwriter[d]['speedtest'] = speedtest_csvwriter
       csvwriter[d]['speedtest_file'] = speedtest_csvfile

       latency_csvfile_name = os.path.join(csvdir, f"{latency_csvfile_prefix}_{d}.csv")
       latency_csvfile_exists = path.exists(latency_csvfile_name)
       latency_csvfile = open(latency_csvfile_name, 'a')
       latency_csvwriter = csv.writer(latency_csvfile)
       if not latency_csvfile_exists: latency_csvwriter.writerow(latency_header)
       csvwriter[d]['latency'] = latency_csvwriter
       csvwriter[d]['latency_file'] = latency_csvfile

       counter_csvfile_name = os.path.join(csvdir, f"{counter_csvfile_prefix}_{d}.csv")
       counter_csvfile_exists = path.exists(counter_csvfile_name)
       counter_csvfile = open(counter_csvfile_name, 'a')
       counter_csvwriter = csv.writer(counter_csvfile)
       if not counter_csvfile_exists: counter_csvwriter.writerow(counter_header)
       csvwriter[d]['counter'] = counter_csvwriter
       csvwriter[d]['counter_file'] = counter_csvfile

       csvwriter[d]['flist']=[filedata]
    else:
       csvwriter[d]['flist'].append(filedata)

def get_csvwriter(csvwriter, date):
    d=date[:6]
    return csvwriter[d]['speedtest'], csvwriter[d]['latency'], csvwriter[d]['counter']

pathlocaldash = None
rootDir = sys.argv[1]

last_ipaddr = {}

def getpathdata(dirName, fname, ftype):
      jfile = os.path.join(dirName, fname)
      path_date=os.path.dirname(dirName)
      path_dev=os.path.dirname(path_date)
      path_topic=os.path.dirname(path_dev)
      dev=os.path.basename(path_dev)
      topic = os.path.basename(path_topic)
      date = os.path.basename(path_date)
      return {'dev': dev, 'jfile': jfile, 'fname': fname,
              'topic': topic, 'date': date, "ftype": ftype}

count = 0
device_check = {}
for dirName, subdirList, fileList in os.walk(rootDir):
  for fname in fileList:
    if fname.endswith(".json.gz"):
      pathdata = getpathdata(dirName, fname, "json.gz")
      gen_csvwriter(csvwriter, pathdata['date'], pathdata)
    elif fname.endswith(".csv.gz"):
      pathdata = getpathdata(dirName, fname, "csv.gz")
      gen_csvwriter(csvwriter, pathdata['date'], pathdata)
    elif fname.endswith(".json"):
      pathdata = getpathdata(dirName, fname, "json")
      gen_csvwriter(csvwriter, pathdata['date'], pathdata)
      count += 1
      dev = pathdata['dev']
      topic = pathdata['topic']
      if dev not in last_ipaddr.keys():
          last_ipaddr[dev] = None
      try:
        device_check[dev]['checked']
        continue
      except KeyError:
        device_check[dev] = { 'checked': True if 
            t_isp(dev) != "None" else False}
        device_check[dev]['topic'] = topic

print(device_check)
stop_here = False
for k in device_check.keys():
  desc = "OK" if device_check[k]['checked'] else f"Missing data in {mapf}"
  if not device_check[k]['checked']: stop_here = True
  print(f"{k} ({device_check[k]['topic']}) {desc}")

if stop_here: sys.exit(0)
print(f"PROCESSED: {processed} + {processed_error}(failed) / {count}")

def process_jsongz(fd, topic, speedtest_writer):
    id = fd['dev']
    with gzip.open(fd['jfile'], mode='rt', newline='') as f:
        try:
            j = json.load(f)
        except ValueError:
            print(f"WARN: failed to load json.gz {fd['jfile']}")
            return
        if j.get('Download', {}).get('ServerMeasurements') is None:
            print(f"WARN: no 'Download' in {fd['jfile']}")
            return
        try:
            ts       = format_date(int(duparser.parse(j['StartTime']).timestamp()))
            tcp_info = j['Download']['ServerMeasurements'][-1]['TCPInfo']
            wifi_bw  = 8 * tcp_info['BytesAcked'] / tcp_info['ElapsedTime']
        except (KeyError, IndexError, ValueError) as err:
            print(f"WARN: error ({err}) {fd['jfile']}")
            return

        row = [ts, id, 'local_dash_server', 'download', 'tcp', 'netrics.local',
               None, None, t_zip(id), t_isp(id),
               wifi_bw, topic, None, None, 0, None]
        speedtest_writer.writerow(row)


def format_date(d):
    utc_date = datetime.fromtimestamp(d)
    utc_tmp = utc_date.replace(tzinfo=from_zone)
    utc = utc_tmp.strftime('%Y-%m-%d %H:%M:%S')
    return utc

def process_csvgz(fd, topic, speedtest_writer, counter_writer):
    id = fd['dev']
    with gzip.open(fd['jfile'], mode='rt', newline='') as f:
        try:
            records = list(csv.reader(f))
            if fd['topic'] == 'trial':
                for r in records:
                    try:
                        ts = format_date(int(r[0]))
                        size_bytes = int(r[1])
                        period_ms = int(r[2])
                    except:
                        print(f"WARN: trial data error {fd['jfile']}")
                        continue
                    row = [ts, id, 'local_dash_client', 'download', 'tcp', 'netrics.local',
                           None, None, t_zip(id), t_isp(id),
                           8 * size_bytes / period_ms, topic, None, None, 0, None]
                    speedtest_writer.writerow(row)
            if fd['topic'] == 'survey':
                for r in records:
                    try:
                        ts = format_date(int(r[0]))
                        subjective = int(r[1])
                    except:
                        print(f"WARN: trial data error {fd['jfile']}")
                        continue
                    row = [ts, id, 'score', 'subjective', None,
                           t_zip(id), t_isp(id), subjective, topic, None, None, 0, None]
                    counter_writer.writerow(row)
        except EOFError as eof:
            print(f"WARN: error reading {fd['jfile']}")

CONF_INC_EXTRA = False
def insert_influx(jfname):
  try:
    with open(jfname) as fjson:
        j = json.load(fjson)
        if 'Meta' not in j:
          print("WARN: (no Meta) malformed json. Continuing.. ")
          return
        if 'Measurements' not in j:
          print("WARN: (no Measurements) malformed json. Continuing.. ")
          return

        meta_id = j['Meta']['Id'] if j['Meta']['Id'] is not None else 'default'
        #print(f"\t{meta_id}")
        meta_time = float(j['Meta']['Time'])
        #print(f"\t{meta_time}")
        meta_enable = False
        if 'Extended' in j['Meta'].keys():
          meta_enable = True
          if CONF_INC_EXTRA:
             meta_extended_gitlog = j['Meta']['Extended']['gitlog']
             print(f"\t{meta_extended_gitlog}")
             meta_extended_annotation = j['Meta']['Extended']['Annotation'] \
             if j['Meta']['Extended']['Annotation'] is not None else ""
             print(f"\t{meta_extended_annotation}")
          try:
            meta_extended_dataver = int(j['Meta']['Extended']['dataver'])
          except:
            print("WARN: DATAVER malformed.")
            meta_extended_dataver = 0
          #print(f"\t{meta_extended_dataver}")
          meta_extended_debhash = j['Meta']['Extended']['debhash']
          #print("\t{} ({})".format(meta_extended_debhash[-7:], meta_extended_debhash))
        for k in j['Measurements'].keys():
          #print("-->"+k+ " " + ("+" if type(j['Measurements'][k]) == dict else ""))
          p = Point(k)
          p.tag("install", meta_id)
          #p.tag("env", "dev")
          if meta_enable:
            #p.tag("meta_extended_gitlog", meta_extended_gitlog)
            p.tag("meta_extended_dataver", meta_extended_dataver)
            p.tag("meta_extended_debhash", meta_extended_debhash[-7:])
            #p.tag("meta_extended_annotation", meta_extended_annotation)
          if type(j['Measurements'][k]) == dict:
            for measurement in j['Measurements'][k].keys():
              try:
                value = float(j['Measurements'][k][measurement])
              except:
                value = j['Measurements'][k][measurement]
              p.field(measurement, value)
          else:
            try:
              value = float(j['Measurements'][k])
            except:
              value = j['Measurements'][k]
            p.field(measurement, value)
          p.time(datetime.fromtimestamp(meta_time))
          try:
              write_api.write(bucket=bucket, record=p)
          except Exception as e:
              print(e)
              print(e, file=sys.stderr)
              pass
  except Exception as e:
    print(e)
    print(e, file=sys.stderr)
 


def thread_csv_month(d, cw):
    global processed
    global processed_error
    print(f"processing {d}")
    for fd in cw['flist']:
      fname = fd['fname']
      jfile = fd['jfile']
      dev = fd['dev']
      date = fd['date']
      #topic = fd['topic']
      topic = t_topic(dev)
      ftype = fd['ftype']

      d1 = datetime.strptime(date, "%Y%m%d")
      if d1 < datetime.strptime(date_to_process_after, "%Y%m%d"): continue

      if fd['ftype'] == 'json' and influxclient is not None:
          insert_influx(jfile)

      try:
          visited[dev][fname]
          continue
      except KeyError:
          pass
      ipaddr_changed = 0
      ipaddr_anon = None

      speedtest_csvwriter,\
             latency_csvwriter,\
             counter_csvwriter = get_csvwriter(csvwriter, date)

      if processed % 100 == 0:
          print(f"PROCESSED({d}): {processed} / {count}")

      if ftype == 'csv.gz':
          process_csvgz(fd, topic, speedtest_csvwriter, counter_csvwriter)
          continue

      if ftype == 'json.gz':
          process_jsongz(fd, topic, speedtest_csvwriter)
          continue

      with open(jfile) as jf:
          try:
             j = json.load(jf)
          except:
            with mutex:
                processed_error += 1
            continue
          id = j['Meta']['Id']

          if id != dev:
              print("WARNING *** j['Meta']['Id']({id}) != dev({dev})")
              id = dev

          utc = format_date(j['Meta']['Time'])
          #utc_date = datetime.fromtimestamp(j['Meta']['Time'])
          #utc_tmp = utc_date.replace(tzinfo=from_zone)
          #utc = utc_tmp.strftime('%Y-%m-%d %H:%M:%S')
          ##central = utc.astimezone(to_zone)
          ipaddr = None
          try:
              ipaddr = j['Measurements']['ipquery']['ipv4']
          except KeyError:
              pass

          if ipaddr is not None:
              if last_ipaddr[dev] is not None:
                  if last_ipaddr[dev] != ipaddr:
                      ipaddr_changed = 1
                      last_ipaddr[dev] = ipaddr
              else:
                  last_ipaddr[dev] = ipaddr
          try: 
              ipaddr_anon = anonymize_ip(last_ipaddr[dev])
          except ValueError:
              ipaddr_anon = None
              pass


          ################ OOKLA #################
          try:
              mjson = j['Measurements']['ookla']
              netrics_csvwrite_ookla(speedtest_csvwriter,
                                     latency_csvwriter,
                                          utc, id,
                                          topic, mjson,
                                          ipaddr_anon, ipaddr_changed)
          except KeyError:
              pass

          ################ NDT7 #################
          try:
              mjson = j['Measurements']['ndt7']
              netrics_csvwrite_ndt7(speedtest_csvwriter,
                                     latency_csvwriter,
                                          utc, id,
                                          topic, mjson,
                                          ipaddr_anon, ipaddr_changed)
          except KeyError:
              pass

          ################ OPLAT #################
          try:
              mjson = j['Measurements']['oplat']
              netrics_csvwrite_oplat(speedtest_csvwriter,
                                     latency_csvwriter,
                                          utc, id,
                                          topic, mjson,
                                          ipaddr_anon, ipaddr_changed)
          except KeyError:
              pass

          ################ PING_LATENCY #################
          try:
              mjson = j['Measurements']['ping_latency']
              netrics_csvwrite_pinglatency(latency_csvwriter,
                                           utc, id,
                                           topic, mjson,
                                           ipaddr_anon, ipaddr_changed)
          except KeyError:
              pass


          ################ DNS_LATENCY #################
          try:
              mjson = j['Measurements']['dns_latency']
              netrics_csvwrite_dnslatency(latency_csvwriter,
                                           utc, id,
                                           topic, mjson,
                                           ipaddr_anon, ipaddr_changed)
          except KeyError:
              pass


          ################ IPERF3 #################
          try:
              mjson = j['Measurements']['iperf']
              netrics_csvwrite_iperf3(speedtest_csvwriter,
                                      latency_csvwriter,
                                          utc, id,
                                          topic, mjson,
                                          ipaddr_anon, ipaddr_changed)
          except KeyError:
              pass

          ################ LAST MILE #################
          try:
              mjson = j['Measurements']['last_mile_rtt']
              netrics_csvwrite_lastmile(latency_csvwriter,
                                          utc, id,
                                          topic, mjson,
                                          ipaddr_anon, ipaddr_changed)
          except KeyError:
              pass
          
          ############# CONNECTED DEVICES ############
          try:
              mjson = j['Measurements']['connected_devices_arp']
              netrics_csvwrite_connecteddev(counter_csvwriter,
                                          utc, id,
                                          topic, mjson,
                                          ipaddr_anon, ipaddr_changed)
          except KeyError:
              pass

            
          ############# HOPS TO TARGET ############
          try:
              mjson = j['Measurements']['hops_to_target']
              netrics_csvwrite_hopstotarget(counter_csvwriter,
                                          utc, id,
                                          topic, mjson,
                                          ipaddr_anon, ipaddr_changed)
          except KeyError:
              pass


          ############# GORESPONSIVENESS (RPM) ############
          try:
              mjson = j['Measurements']['goresp']
              netrics_csvwrite_goresp(speedtest_csvwriter,
                                          counter_csvwriter,
                                          utc, id,
                                          topic, mjson,
                                          ipaddr_anon, ipaddr_changed)
          except KeyError:
              pass


          ############# ENCRYPTED DNS ############
          try:
              mjson = j['Measurements']['encrypteddns']
              netrics_csvwrite_encrypteddns(latency_csvwriter,
                                          utc, id,
                                          topic, mjson,
                                          ipaddr_anon, ipaddr_changed)
          except KeyError:
              pass

          with mutex:
              processed += 1
#      c = conn.cursor()
#      try:
#        c.execute("""INSERT INTO processed(name) VALUES(?)""", (id+"-"+fname,))
#        conn.commit()
#      except Exception as e:
#        exc_type, _, exc_tb = sys.exc_info()
#        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
#        print("error: ({0}) {1} {2} {3}".format(str(e), exc_type, fname, exc_tb.tb_lineno))
#        traceback.print_exc()
#        pass
#        continue

for d,cw in csvwriter.items():
    thread = Thread(target=thread_csv_month, args=(d, cw))
    csvwriter[d]['thread'] = thread
    csvwriter[d]['thread'].start()


print(processed)


for d,cw in csvwriter.items():
  csvwriter[d]['thread'].join()
  csvwriter[d]['speedtest_file'].close()
  csvwriter[d]['latency_file'].close()
  csvwriter[d]['counter_file'].close()

