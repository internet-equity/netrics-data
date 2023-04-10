#!/usr/bin/env python3
import os
import csv, re
from pathlib import Path

d = os.scandir("./")
l=[i.path.strip("./") for i in d if i.is_dir()]

devdict = {}

errors = []

for i in l:
    topic = os.scandir(Path(i))
    devs=[Path(i.path).name for i in topic if i.is_dir()]
    for dev in devs:
        if re.search("^nm-(mngd|anon)-20[0-9]{6}-[a-z0-9]{8}", dev):
            if dev[-4:] in devdict.keys():
                print(f"WARN: {i}/{dev} already in list ({devdict[dev[-4:]]})")
            else:
                devdict[dev[-4:]] = {'topic': i if i != "default" else "chicago", 'label': dev}

with open('../../id_isp_zip2.csv') as csvfile:
    r = csv.reader(csvfile, delimiter=',', quotechar='|')
    for row in r:
        try:
            print(f"{row[0]},{row[1]},{row[2]},{devdict[row[0]]['topic']}")
        except KeyError as ke:
            errors.append(f"{row[0]},{row[1]},{row[2]},UNKNOWN")

print("ERRORS:")
for e in errors:
    print(e)
