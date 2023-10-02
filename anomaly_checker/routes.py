from anomaly_checker import app, db_client, db_funcs, tests
from anomaly_checker.migrations.initial_migration import run_migration

@app.route('/run_migrations/', methods=['GET'])
def run_migrations():
    run_migration()
    QUERY = "SELECT * FROM Anomaly"

    result = db_client.query(QUERY)

    return result.result_rows

@app.route('/get_anomalies/', methods=['GET'])
def get_anomalies():
    QUERY = "SELECT * FROM Anomaly"

    result = db_client.query(QUERY)

    return result.result_rows

@app.route('/get_vpns/', methods=['GET'])
def get_vpns():
    QUERY = "SELECT * FROM VPN"

    result = db_client.query(QUERY)
    res = []
    for row in result.result_rows:
        res.append(row[0:1] + row[3:])
    return res

@app.route('/generate_vpns/<n_vpns>', methods=['GET'])
def generate_vpns(n_vpns):
    db_funcs.generate_vpns(int(n_vpns))
    return {"ok": "ok"}

@app.route('/generate_vpns_fixed/', methods=['GET'])
def generate_vpns_fixed():
    tests.add_preset_vpns()
    return {"ok": "ok"}