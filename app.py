"""
Usage:
    >>python app.py server_token points_file
"""

import aerospike
import datetime
import json
import sys
import urllib2

def _prune_price(price):
    return {
        'display_name': price['display_name'],
        'surge_multiplier': price['surge_multiplier'],
    }

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

try:
    for latitude, longitude in lines:
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
    pass


epoch_time = (datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)).total_seconds()
key = (NAMESPACE, SET, str(epoch_time))

stored_data = {
    'timestamp': str(epoch_time),
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
print json.dumps(stored_data, indent=4, sort_keys=False)
