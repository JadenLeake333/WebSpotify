const makeSearch = () =>{
    var text = document.querySelector("#search").value
    if(text.search('open.') != -1 && text.search('track/') != -1){
        text = parseURL(text,true)
    }else if(text.search('open.') != -1 && text.search('playlist/') != -1){
        text = parseURL(text,false)
    }
    
    if(text.search('spotify:') != -1 && text.search('track:') != -1){
        window.location.href = "/searchtrack?track="+text
    }else if(text.search('spotify:') != -1 && text.search('playlist:') != -1){
        window.location.href = "/playlistdata?playlist="+text
    }else{
        window.location.href = "/search?s="+text
    } 
}

const parseURL = (url,track) =>{ // Temporary function to convert spotify urls into uris. // Track will be a flag indicating whether it is a track or not
    if(track){
        index = url.search('track/')
        url = "spotify:track:"+url.substring(index+6,url.length) // index+6 is length of "track/"
        return url
    }else{
        index = url.search('playlist/')
        url = "spotify:playlist:"+url.substring(index+9,url.length) // index+9 is length of "playlist/"
        return url
    }
}

