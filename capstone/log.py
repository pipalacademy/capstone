import logging

def setup_logger(verbose=False, format="long"):
    """Setup logger to print the logs to stdout.
    By default, the logging level is set to INFO. If the verbose is True,
    then the logging level is set to DEBUG.
    The format specifies how the log message is formatted. There are two
    supported formats.
    short:
        [HH:MM:SS] message
    long:
        YYYY-MM-DD HH:MM:SS logger-name [INFO] message
    By default the short format is used.
    """
    level = logging.DEBUG if verbose else logging.INFO

    FORMATS = {
        'short': '[%(asctime)s] %(message)s',
        'long': '%(asctime)s %(name)s [%(levelname)s] %(message)s'
    }
    DATE_FORMATS = {
        'short': '%H:%M:%S',
        'long': '%Y-%d-%m %H:%M:%S'
    }
    logging.basicConfig(
        level=level,
        format=FORMATS[format],
        datefmt=DATE_FORMATS[format])

