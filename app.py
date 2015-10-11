import aerospike
import urllib2
import json
import sys
import datetime

args = sys.argv
FILE_NAME = args[1]
NUM_POINTS = int(args[2])
NAMESPACE = 'prod'
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


##############################
## Set up aerospike connection
##############################
config = {
    'hosts': [
        ( '54.152.234.234', 3000, )
    ],
    'policies': {
        'timeout': 1000, # milliseconds
    }
}

client = aerospike.client(config)
client.connect()

###########
# Query Uber
###########

SERVER_TOKEN = 'fEdujyqYJcU7IM-FjxjDOH6Vc2Y1RAxrB7IVhoBt'
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

for i in range(NUM_POINTS):
    latitude, longitude = lines[i]
    request_price = urllib2.Request('https://api.uber.com/v1/estimates/price?start_latitude={}&start_longitude={}&end_latitude={}&end_longitude={}'.
                format(
                    latitude,
                    longitude,
                    latitude,
                    longitude,
                )
            )

    request_price.add_header('Authorization', 'Token %s' % SERVER_TOKEN)

    resp = urllib2.urlopen(request_price)
    data = json.load(resp)

    data['latitude'] = latitude
    data['longitude'] = longitude

    data_list.append(data)

##############
# Write to DB
##############

epoch_time = (datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)).total_seconds()
key = ('test', 'price', str(epoch_time),)

stored_data = {
    'timestamp': str(epoch_time),
    'data': data_list,
}
client.put(key, stored_data)

##############
# Log to console
##############
print json.dumps(stored_data, indent=4, sort_keys=False)
