
import stackless

ping_channel = stackless.channel()
pong_channel = stackless.channel()

def ping():
    while ping_channel.receive():
        print("ping")
        pong_channel.send("from ping")

def pong():
    while pong_channel.receive():
        print("pong")
        ping_channel.send("from pong")

stackless.tasklet(ping)()
stackless.tasklet(pong)()
stackless.tasklet(ping_channel.send)("startup")

stackless.run()

