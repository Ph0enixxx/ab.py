ab.py is python port of ab
===================

ab (aka apache benchmark) is widely-used tool for benching http server.<br/>
now I rebuild the software in python, while it 's works on *Uinx.<br/>
it base on gevent and httplib power.

###Requisite
the library gevent is needed.
if you has pip installed on your computer,just execute the command like that on Linux:
sudo pip install gevent



###Usage
http[s]://]hostname[:port]/path

Options are:

-    -n requests     Number of requests to perform
-    -c concurrency  Number of multiple requests to make at a time
-    -s timeout      Seconds to max. wait for each response Default is 30 seconds
-    -p postfile     File containing data to POST. Remember also to set -T
-    -T content-type Content-type header to use for POST/PUT data, eg. 'application/x-www-form-urlencoded' Default is 'text/plain'
-    -V              Print version number and exit
-    -q              Do not show progress when doing more than 150 requests
-    -k              Use HTTP KeepAlive feature
-    -h              Display usage information (this message)

###Example
python ab.py -n 200 -c 10  http://127.0.0.1:8000/
