
import stackless
import random

turns = 10

class HackySacker(object):
    counter = 0
    exit_message = 'exit'
    def __init__(self, name, circle):
        self.channel = stackless.channel()
        self.name = name
        circle.append(self)
        self.circle = circle

        stackless.tasklet(self.message_loop)()

    def increment_counter(self):
        HackySacker.counter += 1
        if HackySacker.counter >= turns:
            while self.circle:
                self.circle.pop().channel.send(HackySacker.exit_message)

    def message_loop(self):
        while True:
            message = self.channel.receive()
            if message == HackySacker.exit_message:
                return
            kick_to = self.random_next()
            print("{} kicking hackysack to {}".format(self.name, kick_to.name))
            self.increment_counter()
            kick_to.channel.send(self)

    def random_next(self):
        kick_to = self.circle[random.randint(0, len(self.circle) - 1)]
        while kick_to is self:
            kick_to = self.circle[random.randint(0, len(self.circle) - 1)]
        return kick_to


def run_it(hs = 5):
    circle = []
    hackysackers = [HackySacker(str(i), circle) for i in range(hs)]
    hackysackers[0].channel.send(hackysackers[0])

    try:
        stackless.run()
    except stackless.TaskletExit:
        pass


if __name__ == "__main__":
    run_it()

