import os
import pymysql
from google.cloud import pubsub_v1
import json
import datetime

# This script receives Cloud Pub/Sub control messages and relays them to the
# TLC network, if this were a real system. In this POC, the commands are instead
# written to the Cloud SQL database which then reflects them in the frontend.

project_id = "core-song-343520"
subscription_id = "gke-tlc-midpoint-app"

# This gets called when we receive a new Pub/Sub message
def callback(message: pubsub_v1.subscriber.message.Message) -> None:
	try:
		json_msg = json.loads(message.data)
		target_controller = str(json_msg["target_controller"])
		command = str(json_msg["command"])
		print(f"Target controller: {target_controller}")
		print(f"Command: {command}\n")
		print("Connecting to Cloud SQL...")
		cnx = pymysql.connect(user=db_user, password=db_password, host='127.0.0.1', db=db_name)
		with cnx.cursor() as cursor:
			now = datetime.datetime.now()
			cursor.execute("INSERT INTO Statuses (Controller, Status, Mode, Alarms) VALUES (\"" + str(target_controller) + "\", \"" + str(command) + "\", \"From Pub/Sub\", \"" + str(now) + "\")")
			cnx.commit()
			cnx.close()
			message.ack()

	except Exception as ex:
		print(f"Exception happened in callback: {ex}")
		message.nack()

# The main program
if __name__ == "__main__":
	db_user = os.environ.get('DB_USER')
	db_password = os.environ.get('DB_PASS')
	db_name = os.environ.get('DB_NAME')


	print("Starting Pub/Sub subscription listener...")
	subscriber = pubsub_v1.SubscriberClient()
	subscription_path = subscriber.subscription_path(project_id, subscription_id)

	streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
	print(f"Listening for messages on {subscription_path}...")

	# Busyloop to receive Pub/Sub messages forever
	while True:
		try:
			streaming_pull_future.result()
		except Exception as ex:
			print(f"Exception happened in busyloop: {ex}")
			streaming_pull_future.cancel()  # Trigger the shutdown.
			streaming_pull_future.result()  # Block until the shutdown is complete.