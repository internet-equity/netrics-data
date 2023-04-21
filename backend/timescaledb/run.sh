#!/bin/bash
docker run -d --name timescaledb1 -p 127.0.0.1:5432:5432 -e POSTGRES_PASSWORD=$POSTGRES_PASSWORD timescale/timescaledb:latest-pg15
