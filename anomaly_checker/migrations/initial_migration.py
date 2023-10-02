from anomaly_checker import db_client

def run_migration():
    db_client.command('DROP TABLE IF EXISTS VPN')
    db_client.command('DROP TABLE IF EXISTS Anomaly')
    db_client.command(
    'CREATE TABLE IF NOT EXISTS VPN (key UInt32, profile String, IP IPv4, lat Float64, lon Float64, time DateTime, date Date) ENGINE MergeTree ORDER BY key')

    db_client.command(
    'CREATE TABLE IF NOT EXISTS Anomaly (key UInt32, VPN_id UInt32, profile String) ENGINE MergeTree ORDER BY key')
