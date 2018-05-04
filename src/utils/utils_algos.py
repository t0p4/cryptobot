def binary_search(needle, haystack):
    num_hay = len(haystack)
    idx = num_hay / 2
    if close_enough(haystack[idx], needle):
        return True, haystack[idx], idx
    elif haystack[idx] < needle:
        found, found_value, found_idx = binary_search(needle, haystack[:idx])
        return found, found_value, found_idx
    else:
        found, found_value, found_idx = binary_search(needle, haystack[idx+1:])
        return found, found_value, found_idx + idx + 1


def binary_insert(needle, haystack):
    haystack_copy = haystack[:]
    found, found_value, found_idx = binary_search(needle, haystack_copy)
    if needle > found_value:
        return haystack[:found_idx+1].concat([needle]).concat(haystack[found_idx:])
    elif needle < found_value:
        return haystack[:found_idx].concat([needle]).concat(haystack[found_idx+1:])
    else:
        return haystack


def close_enough(time_1, time_2):
    return abs(time_1 - time_2) <= 60000
