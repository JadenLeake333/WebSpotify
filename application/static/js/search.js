const makeSearch = () =>{
    var text = document.querySelector("#search").value

    if (text.search('/track/') != -1) {
        track_id = text.substring(text.search('/track/') + 7)
        window.location.href = "/features/" + track_id
    } else if (text.search('/playlist/') != -1) {
        playlist_id = text.substring(text.search('/playlist/') + 10)
        window.location.href = "/content/playlists/" + playlist_id
    } else {
        window.location.href = "/search?s="+text
    } 
}
