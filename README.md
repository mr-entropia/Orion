# Orion
A Google Cloud Platform proof-of-concept project

The intended use for this software package is monitoring and control of traffic light controllers (TLC).

Traffic light controllers send their status updates to the GKE tlc-midpoint-app via TCP/10001. Those updates are written into the Cloud SQL database.

The frontend application, running on GAE, serves a single map view with all TLCs on the map. The TLC indicator images tell their status at a glance. Frontend updates once every five seconds to let users know of updates to TLC statuses. If user clicks on an icon on the map, they can issue commands to that particular controller. Instead of sending them to a real traffic light controller, the commands are looped straight back in to the database so that the effect can be observed after a short while.

Behind the scenes a control issued from the frontend is delivered to the backend via Cloud Pub/Sub. Please see architecture drawing for more information.
