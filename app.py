import streamlit as st
import dataManipulation

st.set_page_config(layout="wide")

st.sidebar.write("Select an optimization method:")
choice = st.sidebar.radio("", ("Optimize by Kart Selection", "Optimize by Stats"))

# Streamlit title/subtitle
row1_1, _, row1_2 = st.columns((1.75, 1.5, 1.5))

row1_1.header("Pareto Optimal Mario Kart Combinations")

with row1_2:
    st.write("")
    row1_2.subheader("A Web App by [Mike Colella](https://github.com/mcolella326)")

# Optimize by Kart Selection: Pareto optimizations based on selecting kart combos and recommending better ones based on a 13-way optimization
if choice == "Optimize by Kart Selection":
    char_list, kart_list, wheel_list, glider_list = dataManipulation.get_options()

    st.sidebar.write("Select a character, kart, wheel, and glider:")
    char = st.sidebar.selectbox("Character", options=char_list)
    kart = st.sidebar.selectbox("Kart", options=kart_list)
    wheel = st.sidebar.selectbox("Wheel", options=wheel_list)
    glider = st.sidebar.selectbox("Glider", options=glider_list)

    selected = dataManipulation.get_selected_pareto(char, kart, wheel, glider)

    if not (selected).empty:
        ind_max = selected.idxmax(1).squeeze()
        ind_min = selected.idxmin(1).squeeze()
        st.write(
            "This is a pareto-optimal combination! Its best stat is "
            + f"{ind_max} "
            + "at "
            + f"{selected[ind_max].max()} "
            + "and its worst stat is "
            + f"{ind_min} "
            "at " + f"{selected[ind_min].min()}."
        )
        st.write("See below for all stats:")
        st.dataframe(selected, width=20000)

    else:
        st.write(
            "Ths is not a pareto optimal combination. See below for a list of dominating combinations:"
        )
        dataManipulation.get_dominated(char, kart, wheel, glider)

# Optimize by Stats: Pareto optimal combinations based on 3 unique criteria
else:
    # Streamlit dropdown selection - updates all dropdowns on update such that you cannot select the same option for 2 or more dropdowns at once
    @st.cache(
        allow_output_mutation=True
    )  # "Remember" output of a function based on input across reruns/adjusting values
    def get_state():  # Retain state upon changing
        return {}

    def display_dropdowns():
        # Get unique options and corresponding index value for each dropdown (unique indices generated for each dropdown for each dropdown combination)
        options = [
            "Weight",
            "Acceleration",
            "On-road Traction",
            "Off-road Traction",
            "Mini-Turbo",
            "Ground Speed",
            "Water Speed",
            "Anti-gravity Speed",
            "Air Speed",
            "Ground Handling",
            "Water Handling",
            "Anti-gravity Handling",
            "Air Handling",
        ]
        opts_x = options.copy()
        opts_x.remove(state["coord_y"])
        opts_x.remove(state["coord_z"])
        x_index = [i for i, opt in enumerate(opts_x) if opt == state["coord_x"]][0]
        opts_y = options.copy()
        opts_y.remove(state["coord_x"])
        opts_y.remove(state["coord_z"])
        y_index = [i for i, opt in enumerate(opts_y) if opt == state["coord_y"]][0]
        opts_z = options.copy()
        opts_z.remove(state["coord_x"])
        opts_z.remove(state["coord_y"])
        z_index = [i for i, opt in enumerate(opts_z) if opt == state["coord_z"]][0]
        return (
            coord_x_placeholder.selectbox("Criterion 1", options=opts_x, index=x_index),
            coord_y_placeholder.selectbox("Criterion 2", options=opts_y, index=y_index),
            coord_z_placeholder.selectbox("Criterion 3", options=opts_z, index=z_index),
        )

    state = get_state()  # Empty dictionary to contain selected categories

    # Initialize state dictionary/sidebar dropdowns (empty lets you multiple selectboxes to the same variable as long as the indices are unique)
    if "coord_x" not in state:
        state["coord_x"] = "Weight"
    if "coord_y" not in state:
        state["coord_y"] = "Acceleration"
    if "coord_z" not in state:
        state["coord_z"] = "On-road Traction"

    st.sidebar.write("Select three criteria for optimization:")
    coord_x_placeholder = st.sidebar.empty()
    coord_y_placeholder = st.sidebar.empty()
    coord_z_placeholder = st.sidebar.empty()

    coord_x, coord_y, coord_z = display_dropdowns()
    input_changed = (
        False  # Flag to ensure only one if statement is run if input has changed
    )
    if coord_x != state["coord_x"] and not input_changed:
        state["coord_x"] = coord_x
        input_changed = True
        display_dropdowns()
    if coord_y != state["coord_y"] and not input_changed:
        state["coord_y"] = coord_y
        input_changed = True
        display_dropdowns()
    if coord_z != state["coord_z"] and not input_changed:
        state["coord_z"] = coord_z
        input_changed = True
        display_dropdowns()

    # 2D Optimization - Read 2d pareto optimal coordinates and statistics and plot pairwise graphs of criteria for each character/kart combination
    st.header("2D Projection Pareto Optimal Combinations")
    col1, col2, col3 = st.columns(3)
    with col1:
        dataManipulation.plot_2d(coord_x, coord_y)

    with col2:
        dataManipulation.plot_2d(coord_x, coord_z)

    with col3:
        dataManipulation.plot_2d(coord_y, coord_z)

    # 3D Optimization - Read 3d pareto optimal coordinates and statistics and plot 3d graphs of criteria for each character/kart combination
    st.header("3D Overall Pareto Optimal Combinations")
    dataManipulation.plot_3d(coord_x, coord_y, coord_z)

# Add additional information
_, row4, _ = st.columns((0.1, 3.2, 0.1))
with row4:
    st.markdown("___")
    about = st.expander("About/Additional Info")
    with about:
        """Thanks for checking out my app! It was built entirely using Mario Kart 8 statistic found on [Mario Wiki](https://www.mariowiki.com/Mario_Kart_8_Deluxe_in-game_statistics). Special thanks to 
        [eigenfoo](https://github.com/eigenfoo) for introducing me to Streamlit.
        This is the first time I have ever built something like this, and any comments/suggestions are appreciated!"""

        """This app aggregates all data from 3 user-selected categories and displays a pareto-optimal curve between each two variables and generates a 3D pareto-optimal surface for all 3 variables. Additionally,
        a set of "best performing" characters for each pareto-optimal point. These statistics are optimized under a set of various statistics described below:"""

        """**Weight** - Weight"""

        """etc."""

        """### Mike Colella, 2022"""
