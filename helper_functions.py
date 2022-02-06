def check_error(response: dict) -> bool:
    if 'error' in response.keys():
        return True
    return False

def make_table():
    pass

# Convert time from ms into H:M:S str
def ms_time_conversion(time : int) -> str:
    import math
    seconds=math.floor((time/1000)%60)
    minutes=math.floor((time/(1000*60))%60)
    hours=math.floor((time/(1000*60*60))%24)
    return f"{str(hours) + 'h' if hours > 0 else ''}{str(minutes) + 'm' if minutes > 0 else ''}{str(seconds) + 's' if seconds > 0 else ''}"

# Split list into n lenghted segments
def split_list(lst : list, n : int) -> list:
    n = max(1, n)
    return [lst[i:i+n] for i in range(0, len(lst), n)]

# https://en.wikipedia.org/wiki/Pitch_class
# Will return Key of a song based on integer (0 = C, 1 = C♯, D♭ )
def pitch_class_conversion(pitch : int) -> str:
    if pitch == 0:
        return "C"
    if pitch == 1:
        return "C♯"
    if pitch == 2:
        return "D"
    if pitch == 3:
        return "D♯"
    if pitch == 4:
        return "E"
    if pitch == 5:
        return "F"
    if pitch == 6:
        return "F♯"
    if pitch == 7:
        return "G"
    if pitch == 8:
        return "G♯"
    if pitch == 9:
        return "A"
    if pitch == 10:
        return "A♯"
    if pitch == 11:
        return "B"