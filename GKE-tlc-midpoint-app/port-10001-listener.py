import os
import socketserver
import pymysql
import json

sql_string = ""

class HandleTCPConnection(socketserver.BaseRequestHandler):
	def handle(self):
		response = json.dumps({"result": "Error"})
		try:
			data = self.request.recv(1024).strip()
			recv = json.loads(data)

			if("controller" in recv):
				if("status" in recv):
					with cnx.cursor() as cursor:
						cursor.execute("INSERT INTO Statuses (Controller, Status, Mode, Alarms) VALUES (\"" + str(recv["controller"]) + "\", \"" + str(recv["status"]) + "\", \"From GKE\", \"---\")")
						cnx.commit()
						response = json.dumps({"result": "Success"})
		except Exception as e:
			response = json.dumps({"result": "Exception happened", "exception": str(e)})

		finally:
			self.request.sendall(response.encode())

if __name__ == "__main__":
	HOST = ""
	PORT = 10001

	db_user = os.environ.get('DB_USER')
	db_password = os.environ.get('DB_PASS')
	db_name = os.environ.get('DB_NAME')
	print("User, pass, db:", db_user, db_password, db_name)

	print("Connecting to SQL...")
	cnx = pymysql.connect(user=db_user, password=db_password, host='127.0.0.1', db=db_name)
	with cnx.cursor() as cursor:
		cursor.execute('SELECT Name FROM Controllers LIMIT 1')
		result = cursor.fetchall()
		sql_string = str(result[0][0])
	print("OK")


	print("Starting server on {} port {}...".format(HOST, PORT))

	try:
		with socketserver.TCPServer((HOST, PORT), HandleTCPConnection) as server:
			server.serve_forever()
	except Exception as ex:
		print("ERROR: Unable to open socket! Exception:", ex)
		print("Quitting.")