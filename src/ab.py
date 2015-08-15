#!/usr/bin/python
import getopt
import sys
import re
import select

program_info = 'ab.py is python port of ab'
version = '0.0.1'
copyright = 'Copyright 2015 tom zhao'


# control the connectins
class connections(object):
    def __init__(self):
        pass


# the cmd input arguments.
class arguments(object):
    def __init__(self):
        self.requests_count = 1
        self.concurrency = 1
        self.timelimit = 0
        self.timeout = 30
        self.windowsize = 0
        self.content_type = "text/plain"
        self.keep_alive = False
        self.print_version = False
        self.print_usage = False


class connection_times(object):
    __slots__ = ('start_time', 'wait_time', 'con_time', 'time')
    # start_time   time of starting the connection
    # wait_time     time of between request and response.
    # connect_time   time to connect
    # time           time for connection


# the result of test
class ab_result(object):
    def __init__(self):
        pass

    def print_result(params):
        pass


def test(params):
    ret = ab_result()
    return ret


def error_handler(tip):
    print("%s: %s" % (sys.argv[0], tip))
    usage()
    sys.exit(2)


def check_arguments(params):
    if params.concurrency > params.requests_count:
        error_handler("Cannot use concurrency level greater than total number \
                       of requests")
    # invalid url
    if params.concurrency < 0:
        error_handler("Invalid concurrency")
    p = re.compile('^http://[\d\-a-zA-Z]+(\.[\d\-a-zA-Z]+)*/.*$')
    if p.match(params.url):
        error_handler("invalid URL")


def arguments_parse():
    """
    process the cmd arguments
    """
    params = arguments()
    try:
        opts, args = getopt.getopt(sys.argv[1:], "n:c:t:s:T:Vh", [])
    except getopt.GetoptError as err:
        print("ab.py: wrong number of arguments")
        usage(sys.argv[0])
        sys.exit(2)

    for arg, val in opts:
        if arg == "-n":
            try:
                params.requests_count = int(val)
            except:
                error_handler("invalid number of requests [%s]" % val)
        if arg == "-c":
            try:
                params.concurrency = int(val)
            except:
                error_handler("invalid number of concurrency [%s]" % val)
        if arg == "-t":
            try:
                params.timelimit = int(val)
            except:
                error_handler("invalid number of timelimit [%s]" % val)

        if arg == "-s":
            try:
                params.timeout = int(val)
            except:
                error_handler("invalid number of timeout [%s]" % val)

        if arg == "-T":
            params.content_type = val
        if arg == "-h":
            params.print_usage = True
        if arg == "-V":
            params.print_version = True
        if arg == "-k":
            params.keep_alive = True

    if len(args) == 1:
        params.url = args[0]

    if params.print_version:
        print_version()
        sys.exit(2)
    if params.print_usage:
        usage(sys.argv[0])
        sys.exit(2)
    check_arguments(params)
    return params


def print_version():
    print("%s, Version %s \n%s" % (program_info, version, copyright))


def usage(prog_name):
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
    args = arguments_parse()
    ab_ret = test(args)
    ab_ret.print_result()

if __name__ == '__main__':
    main()
