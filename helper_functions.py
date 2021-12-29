def check_error(response: dict) -> bool:
    if 'error' in response.keys():
        return True
    return False

def make_table():
    pass

def ms_time_conversion(time : int) -> str:
# Convert time from ms into H:M:S str
    pass

def split_list(lst : list, n : int) -> list:
    # Split list into n lenghted segments
    n = max(1, n)
    return [lst[i:i+n] for i in range(0, len(lst), n)]
