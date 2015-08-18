#!/usr/bin/python
# encoding: utf-8
from __future__ import unicode_literals

import getopt
import sys
import re
import gevent
import httplib
import time
import socket
import math

from gevent import monkey
monkey.patch_all()

program_name = ''
program_info = '%s is python port of ab' % program_name
version = '0.0.1'
copyright = 'Copyright 2015 tom zhao'

# global for coroutines sync print process
process_mark = []


# the cmd input arguments.
class arguments(object):
    """
    arguments..
    """
    def __init__(self, argv):
        self.requests_count = 1
        self.concurrency = 1
        self.timeout = 30
        self.content_type = "text/plain"
        self.keep_alive = False
        self.print_version = False
        self.print_usage = False
        self.url = ""
        self.method = "GET"
        self.https = False
        self.heartbeatres = 100
        self.request_body = None
        # parse the argv..
        self.arguments_parse(argv)
        self.parse_url()

    def check_arguments(self):
        if self.concurrency > self.requests_count:
            error_handler("Cannot use concurrency level greater than total number \
                           of requests")
        # invalid url
        if self.concurrency < 0:
            error_handler("Invalid concurrency")

    def parse_url(self):
        double_slash_pos = self.url.find("://")
        d = {"http": 80, "https": 443}
        protocal = self.url[:double_slash_pos]
        if protocal == "https":
            self.https = True
        self.port = d.get(protocal)
        if not self.port:
            self.port = 80

        domain_path = self.url[7:]
        pos_start_pos = domain_path.find("/")
        self.path = domain_path[pos_start_pos:]
        domain_path = domain_path[:pos_start_pos]
        colon_pos = domain_path.find(":")
        if colon_pos > 0:
            self.host = domain_path[:colon_pos]
            self.port = int(domain_path[colon_pos+1:])
        else:
            self.host = domain_path

    def arguments_parse(self, argv):
        """
        process the cmd arguments
        """
        try:
            opts, args = getopt.getopt(argv, "n:c:s:T:p:Vkh", [])
        except getopt.GetoptError as err:
            print("ab.py: wrong number of arguments")
            usage()
            sys.exit(2)

        for arg, val in opts:
            if arg == "-n":
                try:
                    self.requests_count = int(val)
                except:
                    error_handler("invalid number of requests [%s]" % val)
            if arg == "-c":
                try:
                    self.concurrency = int(val)
                except:
                    error_handler("invalid number of concurrency [%s]" % val)
            if arg == "-s":
                try:
                    self.timeout = int(val)
                except:
                    error_handler("invalid number of timeout [%s]" % val)

            if arg == "-T":
                self.content_type = val
            if arg == "-h":
                self.print_usage = True
            if arg == "-V":
                self.print_version = True
            if arg == "-k":
                self.keep_alive = True
            if arg == "-p":
                self.method = "POST"
                try:
                    with open(val, 'r', encoding='utf-8') as infile:
                        self.request_body = infile.read()
                except Exception as e:
                    error_handler("Could not open POST data file (%s): No such \
                                   file or directory" % val, False)

        if len(args) == 1:
            self.url = args[0]

        if self.print_version:
            print_version()
            sys.exit(2)
        if self.print_usage:
            usage()
            sys.exit(2)
        self.check_arguments()


class connection_stat(object):
    __slots__ = ('start_time', 'wait_time', 'con_time', 'time')
    # start_time   time of starting the connection
    # wait_time     time of between request and response.
    # connect_time   time to connect
    # time           time for connection


