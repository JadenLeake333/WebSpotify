def parse_song_analysis(data : dict) -> dict:
    danceability = [analysis['danceability'] for analysis in data['audio_features']]
    instrumentalness = [analysis['instrumentalness'] for analysis in data['audio_features']]
    valence = [analysis['valence'] for analysis in data['audio_features']]
    energy = [analysis['energy'] for analysis in data['audio_features']]
    return danceability, instrumentalness, valence, energy

def check_error(response: dict) -> bool:
    if 'error' in response.keys():
        return True
    return False

def make_table():
    pass