class Error(Exception): pass
def f():
    x = 1
    x = yield x
    try:
        x = yield x
    except Error:
        print("generator error: Error")
        x = yield x + 1
    try:
        yield x
    except GeneratorExit:
        print("generator error: GeneratorExit")
        # generator 遇到 GeneraotrExit 时必须退出，否则 close 方法会抛出 RuntimeError。

gen = f()
# 第一次调用生成器必须用next，或者send(None)
assert gen.send(None) == 1
assert gen.gi_frame.f_lineno == 4

assert gen.send(12) == 12
assert gen.gi_frame.f_lineno == 6

assert gen.throw(Error) == 13   # generator error: Error
assert gen.gi_frame.f_lineno == 9

assert next(gen) is None
assert gen.gi_frame.f_lineno == 11

assert gen.close() == None      # generator error: GeneratorExit
assert gen.gi_frame is None
