#!/usr/bin/env python3
import logging

from config import ConfigManager
from layout import LayoutManager

from utils import init_logger
from utils import parse_args

args = parse_args()
init_logger(args.verbose)
logger = logging.getLogger('Main')

cm = ConfigManager()
lm = LayoutManager(cm)