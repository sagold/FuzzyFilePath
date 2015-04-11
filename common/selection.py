
def get_position(view):
    return view.sel()[0].begin()

def get_line(view):
    position = get_position(view)
    line_region = view.line(position)
    return view.substr(line_region)

def get_word(view):
    word_region = view.word(get_position(view))
    return view.substr(word_region)

def get_scope(view):
    return view.scope_name(get_position(view))
