import bpm_subscriber
import step_subscriber
import lock
import GUIscreen

from threading import Thread

th1 = Thread(target=bpm_subscriber.main)
th2 = Thread(target=step_subscriber.main)
th3 = Thread(target=lock.main)
th4 = Thread(target=GUIscreen.main)

th1.start()
th2.start()
th3.start()
th4.start()

th1.join()
th2.join()
th3.join()
th4.join()