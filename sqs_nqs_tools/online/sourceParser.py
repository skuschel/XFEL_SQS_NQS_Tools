import argparse
from ..experimentDefaults import defaultConf

def parseSource():
    parser = argparse.ArgumentParser()

    # Default IP is for locally hosted data
    default='tcp://127.0.0.1:9898'
    default = defaultConf['dataStream_tcp_default']

    #ipdict = {'live': 'tcp://10.253.0.142:6666'}
    ipdict = {'live': defaultConf['dataStream_tcp_live'],
                'offline': defaultConf['dataStream_tcp_offline']}

    # Define how to parse command line input
    parser.add_argument('source', 
                        type=str, 
                        help='the source of the data stream. Default is "{}"'.format(default),
                        default=default, 
                        nargs='?')

    # Parse arguments from command line
    args = parser.parse_args()

    # find the source
    source = args.source
    if source in ipdict:
        source = ipdict[source]
        
    print("Data Stream Source: "+source)
    # Start main function
    return source
