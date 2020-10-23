from django.shortcuts import get_object_or_404, render
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from .choices import price_choices, bedroom_choices, state_choices
from json import dumps

import json
import re
from html.parser import HTMLParser
from urllib.parse import (
    parse_qsl, quote, unquote, urlencode, urlsplit, urlunsplit,
)

from django.utils.functional import Promise, keep_lazy, keep_lazy_text
from django.utils.http import RFC3986_GENDELIMS, RFC3986_SUBDELIMS
from django.utils.safestring import SafeData, SafeText, mark_safe
from django.utils.text import normalize_newlines
from django.utils.html import (
    avoid_wrapping, conditional_escape, escape, escapejs,
    json_script as _json_script, linebreaks, strip_tags, urlize as _urlize,
)

from .models import Listing

def index(request):
  listings = Listing.objects.order_by('-list_date').filter(is_published=True)
  
  # for listing in listings:
  #   print(listing.longitude)

  paginator = Paginator(listings, 6)
  page = request.GET.get('page')
  paged_listings = paginator.get_page(page)

  geolocations= list(Listing.objects.values_list( 'title','latitude','longitude'))
  print( 'GEOLOCATIONS!!!',geolocations)
  
  context = {
    'listings': paged_listings,
    # Here, we apply `json.dumps`, `escapejs` and `marksafe` for security
    # and proper formatting
    'geolocations': mark_safe(escapejs(json.dumps(geolocations)))
    
  }
  return render(request, 'listings/listings.html', context)

def listing(request, listing_id):
  listing = get_object_or_404(Listing, pk=listing_id)
  # print(listing.longitude)
  
  
  context = {
    'listing': listing,
    'lon': listing.longitude,
    'lat': listing.latitude,
    'title':listing.title

  }

  return render(request, 'listings/listing.html', context)


def search(request):
  queryset_list = Listing.objects.order_by('-list_date')

  # Keywords
  if 'keywords' in request.GET:
    keywords = request.GET['keywords']
    if keywords:
      queryset_list = queryset_list.filter(description__icontains=keywords)

  # City
  if 'city' in request.GET:
    city = request.GET['city']
    if city:
      queryset_list = queryset_list.filter(city__iexact=city)

  # State
  if 'state' in request.GET:
    state = request.GET['state']
    if state:
      queryset_list = queryset_list.filter(state__iexact=state)

  # Bedrooms
  if 'bedrooms' in request.GET:
    bedrooms = request.GET['bedrooms']
    if bedrooms:
      queryset_list = queryset_list.filter(bedrooms__lte=bedrooms)

  # Price
  if 'price' in request.GET:
    price = request.GET['price']
    if price:
      queryset_list = queryset_list.filter(price__lte=price)

  context = {
    'state_choices': state_choices,
    'bedroom_choices': bedroom_choices,
    'price_choices': price_choices,
    'listings': queryset_list,
    'values': request.GET
  }

  return render(request, 'listings/search.html', context)
