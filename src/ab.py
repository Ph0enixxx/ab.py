#!/usr/bin/python
import getopt
import sys
import re
import gevent
import httplib
import time

program_name = ''
program_info = '%s is python port of ab' % program_name
version = '0.0.1'
copyright = 'Copyright 2015 tom zhao'


# the cmd input arguments.
class arguments(object):
    """
    arguments..
    """
    def __init__(self, argv):
        self.requests_count = 1
        self.concurrency = 1
        self.timelimit = 0
        self.timeout = 30
        self.windowsize = 0
        self.content_type = "text/plain"
        self.keep_alive = False
        self.print_version = False
        self.print_usage = False
        self.url = ""
        self.method = "GET"
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
        d = {"http":80, "https":443}
        self.port = d.get(self.url[:double_slash_pos])
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
            opts, args = getopt.getopt(argv, "n:c:t:s:T:Vh", [])
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
            if arg == "-t":
                try:
                    self.timelimit = int(val)
                except:
                    error_handler("invalid number of timelimit [%s]" % val)

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

    def print_result(self, params):
        print self.stats
        print self.cur_count

def http_test(params, ret):
    for i in xrange(params.requests_count):
        stat = connection_stat()
        conn = httplib.HTTPConnection(params.host, params.port)
        t0 = time.time()
        conn.connect()
        t1 = time.time()
        conn.request(params.method, params.path)
        t2 = time.time()
        response = conn.getresponse()
        t3 = time.time()
        response.read()
        t4 = time.time()
        conn.close()
        if time.time() > params.timeout + ret.begin_time \
              or ret.cur_count >= params.requests_count:
            break
        stat.start_time = t0
        stat.wait_time = t4 - t1
        stat.con_time = t1 - t0
        stat.time = t4 - t0
        ret.stats.append(stat)
        ret.cur_count += 1


def test(params):
    '''the ab.py main processing function'''

    ret = ab_result()
    coroutines = []
    for i in xrange(params.concurrency):
        coroutines.append(gevent.spawn(http_test, params, ret))
    gevent.joinall(coroutines)

    return ret


def error_handler(tip):
    print("%s: %s" % (program_name, tip))
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
    -t timelimit    Seconds to max. to spend on benchmarking
                    This implies -n 50000
    -s timeout      Seconds to max. wait for each response
                    Default is 30 seconds
    -b windowsize   Size of TCP send/receive buffer, in bytes
    -T content-type Content-type header to use for POST/PUT data, eg.
                    'application/x-www-form-urlencoded'
                    Default is 'text/plain'
    -k              Use HTTP KeepAlive feature
    -h              Display usage information (this message)
    """)


def main():
    args = arguments(sys.argv[1:])
    ab_ret = test(args)
    ab_ret.print_result(args)

if __name__ == '__main__':
    program_name = sys.argv[0]
    main()
