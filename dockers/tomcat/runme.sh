#!/bin/bash
/usr/local/tomcat/bin/catalina.sh start
echo "Server starting..."
sleep 10
wget -q -t 1 -T 10 http://127.0.0.1:8080 && echo "server started" || ( echo "server did not start in 10 secs, aborting")

if [ "$#" -eq 0 ] ; then
	echo "Running default test"
	wrk http://localhost:8080/examples/servlets/servlet/HelloWorldExample
else
	case $1 in
		bash)
			exec bash 
			;;
		test)
			cd /tests
			./basics.sh
			;;
		*)
			exec wrk "$@"
			;;
	esac
fi

