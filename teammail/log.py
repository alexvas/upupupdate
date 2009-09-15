# -*- coding: utf-8 -*-
import os, logging

current_dir = os.path.abspath(os.path.dirname(__file__))
logging.config.fileConfig(os.path.join(current_dir, "logging.conf"))
logger = logging.getLogger("traceLogger")
