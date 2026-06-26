import logging

from client.services.client import ClientService
from core.logging import configure_logging
from core.settings import settings


def main() -> None:
    configure_logging(log_file=settings.CLIENT_LOG_FILE)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    ClientService(settings).run()


if __name__ == "__main__":
    main()
