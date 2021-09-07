import re
import json

def create_navbar():
  navbar = '<header class="mb-auto"> <nav class="nav nav-masthead justify-content-center float-md-end">'

  with open ('endpoints.json') as uris:
    endpoints = json.loads(uris.read())

    for nav in endpoints.keys():
      remove_ = re.sub(r"\_"," ", nav)
      navbar += '<a class="nav-link fs-2" href="%s">%s</a>' %(endpoints[nav], remove_)

  navbar += '</nav></header>'
  return navbar

