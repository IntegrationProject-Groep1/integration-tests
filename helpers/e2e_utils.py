"""E2E test utilities: lightweight RabbitMQ helpers and fixtures loader.

These helpers are intentionally small and dependency-light: they use pika
for AMQP operations and Path for fixtures. Tests should gate execution
behind an environment variable (RUN_E2E=1) so CI doesn't run them by
default unless infrastructure is available.
"""
from pathlib import Path
import os
import time
from typing import Optional

import pika

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES_DIR = REPO_ROOT / "integration-tests" / "fixtures"


def load_fixture(team: str, name: str) -> str:
    path = FIXTURES_DIR / team / name
    return path.read_text(encoding="utf-8")


def get_rabbit_params():
    host = os.getenv("RABBITMQ_HOST", "127.0.0.1")
    port = int(os.getenv("RABBITMQ_PORT", "5672"))
    user = os.getenv("RABBITMQ_USER", "guest")
    password = os.getenv("RABBITMQ_PASSWORD", "guest")
    creds = pika.PlainCredentials(user, password)
    params = pika.ConnectionParameters(host=host, port=port, credentials=creds)
    return params


def publish(exchange: str, routing_key: str, body: str) -> None:
    params = get_rabbit_params()
    conn = pika.BlockingConnection(params)
    ch = conn.channel()
    ch.exchange_declare(exchange=exchange, exchange_type="topic", durable=True)
    ch.basic_publish(exchange=exchange, routing_key=routing_key, body=body.encode("utf-8"), properties=pika.BasicProperties(content_type="application/xml", delivery_mode=2))
    conn.close()


def wait_for_message(exchange: str, routing_key: str, timeout: int = 10) -> Optional[str]:
    """Bind an exclusive temporary queue to the given exchange+routing_key and
    wait until a message is received or timeout. Returns message body or None.
    """
    params = get_rabbit_params()
    conn = pika.BlockingConnection(params)
    ch = conn.channel()
    ch.exchange_declare(exchange=exchange, exchange_type="topic", durable=True)

    result = ch.queue_declare(queue="", exclusive=True, auto_delete=True)
    tmp_q = result.method.queue
    ch.queue_bind(exchange=exchange, queue=tmp_q, routing_key=routing_key)

    body_container = {"body": None}

    def callback(_ch, method, properties, body):
        body_container["body"] = body.decode("utf-8")
        _ch.basic_ack(delivery_tag=method.delivery_tag)
        _ch.stop_consuming()

    ch.basic_consume(queue=tmp_q, on_message_callback=callback)

    start = time.time()
    try:
        while time.time() - start < timeout:
            ch._connection.process_data_events(time_limit=0.5)  # type: ignore[attr-defined]
            if body_container["body"] is not None:
                break
    finally:
        try:
            ch.queue_delete(queue=tmp_q)
        except Exception:
            pass
        conn.close()

    return body_container["body"]
