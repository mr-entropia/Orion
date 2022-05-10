import os
import socketserver
import pymysql
import json
import datetime

# This application listens on TCP/10001 for properly formatted JSON messages.
# Once one such message is received, it is parsed and information is pushed into
# Cloud SQL database.

# Example of a valid message: {"controller": 1, "status": "dark"}
# Sets controller with ID to status dark (black indicator circle, meaning traffic lights are switched off)

class HandleTCPConnection(socketserver.BaseRequestHandler):
	def handle(self):
		response = json.dumps({"result": "Error"})
		try:
			data = self.request.recv(1024).strip()
			recv = json.loads(data)

			if("controller" in recv):
				if("status" in recv):
					print("Connecting to Cloud SQL...")
					cnx = pymysql.connect(user=db_user, password=db_password, host='127.0.0.1', db=db_name)
					print("OK")
					with cnx.cursor() as cursor:
						now = datetime.datetime.now()
						cursor.execute("INSERT INTO Statuses (Controller, Status, Mode, Alarms) VALUES (\"" + str(recv["controller"]) + "\", \"" + str(recv["status"]) + "\", \"From GKE\", \"" + str(now) + "\")")
						cnx.commit()
						cnx.close()
						response = json.dumps({"result": "Success"})
		except Exception as e:
			response = json.dumps({"result": "Exception happened", "exception": str(e), "time": datetime.datetime.now()})

		finally:
			self.request.sendall(response.encode())

if __name__ == "__main__":
	HOST = ""
	PORT = 10001

	db_user = os.environ.get('DB_USER')
	db_password = os.environ.get('DB_PASS')
	db_name = os.environ.get('DB_NAME')

	print("Starting server on {} port {}...".format(HOST, PORT))

	try:
		with socketserver.TCPServer((HOST, PORT), HandleTCPConnection) as server:
			server.serve_forever()
	except Exception as ex:
		print("ERROR: Unable to open socket! Exception:", ex)
		print("Quitting.")