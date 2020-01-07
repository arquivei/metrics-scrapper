from . import scrapper
from prometheus_client import Gauge
import redis

class RedisQueue(scrapper.Scrapper):
    def __init__(self, prometheus_config):
        super(RedisQueue, self).__init__()

        self.queue_size = Gauge(
            "redis_queue_size",
            "Gives the number of elements in specific key",
            ["instance", "queue"],
            namespace=prometheus_config['namespace']
        )

        self.mem_use = Gauge(
            "redis_queue_memuse",
            "Gives allocated memory for specific key",
            ["instance", "queue"],
            namespace=prometheus_config['namespace']
        )

    def scrapper(self, instance):
        try:
            instance = self.get_instance_defaults(instance)
            conn = self.connect(instance['host'], instance['port'], instance['db'])
            self.process_db(conn, instance['prefix'], instance['check_mem'], instance['id'])
        except Exception as e:
            self.logger.warn("Failed to scrape instance", extra={"exception": str(e), "instance": instance})

    def get_instance_defaults(self, instance):
        defaults = {
            "host": "127.0.0.1",
            "port": 6379,
            "db": 0,
            "prefix": "queue",
            "check_mem": False
        }

        return defaults.copy().update(instance)

    def connect(self, host, port, db):
        conn = redis.Redis(host=host, port=int(port), db=int(db))
        return conn

    def process_db(self, conn, prefix, check_memuse, instance_id):
        keys = conn.keys("{}*".format(prefix))

        for key in keys:
            size = 0
            key_type = conn.type(key).decode('utf-8')

            if (key_type == 'list'):
                size = conn.llen(key)
                self.queue_size.labels(instance_id, key.decode('utf-8')).set(size)

            if (key_type == 'zset'):
                size = conn.zcard(key)
                self.queue_size.labels(instance_id, key.decode('utf-8')).set(size)

            if (key_type == 'set'):
                size = conn.scard(key)
                self.queue_size.labels(instance_id, key.decode('utf-8')).set(size)

            if not check_memuse:
                return
            try:
                memused = conn.memory_usage(key)
                self.mem_use.labels(instance_id, key.decode('utf-8')).set(memused)
            except:
                pass