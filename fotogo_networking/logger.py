import logging
from datetime import datetime
from colorama import Fore, Back


class Logger:
    """
    Creates a logger that logs messages to the console and to a .log file.

    It is possible to create multiple loggers, each one with a unique name.
    """

    def __init__(self, name: str = None, filename: str = '', level=logging.INFO):
        """
        Creates a logger with provided name and .log file path.

        :param name: The name of the logger. Creating multiple loggers with the same name will return the same logger.
        :param filename: Path to a log file where the logger will output into. If a file with the same name already
        exists, it will append to it.s
        """
        if filename == '':
            filename = f"logs/{name} logs - {str(datetime.now()).split(' ')[0]}.log"

        self._logger = logging.getLogger(name)

        if not self._logger.hasHandlers():
            self._handler = logging.FileHandler(filename)
            self._formatter = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s")
            self._handler.setFormatter(self._formatter)

            self._logger.addHandler(self._handler)
            self._logger.setLevel(level)

    @staticmethod
    def __get_time_formatted() -> str:
        """Returns the current time, formatted with the date and hour, accurate by milliseconds."""
        return datetime.now().strftime('%d/%m/%y %H:%M:%S.%f')

    def __message_format(self, message: str, level: str) -> str:
        """The message format for all levels."""
        return f"[{Logger.__get_time_formatted()}] {self._logger.name} | {level}: {message}"

    def debug(self, message):
        """
        Debugs a message to the console and the log file at the "debug" level, unless level is set to above debug.

        :param message: The message to log.
        """
        self._logger.debug(message)
        print(Fore.WHITE + self.__message_format(message, "Debug") + Fore.RESET)

    def info(self, message, color=Fore.GREEN):
        """
        Debugs a message to the console and the log file at the "info" level, unless level is set to above info.

        :param color: The color in which the message will be printed to the console. Default to green.
        :param message: The message to log.
        """
        self._logger.info(message)
        print(color + self.__message_format(message, "Info") + Fore.RESET)

    def error(self, message):
        """
        Debugs a message to the console and the log file at the "error" level, unless level is set to above error.

        :param message: The message to log.
        """
        self._logger.error(message)
        print(Fore.RED + self.__message_format(message, "Error") + Fore.RESET)

    def critical(self, message):
        """
        Debugs a message to the console and the log file at the "critical" level, unless level is set to above critical.

        :param message: The message to log.
        """
        self._logger.critical(message)
        print(Fore.LIGHTWHITE_EX + Back.RED + self.__message_format(message, "CRITICAL") + Fore.RESET + Back.RESET)

    def exception(self, message):
        """
        Used for logging errors with exception information.

        :param message: The message to log.
        """
        self._logger.exception(message)
