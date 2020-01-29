from kafka import KafkaProducer
import getopt, sys, os

try:
    opts, args = getopt.getopt(sys.argv[1:], "d:b:t:")
except getopt.GetoptError:
    print('kafkaPush -b <bootstrap-server> -d <data>')
    sys.exit(2)

bootstrap_server = ''
data = ''
topic = ''

for opt, arg in opts:
    if opt == '-b':
        bootstrap_server = arg
    elif opt == '-d':
        data = arg
    elif opt == '-t':
        topic = arg

if not bootstrap_server:
    bootstrap_server = os.getenv('KAFKA_BOOTSTRAP')

producer = KafkaProducer(bootstrap_servers=bootstrap_server)
producer.send(topic, bytes(data, encoding='utf-8'), partition=0)
producer.close()
