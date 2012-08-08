
def grep(cond):
    """
    Emit only values for which ``cond(value)`` returns a true value, dropping
    all other values.
    """
    def grep_impl(inp, outp):
        for value in inp:
            if cond(value):
                outp(value)
    return grep_impl


def transform(func):
    """
    Evaluate ``func(value)`` for each value and emit the result.
    """
    def transform_impl(inp, outp):
        for value in inp:
            outp(func(value))
    return transform_impl


def uniq(cmp_func=None):
    """
    Drop any values that are equal to the previous value. If the input is
    a sorted list then this will remove all duplicates.

    If ``cmp_func`` is provided then it is called for each value to obtain
    the value that will be used for comparison. This allows comparison of
    only part of a value (for example, an id property) rather than of the
    whole value.
    """
    NOTHING_YET = object()
    if cmp_func is None:
        cmp_func = lambda x : x
    def uniq_impl(inp, outp):
        prev = NOTHING_YET
        for value in inp:
            current = cmp_func(value)
            if prev != current:
                outp(value)
                prev = current
    return uniq_impl


def aggregate(key_func, close_func):
    """
    Evaluate ``key_func(value)`` for each value and then accumulate a list of
    all values with a matching key until ``close_func(list)`` returns a true
    value, at which point the entire list will be emitted.

    It is the caller's responsibility to ensure that all sequences are closed.
    Unclosed sequences will remain in memory until the containing graph is
    terminated, at which point they will be discarded.
    """
    def aggregate_impl(inp, outp):
        aggrs = {}
        for value in inp:
            key = key_func(value)
            aggr = aggrs.get(key, None)
            if aggr is None:
                aggr = []
                aggrs[key] = aggr
            aggr.append(value)
            if close_func(aggr):
                outp(aggr)
                del aggrs[key]
    return aggregate_impl


def json_encode(**kwargs):
    """
    Pass all values to :py:func:`json.dumps` using the provided keyword
    arguments and emit the resulting strings.
    """
    from json import dumps
    def json_encode_impl(inp, outp):
        for value in inp:
            outp(dumps(value, **kwargs))
    return json_encode_impl


def json_decode(**kwargs):
    """
    Pass all values (which should be strings) to :py:func:`json.loads` using
    the provided keyword arguments and emit the resulting values.
    """
    from json import loads
    def json_decode_impl(inp, outp):
        for value in inp:
            outp(loads(value, **kwargs))
    return json_decode_impl


def sink_to_file(f, separator="\n"):
    def sink_to_file_impl(inp, outp):
        for value in inp:
            f.write("%s%s" % (value, separator))
    return sink_to_file_impl


def sink_to_callable(func):
    """
    Pass each value as a single positional argument into the provided callable
    ``func``. The return value, if any, is discarded.
    """
    def sink_to_callable_impl(inp, outp):
        for value in inp:
            func(value)
    return sink_to_callable_impl
