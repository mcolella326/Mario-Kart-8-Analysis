import streamlit as st
import pandas as pd
from matplotlib import pyplot as plt
import itertools as it
import plotly.graph_objects as go

# Import data/set page characteristics
st.set_page_config(layout="wide")
data = pd.read_csv(r'~/PythonScripts/MK8/MK8Data.csv', index_col='Names').dropna()

# Remove all characters, karts, etc. that have exactly the same stats
data = data.drop_duplicates(keep='first')

# Get character names, kart names, etc.
karts = data.loc['Standard Kart' : 'Tanooki Kart'].T
chars = data.loc['Mario' : 'Cat Peach'].T
wheels = data.loc['Standard' : 'Sponge'].T
gliders = data.loc['Super Glider' :].T

# Sum up all possible stat combinations and add separate columns for character, kart, etc.
char_list, kart_list, wheel_list, glider_list = list(zip(*[name for name in it.product(chars, karts, wheels, gliders)]))
stat_list = [(chars[name[0]] + karts[name[1]] + wheels[name[2]] + gliders[name[3]]) for name in it.product(chars, karts, wheels, gliders)]
names = [(name[0] + '_' + name[1] + '_' + name[2] + '_' + name[3]) for name in it.product(chars, karts, wheels, gliders)]
stats = pd.DataFrame(dict(zip(names, stat_list))).T
stats['Character'] = char_list
stats['Kart'] = kart_list
stats['Wheel'] = wheel_list
stats['Glider'] = glider_list
stats = stats.reindex(columns=['Character', 'Kart', 'Wheel', 'Glider', 'Weight', 'Acceleration', 'On-road Traction',
                                'Off-road Traction', 'Mini-Turbo', 'Ground Speed', 'Water Speed', 
                                'Anti-gravity Speed', 'Air Speed', 'Ground Handling', 'Water Handling', 
                                'Anti-gravity Handling', 'Air Handling'])

# Streamlit title/subtitle
row1_1, _, row1_2 = st.columns((1.75, 1.5, 1.5))

row1_1.header('Three-Way Pareto Optimal Mario Kart Combinations')

with row1_2:
    st.write('')
    row1_2.subheader('A Web App by [Mike Colella](https://github.com/mcolella326)')

# Streamlit dropdown selection - updates all dropdowns on update such that you cannot select the same option for 2 or more dropdowns at once
@st.cache(allow_output_mutation=True) # "Remember" output of a function based on input across reruns/adjusting values
def get_state(): # Retain state upon changing
    return {}

def display_dropdowns():
    # Get unique options and corresponding index value for each dropdown (unique indices generated for each dropdown for each dropdown combination)
    opts_x = ['Weight', 'Acceleration', 'On-road Traction',
            'Off-road Traction', 'Mini-Turbo', 'Ground Speed', 'Water Speed', 
            'Anti-gravity Speed', 'Air Speed', 'Ground Handling', 'Water Handling', 
            'Anti-gravity Handling', 'Air Handling']
    opts_x.remove(state['coord_y'])
    opts_x.remove(state['coord_z'])
    x_index = [i for i, opt in enumerate(opts_x) if opt == state['coord_x']][0]
    opts_y = ['Weight', 'Acceleration', 'On-road Traction',
            'Off-road Traction', 'Mini-Turbo', 'Ground Speed', 'Water Speed', 
            'Anti-gravity Speed', 'Air Speed', 'Ground Handling', 'Water Handling', 
            'Anti-gravity Handling', 'Air Handling']
    opts_y.remove(state['coord_x'])
    opts_y.remove(state['coord_z'])
    y_index = [i for i, opt in enumerate(opts_y) if opt == state['coord_y']][0]
    opts_z = ['Weight', 'Acceleration', 'On-road Traction',
            'Off-road Traction', 'Mini-Turbo', 'Ground Speed', 'Water Speed', 
            'Anti-gravity Speed', 'Air Speed', 'Ground Handling', 'Water Handling', 
            'Anti-gravity Handling', 'Air Handling']
    opts_z.remove(state['coord_x'])
    opts_z.remove(state['coord_y'])
    z_index = [i for i, opt in enumerate(opts_z) if opt == state['coord_z']][0]
    return coord_x_placeholder.selectbox('X', options=opts_x, index=x_index), coord_y_placeholder.selectbox('Y', options=opts_y, index=y_index), coord_z_placeholder.selectbox('Z', options=opts_z, index=z_index)

