
def grep(cond):
    def grep_impl(inp, outp):
        for value in inp:
            if cond(value):
                outp(value)
    return grep_impl


def transform(func):
    def transform_impl(inp, outp):
        for value in inp:
            outp(func(value))
    return transform_impl


def sink_to_file(f, separator="\n"):
    def sink_to_file_impl(inp, outp):
        for value in inp:
            f.write("%s%s" % (value, separator))
    return sink_to_file_impl
