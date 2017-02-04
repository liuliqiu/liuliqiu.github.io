def f():
    x = yield 1
    yield x

def g():
    yield from f()
    x = yield 3
    return x

gen = g()

assert next(gen) == 1
assert gen.gi_frame.f_lineno == 6
assert gen.gi_yieldfrom.gi_frame.f_lineno == 2

assert gen.send(2) == 2
assert gen.gi_frame.f_lineno == 6
assert gen.gi_yieldfrom.gi_frame.f_lineno == 3

assert next(gen) == 3
assert gen.gi_frame.f_lineno == 7
assert gen.gi_yieldfrom is None

try:
    gen.send(4)
except StopIteration as e:
    assert e.value == 4