# the result of test
class ab_result(object):
    def __init__(self):
        self.stats = []
        self.cur_count = 0
        self.begin_time = time.time()
        self.end_time = 0
        self.doc_len = 0
        self.done = 0
        self.total_doc_len = 0
        self.failed = 0
        self.server_software = ""

    def print_result(self, params):
        all_time = self.end_time - self.begin_time
        req_per_sec = self.done / all_time
        times = [stat.time for stat in self.stats]
        req_time = sum(times) / len(times) * 1000
        avg_req_time = all_time / self.done*1000
        transfer_rate = self.total_doc_len / all_time

        print("")
        print("Server Software:        {0}".format(self.server_software))
        print("Server Hostname:        {0}".format(params.host))
        print("Server Port:            {0}".format(params.port))
        print("")
        print("Document Path:          {0}".format(params.path))
        print("Document Length:        {0}".format(self.doc_len))
        print("")
        print("Concurrency Level:      {0}".format(params.concurrency))
        print("Time taken for tests:   {0} seconds".format(all_time))
        print("Complete requests:      {0}".format(self.done))
        print("Failed requests:        {0}".format(self.failed))
        print("Write errors:           {0}".format(self.failed))
        print("HTML transferred:       {0} bytes".format(self.total_doc_len))
        print("")
        print("Requests per second:    %.2f [#/sec] (mean)" % req_per_sec)
        print("Time per request:       %.2f [ms] (mean)" % req_time)
        print("Time per request:       %.2f [ms] (mean, across all requests)"
              % avg_req_time)
        print("Transfer rate:          %.2f [Kbytes/sec] received"
              % (transfer_rate/1024))
        print("")
        print("Connection Times (ms)")
        # statistics
        # wait_time     time of between request and response.
        wait_times = [stat.wait_time for stat in self.stats]
        # connect_time   time to connect
        connect_times = [stat.con_time for stat in self.stats]

        times_sort = sorted(times)
        min_time = times_sort[0] * 1000
        max_time = times_sort[len(times_sort) - 1] * 1000
        med_time = times_sort[len(times_sort) / 2]
        avg_time = req_time
        sdts = [(time_ - med_time)**2 for time_ in times_sort]
        sdt = math.sqrt(sum(sdts))

        wait_times_sort = sorted(wait_times)
        avg_wait_time = sum(wait_times) / len(wait_times) * 1000
        min_wait_time = wait_times_sort[0] * 1000
        max_wait_time = wait_times_sort[len(wait_times_sort) - 1] * 1000
        med_wait_time = wait_times_sort[len(wait_times_sort) / 2]
        sdwaits = [(time_ - med_wait_time)**2 for time_ in wait_times_sort]
        sdwait = math.sqrt(sum(sdwaits))

        connect_times_sort = sorted(connect_times)
        avg_con_time = sum(connect_times) / len(connect_times) * 1000
        min_con_time = connect_times_sort[0] * 1000
        max_con_time = connect_times_sort[len(connect_times_sort) - 1] * 1000
        med_con_time = connect_times_sort[len(connect_times_sort) / 2]
        sdcons = [(time_ - med_con_time)**2 for time_ in connect_times_sort]
        sdcon = math.sqrt(sum(sdcons))

        print("               min  mean[+/-sd] median   max")
        print("Connect:    %5.1f %5.1f %5.1f %5.1f %5.1f"
              % (min_con_time, avg_con_time, sdcon, med_con_time, max_con_time))
        print("Waiting:    %5.1f %5.1f %5.1f %5.1f %5.1f"
              % (min_wait_time, avg_wait_time, sdwait, med_wait_time, max_wait_time))
        print("Total:      %5.1f %5.1f %5.1f %5.1f %5.1f"
              % (min_time, avg_time, sdt, med_time, max_time))

    def end(self):
        self.end_time = time.time()


def get_headers(params):
    """
    make http headers according to command parameter
    """
    headers = {"Content-type": "text/plain"}
    headers["Content-type"] = params.content_type
    if params.keep_alive:
        # https://tools.ietf.org/html/rfc2068
        headers["Connection"] = "Keep-Alive"
    return headers


def print_process(params, done, is_over=False):
    global process_mark
    if params.heartbeatres and not done % params.heartbeatres:
        if done not in process_mark:
            process_mark.append(done)
            print("Completed %d requests" % done)
    if is_over:
        print("Finish %d requests" % done)


def http_test(params, ret):
    """coroutine function"""
    headers = get_headers(params)
    if not params.https:
        conn = httplib.HTTPConnection(params.host, params.port)
    else:
        conn = httplib.HTTPSConnection(params.host, params.port)

    for i in xrange(params.requests_count):
        # end the requests
        if time.time() > params.timeout + ret.begin_time \
                or ret.cur_count >= params.requests_count:
            break

        ret.cur_count += 1
        stat = connection_stat()
        t0 = time.time()
        try:
            conn.connect()
        except Exception as e:
            print("%s %s" % (program_name, str(e)))
            sys.exit(2)

        t1 = time.time()
        conn.request(params.method, params.path, params.request_body, headers=headers)
        t2 = time.time()
        response = conn.getresponse()
        t3 = time.time()
        doc = response.read()
        t4 = time.time()
        conn.close()

        stat.start_time = t0
        stat.wait_time = t4 - t1
        stat.con_time = t1 - t0
        stat.time = t4 - t0
        ret.stats.append(stat)
        ret.done += 1
        ret.doc_len = len(doc)
        ret.total_doc_len += ret.doc_len
        ret.server_software = response.msg['Server']
        print_process(params, ret.cur_count)


def test(params):
    '''the ab.py main processing function'''

    ret = ab_result()
    coroutines = []
    for i in xrange(params.concurrency):
        coroutines.append(gevent.spawn(http_test, params, ret))

    gevent.joinall(coroutines)

    print_process(params, ret.cur_count, True)
    ret.end()
    return ret


def error_handler(tip, with_usage = True):
    print("%s: %s" % (program_name, tip))
    if with_usage:
        usage()
    sys.exit(2)


def print_version():
    print("%s, Version %s \n%s" % (program_info, version, copyright))


def usage(prog_name=program_name):
    print("Usage: %s [options] [http[s]://]hostname[:port]/path\n" % prog_name)
    print("Options are:")
    print("""
    -n requests     Number of requests to perform
    -c concurrency  Number of multiple requests to make at a time
    -s timeout      Seconds to max. wait for each response
                    Default is 30 seconds
    -p postfile     File containing data to POST. Remember also to set -T
    -T content-type Content-type header to use for POST/PUT data, eg.
                    'application/x-www-form-urlencoded'
                    Default is 'text/plain'
    -V              Print version number and exit
    -q              Do not show progress when doing more than 150 requests
    -k              Use HTTP KeepAlive feature
    -h              Display usage information (this message)
    """)


def main():
    args = arguments(sys.argv[1:])
    print_version()
    print("\nBenchmarking %s (be patient)\n" % args.host)
    ab_ret = test(args)
    ab_ret.print_result(args)

if __name__ == '__main__':
    program_name = sys.argv[0]
    main()
