"""Demo: functions anchored with @anchor.test / @anchor.idk (Level 2-4)."""

from anchorlaw import test as pt, i_dont_know as idk


@pt("空列表返回空",
    lambda: process([]) == [],
    source="trace:demo#001, input=[] output=[] observed 2026-08-12")
@pt("保留正数",
    lambda: process([-1, 0, 3, -5]) == [3],
    source="trace:demo#002, input=[-1,0,3,-5] output=[3] observed 2026-08-12")
@idk("超大列表（>1M）的行为边界尚未确定",
    source="static: 未在 trace 中覆盖大输入")
def process(data):
    return [x for x in data if x > 0]
