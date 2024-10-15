wsgi_app = "backend.server.app:app"
proc_name = "GymStats"

bind = "127.0.0.1:3003"
workers = 2
threads = 4

# Debug Config
reload = True
