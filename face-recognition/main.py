import json
import logging
import requests

# Set up a logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    logger.info(event)