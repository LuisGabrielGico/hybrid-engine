import threading
from database.db import init_db
from automation.scheduler import start_scheduler
from dashboard.app import Dashboard

if __name__=="__main__":
    init_db()

    scheduler_thread=threading.Thread(
        target=start_scheduler,
        daemon=True
    )
    scheduler_thread.start()

    Dashboard().run()
