import logging
import structlog


def configure_logging():

    structlog.configure(
        processors=[
            structlog.processors.JSONRenderer()
        ]
    )

    logging.basicConfig(
        level=logging.INFO
    )

    return structlog.get_logger()


logger = configure_logging()