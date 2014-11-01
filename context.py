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
    #! returns first match
    if word is None or word is "":
        return word

    needle = re.escape(word)
    full_words = line.split(" ")
    for full_word in full_words:
        if word in line:
            path = extract_path_from(full_word, needle)
            if not path is None:
                return path

    return word

#! fails if needle occurs also before path (line)
def extract_path_from(word, needle):
   result = re.search('([^\"\'\s]*)' + needle + '([^\"\'\s]*)', word)
   if (result is not None):
       return result.group(0)
   return None