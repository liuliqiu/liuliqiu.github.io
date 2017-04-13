
import greenlet

def foo():
    print("foo")
    greenlet.getcurrent().parent.switch("return1")
    greenlet.getcurrent().parent.switch("return2")
    print("foo2")

if __name__ == "__main__":
    gr = greenlet.greenlet(foo)
    print(gr.switch())
    print(gr.switch())
    print(gr.switch())

