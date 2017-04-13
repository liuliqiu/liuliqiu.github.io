
import greenlet

def generator(n):
    assert (yield 0) == 123
    yield n

def test_generator():
    coroutine = generator(3)
    assert coroutine.next() == 0
    assert coroutine.send(123) == 3


def coroutine(n):
    assert greenlet.getcurrent().parent.switch(0) == 123
    greenlet.getcurrent().parent.switch(n)

def test_coroutine():
    gr = greenlet.greenlet(coroutine)
    assert gr.switch(3) == 0
    assert gr.switch(123) == 3

if __name__ == "__main__":
    test_generator()
    test_coroutine()

