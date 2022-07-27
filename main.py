import sys
from datetime import datetime, timedelta

from fotogo_networking.endpoints import app


def main():
    app.start()


if __name__ == '__main__':
    main()
