import multiprocessing

from backend.server.app import APP_CONFIG
from backend.server.config import DebugConfig

wsgi_app = "backend.server.app:app"
proc_name = "GymStats"

bind = "0.0.0.0:3003"
workers = multiprocessing.cpu_count() * 2 + 1
# workers = 2
threads = 2

# Debug Config
if isinstance(APP_CONFIG, DebugConfig):
    reload = True
else:
    reload = False
