#! /bin/bash
exec python port-10001-listener.py &
exec python sql-to-tlc-commander.py