def f():
    yield 1
    for i in [2, 3]:
        yield i * i

gen = f()
frame = gen.gi_frame
for v in gen:
    print("val: {}, lineno:{}, locals:{}".format(v, frame.f_lineno, frame.f_locals))
    # gi_frame 就是函数的栈帧，f_lineno 表示当前栈帧执行到的行数，f_locals是局域变量。
