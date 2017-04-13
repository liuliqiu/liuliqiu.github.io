
import greenlet


def ping():
    while True:
        print("ping")
        gr_pong.switch()


def pong():
    while True:
        print("pong")
        gr_ping.switch()

gr_ping = greenlet.greenlet(ping)
gr_pong = greenlet.greenlet(pong)

gr_ping.switch()
