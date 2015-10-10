import aerospike

config = {
    'hosts': [
        ( '54.152.234.234', 3000 )
    ],
    'policies': {
        'timeout': 1000 # milliseconds
    }
}

client = aerospike.client(config)
client.connect()

