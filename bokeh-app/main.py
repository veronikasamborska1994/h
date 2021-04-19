import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib import cm
import geopandas as gpd
import json
from datetime import date
import datetime as dt
from bokeh.io import output_notebook, show, output_file
from bokeh.plotting import figure
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar, NumeralTickFormatter
from bokeh.palettes import brewer

from bokeh.io.doc import curdoc
from bokeh.models import Slider, HoverTool, Select, Label
from bokeh.layouts import widgetbox, row, column
from bokeh.models import Div, Column, CustomJS

# read in population data

from os import listdir
from os.path import isfile, join

gdata = gpd.read_file('https://raw.githubusercontent.com/veronikasamborska1994/GNI-Fellowship-at-The-Guardian/master/data/eer.geojson')

#mypath = '/Users/veronikasamborska/Desktop/project_beds/'
#onlyfiles = [f for f in listdir(mypath) if (isfile(join(mypath, f)) and ('.xlsx' in f ))]

area_year = []
ward_year = []
year_all = []
area_ns = []


mypath = ['https://raw.githubusercontent.com/veronikasamborska1994/GNI-Fellowship-at-The-Guardian/master/data/2020-03-01.xlsx',
          'https://raw.githubusercontent.com/veronikasamborska1994/GNI-Fellowship-at-The-Guardian/master/data/2020-06-01.xlsx', 
          'https://raw.githubusercontent.com/veronikasamborska1994/GNI-Fellowship-at-The-Guardian/master/data/2020-12-01.xlsx', 
          'https://raw.githubusercontent.com/veronikasamborska1994/GNI-Fellowship-at-The-Guardian/master/data/2020-09-01.xlsx',
          'https://raw.githubusercontent.com/veronikasamborska1994/GNI-Fellowship-at-The-Guardian/master/data/2019-12-01.xlsx', 
          'https://raw.githubusercontent.com/veronikasamborska1994/GNI-Fellowship-at-The-Guardian/master/data/2019-09-01.xlsx',
          'https://raw.githubusercontent.com/veronikasamborska1994/GNI-Fellowship-at-The-Guardian/master/data/2019-06-01.xlsx']




for file in mypath:
    df = pd.read_excel(file) 
    area_codes = ['Y56','Y58','Y59','Y60','Y61','Y62','Y63']

    data = []
    for code in area_codes:
        data.append(df['Unnamed: 3']== code)
        
    mental_health = df['Unnamed: 22']
    maternity = df['Unnamed: 21']
    learning_dis =  df['Unnamed: 20']
    general_acute =  df['Unnamed: 19']
    total =  df['Unnamed: 18']
    all_wards = [total,mental_health,maternity,learning_dis,general_acute]
    all_wards_names = ['total','mental_health','maternity','learning_dis','general_acute']
    area_ns.append(['London','South West','South East','Midlands','Eastern','North West','North East'])
    
    year_all.append([file[-15:-5],file[-15:-5], file[-15:-5], file[-15:-5],file[-15:-5],file[-15:-5], file[-15:-5]])
    
    #wards in all areas
    ward_list = []
    for w,ward in enumerate(all_wards):
        area_list = []
        for dd,d in enumerate(data):
            health = np.asarray(ward[d])
            condition = np.where(health != '-')
            mean = np.mean(health[condition])
            area_list.append(np.round(mean*100))
        ward_list.append(area_list)
    ward_year.append(ward_list)
    
wards = np.array([np.asarray(ward_year)[:,0].flatten(),\
                                    np.asarray(ward_year)[:,1].flatten(),\
                                    np.asarray(ward_year)[:,2].flatten(),\
                                    np.asarray(ward_year)[:,3].flatten(),\
                                    np.asarray(ward_year)[:,4].flatten()])
data_frame = pd.DataFrame(np.asarray([wards[0],wards[1],wards[2],wards[3],wards[4],
                           np.asarray(year_all).flatten(),np.asarray(area_ns).flatten()]).T,\
columns = ['total','mental_health','maternity','learning_dis','general_acute','year', 'area'])




