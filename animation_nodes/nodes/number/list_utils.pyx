from ... data_structures cimport (
    DoubleList,
    LongLongList
)

from ... utils.clamp cimport clampLong

def clampDoubleList(DoubleList values, double minValue, double maxValue):
    cdef Py_ssize_t i
    for i in range(len(values)):
        if values.data[i] < minValue:
            values.data[i] = minValue
        elif values.data[i] > maxValue:
            values.data[i] = maxValue

def range_LongLongList_StartStep(amount, start, step):
    cdef long long _amount = clampLong(amount)
    cdef long long _start = clampLong(start)
    cdef long long _step = clampLong(step)

    cdef LongLongList newList = LongLongList(length = max(_amount, 0))
    cdef Py_ssize_t i
    for i in range(len(newList)):
        newList.data[i] = _start + i * _step
    return newList

def range_DoubleList_StartStep(amount, double start, double step):
    cdef DoubleList newList
    cdef Py_ssize_t i
    if step == 0:
        newList = DoubleList.fromValues([start]) * max(amount, 0)
    else:
        newList = DoubleList(length = max(amount, 0))
        for i in range(len(newList)):
            newList.data[i] = start + i * step
    return newList

def range_DoubleList_StartStop(Py_ssize_t amount, double start, double stop):
    if amount == 1:
        return DoubleList.fromValues([start])
    else:
        return range_DoubleList_StartStep(amount, start, (stop - start) / (amount - 1))