from anomaly_checker import db_client
from datetime import datetime, timedelta
from ipaddress import IPv4Address
import geopy.distance
import random


def add_vpn(profile, ip, lat, lon, time, date):
    '''
    Добавляем лог подключения.
    '''
    auto_id = db_client.command("SELECT max(key) from VPN")
    row = [auto_id+1, profile, ip, lat, lon, time, date]
    res = db_client.insert('VPN', [row], column_names=[
                           'key', 'profile', 'IP', 'lat', 'lon', 'time', 'date'])
    return res


def add_anomaly(vpn_id, profile):
    '''
    Добавляем анломалию.
    '''
    auto_id = db_client.command("SELECT max(key) from Anomaly")
    row = [auto_id+1, vpn_id, profile]
    res = db_client.insert('Anomaly', [row], column_names=[
                           'key', 'VPN_id', 'profile'])
    return res


def check_anomalies():
    '''
    Проверка логов на аномалии.
    Берем все логи, начиная с максимального key, который фигурировал в таблице аномалий.
    Для каждого лога находим предыдущий лог того же 
    пользователя и осуществляем математическую проверку на аномалию.
    '''
    last_anomaly = db_client.command("SELECT max(VPN_id) from Anomaly")
    new_vpns_query = db_client.query(
        "SELECT * FROM VPN where key > " + str(last_anomaly) + " ORDER BY key")
    for row in new_vpns_query.result_rows:
        profile = row[1]
        profile_location = (row[3], row[4])
        profile_datetime = datetime.combine(row[6], row[5].time())
        related_vpns_query = db_client.query(
            "SELECT * FROM VPN WHERE profile = '" + profile + "' and key<" + str(row[0]) + " ORDER BY key")
        if len(related_vpns_query.result_rows) > 1:
            related_vpn = related_vpns_query.result_rows[-1]
            related_location = (related_vpn[3], related_vpn[4])
            related_datetime = datetime.combine(
                related_vpn[6], related_vpn[5].time())
            time_passed = (profile_datetime - related_datetime).seconds/3600
            distance_km = geopy.distance.geodesic(
                profile_location, related_location).km
            max_distance_km = time_passed*926
            if distance_km > max_distance_km:
                add_anomaly(row[0], row[1])


def generate_vpns(number_of_vpns):
    '''
    Генерируем рандомные логи подключений.
    '''
    profiles = ['V_Varkentin', 'I_Ivanov', 'S_Burnett']
    ips = ['88.29.25.1', '78.29.32.0']
    for _ in range(number_of_vpns):
        profile = random.choice(profiles)
        ip = random.choice(ips)
        lat = round(random.uniform(-90,  90), 5)
        lon = round(random.uniform(-180, 180), 5)
        last_vpn_query = db_client.query(
            "SELECT * from VPN ORDER BY key DESC LIMIT 1")
        if len(last_vpn_query.result_rows) > 0:
            last_vpn = last_vpn_query.first_row
            vpn_datetime = datetime.combine(last_vpn[6], last_vpn[5].time())
            new_datetime = vpn_datetime + timedelta(hours=random.randint(1, 9))
            add_vpn(profile, ip, lat, lon, new_datetime, new_datetime.date())
        else:
            vpn_data = ('V_Varkentin', IPv4Address('88.29.25.1'), 37.382282, -5.975701, datetime.strptime(
                '25.07.2023 16:20:00', '%d.%m.%Y %H:%M:%S'), datetime.strptime('25.07.2023', '%d.%m.%Y').date())
            add_vpn(*vpn_data)
