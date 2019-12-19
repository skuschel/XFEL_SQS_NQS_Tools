#!/bin/bash

exppath=$1

startAtRun=$2

while [ 1 ]; do

	runGet="./runformat.py $startAtRun"
	formattedRun=$($runGet)
	runpath="$exppath/raw/$formattedRun"

	while [ ! -d $runpath ]; do
		echo "Waiting"
		sleep 10
	done

	echo "Checking run $startAtRun"

	karabo-bridge-serve-files $runpath 10201 &
	jobidkb=$!
	echo $jobidkb

	./xfelmay2019-daqalive.py tcp://127.0.0.1:10201 &
	jobiddaq=$!
	echo $jobiddaq

	sleep 10

	startAtRun=$((startAtRun+1))
	waitForRun=$((startAtRun+1))
	runGet="./runformat.py $startAtRun"
	formattedRun=$($runGet)
	runpath="$exppath/raw/$formattedRun"

	while [ ! -d $runpath ]; do
		echo "Waiting"
		sleep 10
	done

	kill $jobiddaq
	kill $jobidkb
done



