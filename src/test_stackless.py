import _continuation
import pickle

def copy(data):
    return pickle.loads(pickle.dumps(data))

def f(cont):
    print "begin"
    cont.switch()
    print "end"

task = _continuation.continulet(f)
task.switch()
task2 = copy(task)
task.switch()
task2.switch()

