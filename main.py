import time, os, json
import atexit
import prometheus_client

import scrappers

from apscheduler.schedulers.background import BackgroundScheduler
from wsgiref.simple_server import make_server

def app_run():
    app = prometheus_client.make_wsgi_app()
    httpd = make_server('', os.environ['HTTP_PORT'], app)
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
i.info({'version': "2001.0", 'env': os.environ['APP_ENV']})

# Defines the scrappers to run every 15 seconds
scheduler = BackgroundScheduler(timezone="UTC")
scheduler.start()

inited_metrics = {}

JOBS_CONFIG=json.loads(os.environ['JOBS_CONFIG'])

def schedule_jobs(scheduler, scrapper, id_prefix, instances):
    for instance in instances:
        scheduler.add_job(
            scrapper,
            id=id_prefix.format(instance['id']),
            trigger="interval",
            seconds=15,
            max_instances=1,
            kwargs={"instance":instance}
        )

for scrapper in JOBS_CONFIG:
    if scrapper in inited_metrics:
        continue
    if scrapper == 'redis_queue':
        inited_metrics[scrapper] = scrappers.RedisQueue(PROMETHEUS_CONFIG)
        schedule_jobs(
            scheduler,
            inited_metrics['redis_queue'].scrapper,
            "redis_queue_scrapper-{}",
            JOBS_CONFIG[scrapper]['instances']
        )

# Final endpoints: stop scheduler when exiting the code
atexit.register(lambda: scheduler.shutdown())

if __name__ == '__main__':
    # prometheus_client.start_http_server(9000)
    app_run()