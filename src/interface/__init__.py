# -*- coding: utf-8 -*-

import os
import ConfigParser


settings = ConfigParser.SafeConfigParser()
settings.read(os.path.join("..", "settings.conf"))