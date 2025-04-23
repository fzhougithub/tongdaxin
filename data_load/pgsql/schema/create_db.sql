\! mkdir /var/tellme/pgsql/fzhou
create tablespace fzhou location '/var/tellme/pgsql/fzhou';

create database fzhou tablespace fzhou;

\c fzhou
create schema if not exists stock authorization current_role;
select * from information_schema.schemata;

create user pfchart with login password 'pfchart1';
grant usage on schema stock to pfchart;
grant create on schema stock to pfchart;
grant select on all tables in schema stock to pfchart;
grant update on all tables in schema stock to pfchart;
grant insert on all tables in schema stock to pfchart;
grant delete on all tables in schema stock to pfchart;

alter role pfchart set search_path to stock,public,"$user";
GRANT pg_read_server_files TO pfchart;
alter user pfchart set search_path to stock,pfchart,public;

add below line into /var/tellme/pgsql/data/pg_hba.conf

host    fzhou           pfchart         127.0.0.1/24            peer

psql -h localhost -d fzhou -U pfchart -W


CREATE TABLE IF NOT EXISTS stock.stockhistory (
    symbol VARCHAR(50),
    day DATE,
    o FLOAT,
    h FLOAT,
    l FLOAT,
    c FLOAT,
    amount FLOAT,
    v FLOAT,
    last FLOAT,
    PRIMARY KEY (symbol, day) -- Unique constraint on symbol and day
); 
#partition by list(symbol);

Then, we have to pre-create partitions for each of the symbol, it will be changed in future, we rely on the script

-- Partition for symbol 'AAPL'
CREATE TABLE {table_name}_aapl PARTITION OF {table_name}
FOR VALUES IN ('AAPL');

-- Partition for symbol 'GOOG'
CREATE TABLE {table_name}_goog PARTITION OF {table_name}
FOR VALUES IN ('GOOG');

-- Partition for symbol 'MSFT'
CREATE TABLE {table_name}_msft PARTITION OF {table_name}
FOR VALUES IN ('MSFT');


https://www.postgresql.org/docs/current/catalogs.html

fzhou=# select * from information_schema.enabled_roles
fzhou-# ;
          role_name
-----------------------------
 postgres
 pg_database_owner
 pg_read_all_data
 pg_write_all_data
 pg_monitor
 pg_read_all_settings
 pg_read_all_stats
 pg_stat_scan_tables
 pg_read_server_files
 pg_write_server_files
 pg_execute_server_program
 pg_signal_backend
 pg_checkpoint
 pg_maintain
 pg_use_reserved_connections
 pg_create_subscription
(16 rows)


alter table stock.history rename to stockhistory_init;

CREATE TABLE IF NOT EXISTS stock.stockhistory (
    symbol VARCHAR(50),
    day DATE,
    o FLOAT,
    h FLOAT,
    l FLOAT,
    c FLOAT,
    amount FLOAT,
    v FLOAT,
    last FLOAT,
    PRIMARY KEY (symbol, day) -- Unique constraint on symbol and day
)partition by list(symbol);


fzhou=# create table stockhistory_300001 partition of stock.stockhistory for values in ('300001');
CREATE TABLE


