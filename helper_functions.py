def check_error(response: dict) -> bool:
    if 'error' in response.keys():
        return True
    return False

def make_table():
    pass

def ms_time_conversion(time : int) -> str:
    import math
# Convert time from ms into H:M:S str
    seconds=math.floor((time/1000)%60)
    minutes=math.floor((time/(1000*60))%60)
    hours=math.floor((time/(1000*60*60))%24)
    return f"{str(hours) + 'h' if hours > 0 else ''}{str(minutes) + 'm' if minutes > 0 else ''}{str(seconds) + 's' if seconds > 0 else ''}"

def split_list(lst : list, n : int) -> list:
    # Split list into n lenghted segments
    n = max(1, n)
    return [lst[i:i+n] for i in range(0, len(lst), n)]
