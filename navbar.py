import re
import json

def create_navbar():
  navbar = '<header> <nav class="nav nav-masthead float-md-end">'

  with open ('endpoints.json') as uris:
    endpoints = json.loads(uris.read())

    for nav in endpoints.keys():
      navbar += '<a class="nav-link fs-2" href="%s">%s</a>' %(endpoints[nav], nav)

  navbar += '</nav><div class="input-group mb-3"><input type="text" id="search" class="form-control" aria-describedby="button-addon2"><button class="btn btn-outline-secondary" type="button" id="button-addon2" onclick="makeSearch()">Search</button></div></header>'
  return navbar