def json_data(selectedar):
    
    # Pull selected year from neighborhood summary data
    df_ar = data_frame[data_frame['year'] == selectedar]
    # Merge the GeoDataframe object (sf) with the neighborhood summary data (neighborhood)
    merged = gdata.merge(df_ar, left_on = 'EER13NM', right_on = 'area')
    
    # Fill the null values
    #Read data to json.
    merged_json = json.loads(merged.to_json())
    #Convert to String like object.
    json_data = json.dumps(merged_json)

    return json_data


# Define the callback function: update_plot
def update_plot(attr, old, new):
    # The input yr is the year selected from the slider
    yr = slider.value
    date = dates[yr]
    new_data = json_data(date)
    label.text = str(date)

    
    # The input cr is the criteria selected from the select box
    cr = select.value    
    # Update the plot based on the changed inputs
    p = make_plot(cr)
    p.add_layout(label)

    
    # Update the layout, clear the old document and display the new document
    layout = column(p, widgetbox(slider), widgetbox(select))
    curdoc().clear()
    curdoc().add_root(layout)
    
    # Update the data
    geosource.geojson = new_data
    
    

def make_plot(ward_name):    
  # Set the format of the colorbar
  min_range = float(data_frame[ward_name].min())
  max_range = float(data_frame[ward_name].max())
  
    
  # Instantiate LinearColorMapper that linearly maps numbers in a range, into a sequence of colors.
  colormap = cm.get_cmap("BuPu")
  bokehpalette = [mpl.colors.rgb2hex(m) for m in colormap(np.arange(colormap.N))][::10]
  color_mapper = LinearColorMapper(palette=bokehpalette, low=min_range, high=max_range)

  # Create color bar.
  #format_tick = NumeralTickFormatter(format='0.0%')
  color_bar = ColorBar(color_mapper=color_mapper, label_standoff=18, 
  border_line_color=None, location = (0, 0))

  # Create figure object.

  p = figure(title = str(ward_name) + ' occupied', 
             plot_height = 600, plot_width = 400,
             toolbar_location = None)
  p.xgrid.grid_line_color = None
  p.ygrid.grid_line_color = None
  p.axis.visible = False

  # Add patch renderer to figure. 
  p.patches('xs','ys', source = geosource, fill_color = {'field' : ward_name, 'transform' : color_mapper},
          line_color = 'black', line_width = 0.25, fill_alpha = 1)
  
  # Specify color bar layout.
  p.add_layout(color_bar, 'below')
  # Add the hover tool to the graph
  p.add_tools(hover)

    
  return p
    
geosource = GeoJSONDataSource(geojson = json_data('2019-06-01'))


# Input geojson source that contains features for plotting for:
# initial year 2018 and initial criteria sale_price_median
ward_name = 'total'
all_wards_names = ['total','mental_health','maternity','learning_dis','general_acute']

# Define a sequential multi-hue color palette.
palette = brewer['Blues'][8]

# Reverse color order so that dark blue is highest obesity.
palette = palette[::-1]

# Add hover tool
hover = HoverTool(tooltips = [('% Total', '@total'),  
                              ('% Mental Health', '@mental_health'),
                              ('% Maternity', '@maternity'),
                              ('% Learning Disabilities', '@learning_dis'),
                              ('% General Acute', '@general_acute'),
                               ('Region', '@area')])


# Call the plotting function
p = make_plot(ward_name)

dates = np.unique(year_all)
number_dates = np.arange(len(dates))
slider = Slider(title = 'Quarter',start = number_dates[0], end = number_dates[-1], step = 1, value = number_dates[0])
label = Label(x = -0.9, y = 55, text=str(dates[0]), text_font_size='20px')
slider.on_change('value',update_plot)
p.add_layout(label)

# Make a selection object: select
select = Select(title='Select Ward:', value = 'total', options= ['total','mental_health','maternity','learning_dis','general_acute'])
select.on_change('value', update_plot)

# Make a column layout of widgetbox(slider) and plot, and add it to the current document
# Display the current document
layout = column(p, widgetbox(slider), widgetbox(select))
curdoc().add_root(layout)

# Use the following code to test in a notebook, comment out for transfer to live site
# Interactive features will not show in notebook
#output_notebook()
show(p)
