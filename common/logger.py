import logging
import os


__handlers = []
if "APPLICATIONINSIGHTS_CONNECTION_STRING" in os.environ:
    from opencensus.ext.azure.log_exporter import AzureLogHandler
    __handlers.append(AzureLogHandler())

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s [%(levelname)s]::%(name)s: %(message)s',
                    datefmt="%Y-%m-%d %H:%M:%S",
                    handlers=__handlers)


def get_logger(name: str):
    logger = logging.getLogger(name)
    return logger
