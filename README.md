# Metrics Scrapper

Generic metric scrapper for commonly used resources where we don't usualy have metrics for.

All metrics will contain the PROMETHEUS_NAMESPACE prefix for them.

## Configuring

The following ENV are required to run this project:

* **PROMETHEUS_CONFIG**: JSON with the following fields
  * namespace: The namespace to be used by the Prometheus library
* **JOBS_CONFIG**: JSON with the desired configuration for each scrapper

### Example:

```json
PROMETHEUS_CONFIG={
    "namespace": "sample"
}

JOBS_CONFIG={
    "redis_queue": [
        {
            "id": "main-db",
            "host": "127.0.0.1",
            "port": 6379,
            "db": 0
        },
        {
            "id": "replica-db",
            "host": "127.0.0.1",
            "port": 6379,
            "db": 2,
            "prefix": "my-prefix", // Optional (defaults to "queue")
            "check_mem": false     // Optional (defaults to false)
        }
    ],
    "humancoder": [
        {
            "id": "main-account",
            "key": "MY-SECRET-KEY"
        }
    ]
}
```

## Redis Queue

Provides access to queue size keys in a Redis instance. Usually when using Redis as queue from Laravel or other framework, we don't have easy and automatic access to each queue size and how much memory it is using. This scrapper provides both of this information for each configured instance (host + db) and a key prefix.

### Metrics

* **redis_queue_size**: Prometheus gauge with number o elements in determined key. Also provides labels with instanceId and key name
* **redis_queue_memuse**: Prometheus gauge with current allocated memory for the key. Also provides labels with instanceId and key name

## HumanCoder Balance

Provides access to current account balance for each KEY.

### Metrics

* **humancoder_balance**: Prometheus gauge with remaining balance
