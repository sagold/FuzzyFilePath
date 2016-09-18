def get_diff(first, second):
    # get intersection at start
    start = get_start_diff(first, second)

    # remove intersection to prevent end diff duplicates
    first = first[len(start):]
    second = second[len(start):]
    end = get_end_diff(first, second)

    return {
        "start": start,
        "end": end
    }

def get_start_diff(first, second):
    index = 0
    result = ""
    for c in first:
        if c is second[index]:
            index += 1
            result += c
        else:
            break

    return result

def get_end_diff(first, second):
    first = first[::-1]
    second = second[::-1]
    index = 0
    result = ""
    for c in first:
        if index in second and c is second[index]:
            index += 1
            result = c + result
        else:
            break

    return result
