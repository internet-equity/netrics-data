#!/usr/bin/env python3
import pyarrow as pa
import pyarrow.parquet as pq
import pyarrow.csv
import glob
import sys

csvfiles = glob.glob("./csvdata/netrics_latency_*.csv")
csvfiles.extend(glob.glob("./csvdata/netrics_speedtest_*.csv"))
csvfiles.extend(glob.glob("./csvdata/netrics_counter_*.csv"))
print(csvfiles)


convert_options = pyarrow.csv.ConvertOptions()

convert_dict = {
     'time': pa.timestamp('ms', None),
     'deviceid': pa.string(),
     'tool': pa.string(),
     'direction': pa.string(),
     'protocol': pa.string(),
     'target': pa.string(),
     'pktloss': pa.float32(),
     'method': pa.string(),
     'zip': pa.uint32(),
     'isp': pa.string(),
     'value': pa.float64(),
     'topic': pa.string(),
     'anonipaddr': pa.string(),
     'ipaddrchanged': pa.bool_(),
     'error': pa.bool_(),
     'errormsg': pa.string()
}

convert_options = pa.csv.ConvertOptions(
            column_types=convert_dict
                , strings_can_be_null=True
                , quoted_strings_can_be_null=True
                ,timestamp_parsers=["%Y-%m-%d %H:%M:%S"],
            )

for csvf in csvfiles:
  pname = csvf.replace(".csv", ".parquet")
  print(f"Processing {csvf}")

  writer = None
  with pyarrow.csv.open_csv(csvf, convert_options=convert_options) as reader:
    try:
      for next_chunk in reader: 
        if next_chunk is None: break
        if writer is None:
            writer = pq.ParquetWriter(pname, next_chunk.schema)
        next_table = pa.Table.from_batches([next_chunk])
        try:
           writer.write_table(next_table)
        except AssertionError as ae:
           print(f"ERROR: {ae}")
           sys.exit(1)
      if writer is not None: writer.close()
    except Exception as e:
        print(f"{next_chunk}")
        print(f"here: {e}")
