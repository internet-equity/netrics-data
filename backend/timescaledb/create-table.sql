SHOW time zone;
SET TIME ZONE 'America/Chicago';

CREATE TABLE IF NOT EXISTS community (
  communityid SERIAL PRIMARY KEY,
  label       VARCHAR(40) UNIQUE
);

CREATE TABLE IF NOT EXISTS device (
  deviceid   SERIAL,
  label       VARCHAR(30) NOT NULL,
  isp         VARCHAR(30) NULL,
  zip         INT    NULL,
  deployment  VARCHAR(30) NOT NULL,
  PRIMARY KEY(deviceid)
);

ALTER TABLE device ADD COLUMN communityid INT NULL
CONSTRAINT fk_community REFERENCES community (communityid) 
ON UPDATE CASCADE ON DELETE CASCADE;

-- UPDATE device SET communityid = c.communityid from community c where c.label='LINCOLN SQUARE' and device.label = 'nm-mngd-20210927-4def23bd';

CREATE TABLE speedtest (
  time        TIMESTAMPTZ       NOT NULL,  
  deviceid    TEXT              NOT NULL,
  tool        TEXT              NOT NULL, 
  direction   TEXT              NOT NULL,
  protocol    TEXT		NULL,
  target      TEXT		NULL,
  pktloss     DOUBLE PRECISION  NULL, 
  retrans     DOUBLE PRECISION  NULL, 
  zip         INT		NULL,
  isp         TEXT              NULL,
  value       DOUBLE PRECISION  NULL 
);

CREATE TABLE latency (
  time        TIMESTAMPTZ       NOT NULL,  
  deviceid    TEXT              NOT NULL,
  tool        TEXT              NOT NULL,
  direction   TEXT		NULL, 
  protocol    TEXT              NOT NULL,
  target      TEXT		NOT NULL,
  method      TEXT		NOT NULL,
  zip         INT		NULL,
  isp         TEXT              NULL,
  value       DOUBLE PRECISION  NULL
);

CREATE TABLE speedtest2 (
  time        TIMESTAMPTZ       NOT NULL,  
  deviceid    INT               NOT NULL,
  tool        TEXT              NOT NULL, 
  direction   TEXT              NOT NULL,
  protocol    TEXT		NULL,
  target      TEXT		NULL,
  pktloss     DOUBLE PRECISION  NULL, 
  retrans     DOUBLE PRECISION  NULL, 
  value       DOUBLE PRECISION  NOT NULL,
  CONSTRAINT fk_device
      FOREIGN KEY(deviceid) 
	  REFERENCES device(deviceid)
);

CREATE TABLE latency2 (
  time        TIMESTAMPTZ       NOT NULL,  
  deviceid    INT               NOT NULL,
  tool        TEXT              NOT NULL,
  direction   TEXT		NULL, 
  protocol    TEXT              NOT NULL,
  target      TEXT		NOT NULL,
  method      TEXT              NOT NULL,
  value       DOUBLE PRECISION  NULL,
  CONSTRAINT fk_device
      FOREIGN KEY(deviceid) 
	  REFERENCES device(deviceid)
);

select l.time,d.label,l.tool,l.direction,l.protocol,l.target,d.deployment,l.value from latency2 l, device d where l.deviceid = d.deviceid; 

insert into device (label, isp, deployment, zip)
select distinct(s.deviceid), s.isp, 'chicago' as deployment, s.zip from speedtest s;

insert into speedtest2 (time,deviceid,tool,direction,protocol,target,pktloss,retrans,value)
select s.time,d.deviceid,s.tool,s.direction,s.protocol,s.target,s.pktloss,s.retrans,s.value from speedtest s, device d where s.deviceid = d.label; 

insert into latency2 (time,deviceid,tool,direction,protocol,target,method,value)
select l.time,d.deviceid,l.tool,l.direction,l.protocol,l.target,l.method,l.value from latency l, device d where l.deviceid = d.label;

create or replace view latency3 as select l.time,d.label,l.tool,l.direction,l.protocol,l.target,d.isp,d.deployment,d.zip,community.label as community,l.method,l.value 
from latency2 l, device d
left join community ON d.communityid = community.communityid
where l.deviceid = d.deviceid;

create or replace view speedtest3 as select s.time,d.label,s.tool,s.direction,s.protocol,s.target,s.pktloss,s.retrans,d.isp,d.deployment,d.zip,community.label as community,s.value 
from speedtest2 s, device d
left join community ON d.communityid = community.communityid
where s.deviceid = d.deviceid;

postgres=# SELECT create_hypertable('speedtest', 'time');
postgres=# SELECT create_hypertable('latency', 'time');
postgres=# SELECT create_hypertable('speedtest2', 'time');
postgres=# SELECT create_hypertable('latency2', 'time');

CREATE UNIQUE INDEX device_idx ON device (deviceid);

-- **** QUERY EXAMPLES ****

-- select l.community, l.isp, avg(l.value) from latency3 l 
-- where l.method = 'Avg'
-- group by l.community, l.isp;


-- **** DROP TABLES ****

-- drop table community cascade;
-- drop table device cascade;
-- drop table latency2 cascade;
-- drop table speedtest2 cascade; 
