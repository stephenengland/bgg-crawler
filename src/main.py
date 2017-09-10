#!/usr/bin/python3

import logging
import configargparse
import sys
from crawler import crawl

# Configure loging
root = logging.getLogger()
root.setLevel(logging.INFO)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(message)s - %(name)s - %(levelname)s', "%m-%d %H:%M:%S")
ch.setFormatter(formatter)
root.addHandler(ch)

def main(log_level):
    level = logging.getLevelName(log_level)
    root.setLevel(level)
    ch.setLevel(level)
    crawl()

if __name__ == "__main__":
    parser = configargparse.ArgumentParser(description="Get data for config")
    parser.add_argument("--log_level", env_var="LOG_LEVEL", type=str, default="INFO", help="Logging Level")

    args = parser.parse_args()
    main(**args.__dict__)