'''
module providing functions for data access.
'''
from . import generatorpipeline as gp


# ---- Access the data on disk or network ----


def servedata(host, type='REQ'):
    '''
    Generator for the online data stream.
    Input: 
        host: ip address of data stream
        type: ???
    Output:
        dictionary of values for current event
    '''
    from karabo_bridge import Client
    # Generate a client to serve the data
    c = Client(host, type)

    # Return the newest event in the datastream using an iterator construct
    for ret in c:
    	yield ret



# ---- Access specific data from the stream ----


#@gp.pipeline_parallel()  #does not work due to pickling error of the undecorated function
def _getTof(streamdata):
    data, meta = streamdata
    ret = data['SQS_DIGITIZER_UTC1/ADC/1:network']['digitizers.channel_1_A.raw.samples']
    return ret[262000:290000]
getTof = gp.pipeline_parallel(1)(_getTof)  # this works
