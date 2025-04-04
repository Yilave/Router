from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from API.route_plotter import get_route
import plotly.express as px
import plotly.graph_objects as go
from plotly.offline import plot

# Create your views here.
def index(request):
    context = {}
    template = "index.html"
    try:
        if request.method == "POST":
            origin = request.POST['origin']
            destination = request.POST['dest']
            # Here we are getting the Python Dictionary
            data = get_route(origin, destination, response_type=None)
            # nodes = data['']
            df = data['data']
            longitude = data['lon']
            latitude = data['lat']
            
            # Plotting the route and coordinates on map
            fig = go.Figure()
            color_scale = [(0, 'red'), (1,'green')]
            fig = px.line_mapbox(df, 
                        lat="lat", 
                        lon="long", 
                        zoom=8, 
                        height=500,
                    width=900)
            

            fig.update_layout(
                mapbox_style="open-street-map",
                )
            fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
            
            for lon, lat in data['lon_lat']:
                fig.add_trace(go.Scattermapbox(mode="markers",
                    lon=[longitude[-1],lon],
                    lat=[latitude[-1], lat],
                    marker={
                        'size': 10,
                        "color": "green"
                    }
                ))
            map = plot(fig, output_type="div")
            # return map
            context['map'] = map
            context['distance'] = data['distance']
            context['gallons'] = data['gallons']
            context['average_price'] = data['average_price']
            context['total_cost'] = data['total_cost']
            context['origin'] = origin
            context['destination'] = destination

        return render(request, template, context)
    except:
        messages.error(request, "Coult not find places on Map. Please make sure you enter a valid location")
        return render(request, template)


# Api endpoint to return a Json data
@csrf_exempt
def get_route_api(request):
    if request.method == "POST":
        origin = request.GET.get('origin')
        destination = request.GET.get('destination')
        
        data = get_route(origin, destination, response_type="Json")

        return data
