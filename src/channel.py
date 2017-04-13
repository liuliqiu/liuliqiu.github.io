import stackless

def producer(ch):
    for i in range(3):
        print "send", i
        ch.send(i)

def consumer(ch):
    while True:
        i = ch.receive()
        print "receive", i

ch = stackless.channel()
stackless.tasklet(consumer)(ch)
stackless.tasklet(producer)(ch)
stackless.run()


