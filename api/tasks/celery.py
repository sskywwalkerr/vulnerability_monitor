from celery import Celery

from api.config import Config

celery = Celery(
    'tasks',
    broker=f'redis://{Config.REDIS_HOST}:{Config.REDIS_PORT}',
    include=['api.tasks.tasks']
)
