# Pareto Optimal Mario Kart Combinations App
This app compiles Mario Kart 8 statistics from [Mario Wiki](https://www.mariowiki.com/Mario_Kart_8_Deluxe_in-game_statistics).
Built using [Streamlit](https://www.streamlit.io/).

## Overview
This app optimizes Mario Kart selections based on two methods. 

The first method determines all pareto optimal combinations from the 13 unique statistics Mario Wiki offers, and asks the user to select a specific character, kart, wheel set, and glider set. If the combination is pareto optimal, the statistics for this combination will be provided. If the combination is not pareto optimal, a set of dominating combinations and the corresponding statistics for each combination are provided.

The second method asks the user for three unique criteria to optimize under, and both 2D projected graphs and a 3D graph of the pareto optimal curves/surfaces are provided. Additionally, the set of pareto optimal combinations for the 3D data set with the corresponding statistics for each combination are provided.

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/mcolella326/mario-kart-8-analysis/main/app.py)
