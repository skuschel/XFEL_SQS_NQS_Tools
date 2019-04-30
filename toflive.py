#!/usr/bin/env python3

# Stephan Kuschel, 2019

import numpy as np

def servedata(host, type='REQ'):
    from karabo_bridge import Client
    c = Client(host, type)
    for ret in c:
    	yield ret






def main(source):
    for data, meta in servedata(source):
        print(data.keys())




if __name__=='__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=str, help='the source of the data stream',
            default='tcp://127.0.0.1:9898', nargs='?')
    args = parser.parse_args()
    main(args.source)
