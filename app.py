"""
Usage:
    >>python app.py server_token points_file
"""

import aerospike
import json
import sys
import time
import urllib2

start_time = time.time()

def _prune_price(price):
    return {
        'display_name': price['display_name'],
        'surge_multiplier': price['surge_multiplier'],
    }

def _current_milli_time():
    return int(round(time.time() * 1000))

args = sys.argv

###########
# Constants
###########

SERVER_TOKEN = args[1]
FILE_NAME = args[2]
NAMESPACE = 'test'
SET = 'price'

#######################
# Read points from file
#######################

with open(FILE_NAME, 'r') as ins:
    lines = []
    for line in ins:
        strs = line.split()
        ll_tuple = (strs[0], strs[1])
        lines.append(ll_tuple)


###########
# Query Uber
###########

data_list = []

# Unused requests
#request_product = urllib2.Request(
#        'http://api.uber.com/v1/products?latitude={}&longitude={}'.
#            format(latitude, longitude),
#        )
#
#
#request_time = urllib2.Request(
#        'http://api.uber.com/v1/estimates/time?start_latitude={}&start_longitude={}'.
#            format(latitude, longitude),
#        )

for latitude, longitude in lines:
    try:
        request_price = urllib2.Request('https://api.uber.com/v1/estimates/price?start_latitude={}&start_longitude={}&end_latitude={}&end_longitude={}'.
                    format(latitude, longitude, latitude, longitude)
                )

        request_price.add_header('Authorization', 'Token %s' % SERVER_TOKEN)

        resp = urllib2.urlopen(request_price)
        data = json.load(resp)

        data['prices'] = [_prune_price(price) for price in data['prices']]

        data['latitude'] = latitude
        data['longitude'] = longitude

        data_list.append(data)
    except Exception:
        break


current_milli_time = _current_milli_time()
key = (NAMESPACE, SET, current_milli_time)

stored_data = {
    'timestamp': current_milli_time,
    'data': data_list,
}

##############################
## Set up aerospike config
##############################
config = {
    'hosts': [
        ( '54.152.234.234', 3000, )
    ],
    'policies': {
        'timeout': 1000,
    }
}

##############
# Write to DB
##############
try:
    client = aerospike.client(config)
    client.connect()
    client.put(key, stored_data)
except Exception:
    pass

##############
# Log to console
##############
print(' --- Execution took %s seconds --- ' % (time.time() - start_time))
print json.dumps(stored_data, indent=4, sort_keys=False)
