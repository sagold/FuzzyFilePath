import re
import sublime

from FuzzyFilePath.common.verbose import verbose

def get_line_at_cursor(view):
    selection = view.sel()[0]
    position = selection.begin()
    region = view.line(position)
    line = view.substr(region)
    verbose("view", "line at cursor", line)
    return [line, region]

def get_path_at_cursor(view):
    pre = ""
    post = ""
    selection = view.sel()[0]
    position = selection.begin()

    # get regions
    word_region = view.word(position)
    line_region = view.line(position)
    final_region = view.line(position)
    line = view.substr(line_region)
    line_to = view.substr(line_region)

    """ get path start """
    line_region.b = word_region.b
    line_to = view.substr(line_region)
    print("line", line, "line to", line_to)
    # line_to = re.escape(line_to)
    path_start = re.match(".*[\s\"\'\(]([$.A-Za-z0-9/]*$)", line_to)
    if path_start and path_start.group(1):
        pre = path_start.group(1)
        print("path start: '", pre, "'")

    line_to = re.sub(re.escape(pre) + "$", "", line_to)
    final_region.a += len(line_to)

    """ get path end """
    line_region = view.line(position)
    line_region.a = word_region.b
    line_from = view.substr(line_region)
    print("line from current word", line_from)

    path_end = re.match("^([$.A-Za-z0-9/]*)", line_from)
    if path_end and path_end.group(1):
        post = path_end.group(1)
        print("path start: '", post, "'")

    # line_from = re.sub("^" + re.escape(post), "", line_from)
    # final_region.b -= len(line_to)


    full_path = pre + post
    print("final path: '", full_path ,"'")

    """region in path"""
    final_region.b = final_region.a + len(full_path)
    print("final path by region: '", view.substr(final_region) ,"'")

    return [full_path, final_region]


def _get_path_at_cursor(view):
    word = get_word_at_cursor(view)
    line = get_line_at_cursor(view)
    path = get_path(line[0], word[0])
    path_region = sublime.Region(word[1].a, word[1].b)
    path_region.b = word[1].b
    path_region.a = word[1].a - (len(path) - len(word[0]))
    verbose("view", "path_at_cursor", path, "word:", word, "line", line)
    return [path, path_region]

# tested
def get_word_at_cursor(view):
    selection = view.sel()[0]
    position = selection.begin()
    region = view.word(position)
    region.a -= 1
    word = view.substr(region)
    # validate
    valid = not re.sub("[\"\'\s\(\)]*", "", word).strip() == ""
    if not valid:
        verbose("view", "invalid word", word)
        return ["", sublime.Region(position, position)]
    # single line only
    if "\n" in word:
        return ["", sublime.Region(position, position)]
    # strip quotes
    if len(word) > 0:
        if word[0] is '"':
            word = word[1:]
            region.a += 1

        if word[-1:] is '"':
            word = word[1:]
            region.a += 1
    # cleanup in case an empty string is encounterd
    if word.find("''") != -1 or word.find('""') != -1 or word.isspace():
        word = ""
        region = sublime.Region(position, position)

    return [word, region]

# tested
def get_path(line, word):
    last_match = None

    #! returns last match
    if word is None or word is "":
        return word

    needle = re.escape(word)
    full_words = line.split(" ")

    for full_word in full_words:
        if word in line:
            path = extract_path_from(full_word, needle)
            if not path is None:
                last_match = path

    if last_match is None:
        return word
    else:
        return last_match

#! fails if needle occurs also before path (line)
def extract_path_from(word, needle):
   result = re.search('([^\"\'\s]*)' + needle + '([^\"\'\s]*)', word)
   if (result is not None):
       return result.group(0)
   return None
