import os
import socketserver
import pymysql

sql_string = ""

class HandleTCPConnection(socketserver.BaseRequestHandler):
	def handle(self):
		print(sql_string)
		self.request.sendall(sql_string.encode())

if __name__ == "__main__":
	HOST = ""
	PORT = 10001

	db_user = os.environ.get('DB_USER')
	db_password = os.environ.get('DB_PASS')
	db_name = os.environ.get('DB_NAME')

	print("Fetching from SQL...")
	cnx = pymysql.connect(user=db_user, password=db_password, host='127.0.0.1', db=db_name)
	with cnx.cursor() as cursor:
		cursor.execute('SELECT Name FROM Controllers LIMIT 1')
		result = cursor.fetchall()
		sql_string = str(result[0][0])
	cnx.close()
	print("OK")


	print("Starting server on {} port {}...".format(HOST, PORT))

	try:
		with socketserver.TCPServer((HOST, PORT), HandleTCPConnection) as server:
			server.serve_forever()
	except Exception as ex:
		print("ERROR: Unable to open socket! Exception:", ex)
		print("Quitting.")