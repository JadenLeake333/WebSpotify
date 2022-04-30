def create_navbar():
  import re
  import json

  endpoints = {
  "Home": "/home",
  "Search": "/search",
  "View Playlists": "/playlists",
  "Logout": "/logout"
  }

  navbar = '<header> <nav class="nav nav-masthead float-md-end">'

  for nav in endpoints.keys():
    navbar += '<a class="nav-link fs-2" href="%s">%s</a>' %(endpoints[nav], nav)

  navbar += '</nav></header>'

  searchbar = '<div class="mb-3"><form onsubmit="makeSearch(); return false;"><input placeholder="Search Spotify for a song or playlist!" type="text" id="search" class="w-75" aria-describedby="button-addon2"><button class="btn btn-outline-secondary" type="button" id="button-addon2" onclick="makeSearch()">Search</button></form></div>'
  return navbar, searchbar

