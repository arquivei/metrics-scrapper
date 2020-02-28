# Base
import time, os, json, sys
import atexit
import prometheus_client
# Scrappers
import scrappers
# Logging
import logging
from pythonjsonlogger import jsonlogger

from apscheduler.schedulers.background import BackgroundScheduler
from wsgiref.simple_server import make_server

# Configures logger: https://github.com/madzak/python-json-logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)
if 'LOG_LEVEL' in os.environ:
    logger.setLevel(os.environ['LOG_LEVEL'])

supported_keys = [
    'timestamp',
    'levelname',
    'message',
    'funcName',
    'lineno',
    'module'
]

log_format = lambda x: ['%({0:s})'.format(i) for i in x]
custom_format = " ".join(log_format(supported_keys))
logHandler = logging.StreamHandler(sys.stdout)
logHandler.setFormatter(jsonlogger.JsonFormatter(custom_format, timestamp = True))
logger.addHandler(logHandler)

def app_run():
    logger.info("App starting", extra={"http_port": os.environ['HTTP_PORT']})
    app = prometheus_client.make_wsgi_app()
    httpd = make_server('', int(os.environ['HTTP_PORT']), app)
    httpd.serve_forever()

# global constants
PROMETHEUS_CONFIG=json.loads(os.environ['PROMETHEUS_CONFIG'])

# Basic metrics
# @TODO: get VERSION from somehere :P
i = prometheus_client.Info(
    'system',
    'Version and environment information',
    namespace=PROMETHEUS_CONFIG['namespace']
)
i.info({'version': "2002.0", 'env': os.environ['APP_ENV']})

# Defines the scrappers to run every 15 seconds
scheduler = BackgroundScheduler(timezone="UTC")
scheduler.start()

inited_metrics = {}

JOBS_CONFIG=json.loads(os.environ['JOBS_CONFIG'])

def add_scrapper(scrapper, instances):
    for instance in instances:
        interval = instance['check_interval'] if 'check_interval' in instance else 15
        scrapper_id = "{}_scrapper-{}".format(scrapper, instance['id'])

        logger.info("Adding scrapper", extra={"scrapper": scrapper, "interval": interval, "id": scrapper_id})
        scheduler.add_job(
            inited_metrics[scrapper].scrapper,
            id=scrapper_id,
            trigger="interval",
            seconds=interval,
            max_instances=1,
            kwargs={"instance":instance}
        )

for scrapper in JOBS_CONFIG:
    if scrapper in inited_metrics:
        continue
    if scrapper == 'redis_queue':
        inited_metrics[scrapper] = scrappers.RedisQueue(PROMETHEUS_CONFIG)
        add_scrapper(scrapper, JOBS_CONFIG[scrapper])
    if scrapper == 'humancoder':
        inited_metrics[scrapper] = scrappers.HumanCoder(PROMETHEUS_CONFIG)
        add_scrapper(scrapper, JOBS_CONFIG[scrapper])

# Final endpoints: stop scheduler when exiting the code
atexit.register(lambda: scheduler.shutdown())

if __name__ == '__main__':
    app_run()
