import os
from flask import Flask, request, send_from_directory
import json
import pymysql

db_user = os.environ.get('CLOUD_SQL_USERNAME')
db_password = os.environ.get('CLOUD_SQL_PASSWORD')
db_name = os.environ.get('CLOUD_SQL_DATABASE_NAME')
db_connection_name = os.environ.get('CLOUD_SQL_CONNECTION_NAME')

app = Flask(__name__)


# This method handles responses to all Ajax calls
@app.route('/ajax', methods=['GET'])
def ajax():
    if os.environ.get('GAE_ENV') == 'standard':
        # If deployed, use the local socket interface for accessing Cloud SQL
        unix_socket = '/cloudsql/{}'.format(db_connection_name)
        cnx = pymysql.connect(user=db_user, password=db_password, unix_socket=unix_socket, db=db_name)
    else:
        # If running locally, use the TCP connections instead
        # Set up Cloud SQL Proxy (cloud.google.com/sql/docs/mysql/sql-proxy)
        # so that your application can use 127.0.0.1:3306 to connect to your
        # Cloud SQL instance
        host = '127.0.0.1'
        cnx = pymysql.connect(user=db_user, password=db_password, host=host, db=db_name)


    # Returns all controllers parameters such as position and status, as well as mapview parameters
    if(request.args.get('type') == 'full'):
        with cnx.cursor() as cursor:
            cursor.execute('SELECT Latitude, Longitude, Zoom, MinZoom, MaxZoom, TileSize, ZoomOffset FROM MapView LIMIT 1;')
            result = cursor.fetchall()
            mapview = result

        with cnx.cursor() as cursor:
            cursor.execute('SELECT Id, Name, Latitude, Longitude FROM Controllers ORDER BY Id ASC')
            result = cursor.fetchall()
            controllers = result

        statuses = []

        for controller in controllers:
            with cnx.cursor() as cursor:
                cursor.execute('SELECT Status, Mode, Alarms FROM Statuses WHERE Controller = ' + str(controller[0]) + ' ORDER BY Modified DESC LIMIT 1')
                result = cursor.fetchall()
                status = result[0]
            statuses.append({"name": controller[1], "lat": controller[2], "lon": controller[3], "status": status[0], "mode": status[1], "alarms": status[2]})

        cnx.close()

        return json.dumps(
            {
                "controllers": statuses,
                "mapview":
                    {
                        "lat": mapview[0][0],
                        "lon": mapview[0][1],
                        "zoom": mapview[0][2],
                        "minZoom": mapview[0][3],
                        "maxZoom": mapview[0][4],
                        "tileSize": mapview[0][5],
                        "zoomOffset": mapview[0][6]
                    }
            }
        )
    elif(request.args.get('type') == 'status'):
        with cnx.cursor() as cursor:
            cursor.execute('SELECT Id, Name FROM Controllers ORDER BY Id ASC')
            result = cursor.fetchall()
            controllers = result

        statuses = []

        for controller in controllers:
            with cnx.cursor() as cursor:
                cursor.execute('SELECT Status, Mode, Alarms FROM Statuses WHERE Controller = ' + str(controller[0]) + ' ORDER BY Modified DESC LIMIT 1')
                result = cursor.fetchall()
                status = result[0]
            statuses.append({"name": controller[1], "status": status[0], "mode": status[1], "alarms": status[2]})

        cnx.close()

        return json.dumps(
            {
                "controllers": statuses
            }
        )
    elif(request.args.get('type') == 'control'):
        if(request.args.get('controller') and request.args.get('command')):
            if os.environ.get('GAE_ENV') == 'standard':
                # If deployed, use the local socket interface for accessing Cloud SQL
                unix_socket = '/cloudsql/{}'.format(db_connection_name)
                cnx = pymysql.connect(user=db_user, password=db_password, unix_socket=unix_socket, db=db_name)
            else:
                # If running locally, use the TCP connections instead
                # Set up Cloud SQL Proxy (cloud.google.com/sql/docs/mysql/sql-proxy)
                # so that your application can use 127.0.0.1:3306 to connect to your
                # Cloud SQL instance
                host = '127.0.0.1'
                cnx = pymysql.connect(user=db_user, password=db_password, host=host, db=db_name)

            with cnx.cursor() as cursor:
                cursor.execute('SELECT Id FROM Controllers WHERE name = \'' + request.args.get('controller') + '\' LIMIT 1')
                result = cursor.fetchall()

            with cnx.cursor() as cursor:
                cursor.execute('INSERT INTO Commands (TargetController, Command) VALUES (\'' + str(result[0][0]) + '\', \'' + request.args.get('command') + '\')')
                cnx.commit()
                pass
            
            cnx.close()

            return json.dumps({"result": "Success"})
        else:
            return json.dumps({"result": "Error", "error": "Controller and/or command argument is invalid"})
    else:
        return json.dumps({"result": "Error", "error": "No type argument specified, or type argument is invalid"})

# Serves index page
@app.route('/')
def index():
    return send_from_directory("resources", "mapview.html")

# Serves all resources (i.e. images)
@app.route('/resources/<path:name>')
def get_resource(name):
    return send_from_directory("resources", name, as_attachment=True)

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app.
    app.run(host='127.0.0.1', port=8080, debug=True)
