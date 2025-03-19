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

psql -h localhost -d fzhou -U pfchart -W


CREATE TABLE IF NOT EXISTS {table_name} (
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


