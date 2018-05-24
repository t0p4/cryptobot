def binary_search(needle, haystack):
    num_hay = len(haystack)
    if num_hay == 0:
        return False, None, 0
    if num_hay == 1:
        return True, haystack[0], 0

    idx = int(num_hay / 2)

    if num_hay > 0 and close_enough(haystack[idx], needle):
        return True, haystack[idx], idx
    elif num_hay > 0 and haystack[idx] < needle:
        found, found_value, found_idx = binary_search(needle, haystack[:idx])
        return found, found_value, found_idx
    else:
        found, found_value, found_idx = binary_search(needle, haystack[idx+1:])
        return found, found_value, found_idx + idx + 1


def binary_insert(needle, haystack):
    haystack_copy = haystack[:]
    if len(haystack) == 0:
        return [needle]
    found, found_value, found_idx = binary_search(needle, haystack_copy)
    if found_value is not None:
        if needle > found_value:
            return haystack[:found_idx+1] + [needle] + haystack[found_idx:]
        elif needle < found_value:
            return haystack[:found_idx] + [needle] + haystack[found_idx+1:]
        else:
            return haystack
    return haystack


def close_enough(time_1, time_2):
    return abs(time_1 - time_2) <= 60000
