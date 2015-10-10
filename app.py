import aerospike
import urllib2
import json

##############################
## Set up aerospike connection
##############################
#config = {
#    'hosts': [
#        ( '54.152.234.234', 3000, )
#    ],
#    'policies': {
#        'timeout': 1000, # milliseconds
#    }
#}
#
#client = aerospike.client(config)
#client.connect()

###########
# Query Uber
###########

server_token = 'fEdujyqYJcU7IM-FjxjDOH6Vc2Y1RAxrB7IVhoBt'

latitude = 37.871210
longitude = -122.250281
lat2 = 37.774183
long2 = -122.394756

request_product = urllib2.Request(
        'http://api.uber.com/v1/products?latitude={}&longitude={}'.
            format(latitude, longitude),
        )


request_time = urllib2.Request(
        'http://api.uber.com/v1/estimates/time?start_latitude={}&start_longitude={}'.
            format(latitude, longitude),
        )



request_price = urllib2.Request('https://api.uber.com/v1/estimates/price?start_latitude={}&start_longitude={}&end_latitude={}&end_longitude={}'.
            format(
                latitude,
                longitude,
                lat2,
                long2,
            )
        )

request_price.add_header('Authorization', 'Token %s' % server_token)

resp = urllib2.urlopen(request_price)
data = json.load(resp)

print json.dumps(data, indent=4, sort_keys=True)