state = get_state() # Empty dictionary to contain selected categories

# Initialize state dictionary/sidebar dropdowns (empty lets you multiple selectboxes to the same variable as long as the indices are unique)
if 'coord_x' not in state:
    state['coord_x'] = 'Weight'
if 'coord_y' not in state:
    state['coord_y'] = 'Acceleration'
if 'coord_z' not in state:
    state['coord_z'] = 'On-road Traction'

coord_x_placeholder = st.sidebar.empty()
coord_y_placeholder = st.sidebar.empty()
coord_z_placeholder = st.sidebar.empty()

coord_x, coord_y, coord_z = display_dropdowns()
input_changed = False # Flag to ensure only one if statement is run if input has changed
if coord_x != state['coord_x'] and not input_changed:
    state['coord_x'] = coord_x
    input_changed = True
    display_dropdowns()
if coord_y != state['coord_y'] and not input_changed:
    state['coord_y'] = coord_y
    input_changed = True
    display_dropdowns()
if coord_z != state['coord_z'] and not input_changed:
    state['coord_z'] = coord_z
    input_changed = True
    display_dropdowns()

# 2D Optimization - Define functions for getting max ground speed for each unique acceleration and drop all not pareto optimal 
# (keep only last/greatest acceleration at same ground speed), and get corresponding DF for pareto frontier
@st.cache(allow_output_mutation=True)
def simple_cull_2d(coord1, coord2):
    inputPoints = stats[[coord1, coord2]].drop_duplicates().reset_index(drop=True)
    candidateRowNr = 0
    pareto_points = pd.DataFrame({coord1: [], coord2: []})
    while True:
        candidateRow = inputPoints.iloc[candidateRowNr]
        inputPoints = inputPoints.drop([candidateRowNr]).reset_index(drop=True)
        rowNr = 0
        nonDominated = True
        while len(inputPoints) != 0 and rowNr < len(inputPoints):
            row = inputPoints.iloc[rowNr]
            if ((candidateRow >= row).all()):
                inputPoints = inputPoints.drop([rowNr]).reset_index(drop=True)
            elif ((row >= candidateRow).all()):
                nonDominated = False
                rowNr += 1
            else:
                rowNr += 1
        if nonDominated:
            pareto_points = pareto_points.append([candidateRow], ignore_index=True)

        if len(inputPoints) == 0:
            break
    coords = pareto_points.sort_values(coord1)
    coords_renamed = coords.rename(columns={coord1: coord1, coord2: 'Max ' + coord2})
    merged = stats.merge(coords_renamed, on=coord1)
    stats_best = merged[merged[coord2] == merged['Max ' + coord2]]
    stats_best = stats_best.drop(columns='Max ' + coord2).sort_values(coord1)
    return coords, stats_best

combs = [pair for pair in it.combinations([coord_x, coord_y, coord_z], 2)]
results = list(zip(*[simple_cull_2d(*name) for name in combs]))
coords_2d = results[0]
stats_best_2d = results[1]

# Get corresponding figures
fig_2d1 = plt.figure()
ax_2d1 = fig_2d1.add_subplot(111, xlabel=combs[0][0], ylabel=combs[0][1])
ax_2d1.scatter(stats[combs[0][0]], stats[combs[0][1]])
ax_2d1.plot(coords_2d[0][combs[0][0]], coords_2d[0][combs[0][1]], c='black')
ax_2d1.scatter(coords_2d[0][combs[0][0]], coords_2d[0][combs[0][1]], c='black')

fig_2d2 = plt.figure()
ax_2d2 = fig_2d2.add_subplot(111, xlabel=combs[1][0], ylabel=combs[1][1])
ax_2d2.scatter(stats[combs[1][0]], stats[combs[1][1]])
ax_2d2.plot(coords_2d[1][combs[1][0]], coords_2d[1][combs[1][1]], c='black')
ax_2d2.scatter(coords_2d[1][combs[1][0]], coords_2d[1][combs[1][1]], c='black')

fig_2d3 = plt.figure()
ax_2d3 = fig_2d3.add_subplot(111, xlabel=combs[2][0], ylabel=combs[2][1])
ax_2d3.scatter(stats[combs[2][0]], stats[combs[2][1]])
ax_2d3.plot(coords_2d[2][combs[2][0]], coords_2d[2][combs[2][1]], c='black')
ax_2d3.scatter(coords_2d[2][combs[2][0]], coords_2d[2][combs[2][1]], c='black')

