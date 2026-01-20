# gunicorn.conf.py
import os

# Server socket
bind = "0.0.0.0:" + os.environ.get("PORT", "8000")

# Worker processes - ONLY 1 WORKER FOR RENDER FREE TIER
workers = 1  # Critical: Render free tier has limited memory
worker_class = "sync"
worker_connections = 1000
timeout = 120  # Increased timeout to prevent worker killing
keepalive = 5

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Process naming
proc_name = "sklearntrack_backend"

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# Worker process graceful timeout
graceful_timeout = 30

# Preload application code to save memory
preload_app = True

# Maximum requests per worker
max_requests = 1000
max_requests_jitter = 50

# Server hooks
def post_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def pre_fork(server, worker):
    pass

def pre_exec(server):
    server.log.info("Forked child, re-executing.")

def when_ready(server):
    server.log.info("✅ Server is ready. Spawning worker...")

def worker_int(worker):
    worker.log.info("Worker received INT or QUIT signal")

def worker_abort(worker):
    worker.log.info("Worker received SIGABRT signal")