col1, col2, col3 = st.columns(3)
with col1:
    st.write('{} vs. {}'.format(combs[0][0], combs[0][1]))
    st.pyplot(fig_2d1)
    # st.table(stats_best_2d[0])

with col2:
    st.write('{} vs. {}'.format(combs[1][0], combs[1][1]))
    st.pyplot(fig_2d2)
    # st.table(stats_best_2d[1])

with col3:
    st.write('{} vs. {}'.format(combs[2][0], combs[2][1]))
    st.pyplot(fig_2d3)
    # st.table(stats_best_2d[2])

# 3D Optimization - Define functions for finding pareto frontier coords for each projection and merging into stats DF
@st.cache(allow_output_mutation=True)
def simple_cull_3d(coord1, coord2, coord3):
    inputPoints = stats[[coord1, coord2, coord3]].drop_duplicates().reset_index(drop=True)
    candidateRowNr = 0
    pareto_points = pd.DataFrame({coord1: [], coord2: [], coord3: []})
    while True:
        candidateRow = inputPoints.iloc[candidateRowNr]
        inputPoints = inputPoints.drop([candidateRowNr]).reset_index(drop=True)
        rowNr = 0
        nonDominated = True
        while len(inputPoints) != 0 and rowNr < len(inputPoints):
            row = inputPoints.iloc[rowNr]
            if ((candidateRow >= row).all()):
                inputPoints = inputPoints.drop([rowNr]).reset_index(drop=True)
            elif ((row >= candidateRow).all()):
                nonDominated = False
                rowNr += 1
            else:
                rowNr += 1
        if nonDominated:
            pareto_points = pareto_points.append([candidateRow], ignore_index=True)

        if len(inputPoints) == 0:
            break
    coords = pareto_points.sort_values(coord1)
    coords_renamed = coords.rename(columns={coord1: coord1, coord2: coord2, coord3: 'Max ' + coord3})
    merged = stats.merge(coords_renamed, on=[coord1, coord2])
    stats_best = merged[merged[coord3] == merged['Max ' + coord3]]
    stats_best = stats_best.drop(columns='Max ' + coord3).sort_values(coord1)
    return coords, stats_best

coords_3d, stats_best_3d = simple_cull_3d(coord_x, coord_y, coord_z)

# Plot 3D combinations and corresponding pareto frontier surf
fig_3D = go.Figure()
fig_3D.add_trace(go.Mesh3d(x=coords_3d[coord_x], y=coords_3d[coord_y], z=coords_3d[coord_z]))
fig_3D.add_trace(go.Scatter3d(x=stats[coord_x], y=stats[coord_y], z=stats[coord_z], mode='markers', marker=dict(size=4, color='black', opacity=0.5)))
fig_3D.update_layout(scene=dict(xaxis_title=coord_x, yaxis_title=coord_y, zaxis_title=coord_z), height=1000, width=1000)

# Plot 3D graph
_, row3, _ = st.columns((.5, 1, .01))
with row3:
    st.header('{} vs {} vs {}'.format(coord_x, coord_y, coord_z))

_, row4, _ = st.columns((.2, 1, .01))
with row4:
    st.plotly_chart(fig_3D)

# Add additional information
_, row5, _ = st.columns((.1, 3.2, .1))
with row5:
    st.markdown('___')
    about = st.expander('About/Additional Info')
    with about:
        '''Thanks for checking out my app! It was built entirely using Mario Kart 8 statistic found on [Mario Wiki](https://www.mariowiki.com/Mario_Kart_8_Deluxe_in-game_statistics). Special thanks to 
        [George Ho](https://github.com/eigenfoo) for all the help with both introducing me to Streamlit and with making this all possible.
        This is the first time I have ever built something like this, and any comments/suggestions are appreciated!'''
    
        '''This app aggregates all data from 3 user-selected categories and displays a pareto-optimal curve between each two variables and generates a 3D pareto-optimal surface for all 3 variables. Additionally,
        a set of "best performing" characters for each pareto-optimal point. These statistics are optimized under a set of various statistics described below:'''
    
        '''**Weight** - Weight'''
    
        '''etc.'''
    
        '''### Mike Colella, 2022'''