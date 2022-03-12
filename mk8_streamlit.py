import streamlit as st
import pandas as pd
from matplotlib import pyplot as plt
import itertools as it
import plotly.graph_objects as go

st.set_page_config(layout="wide")

st.sidebar.write("Select an optimization method:")  # Filler text, to be adjusted
choice = st.sidebar.radio("", ("Mode 1", "Mode 2"))  # Filler text, to be adjusted

# Mode 1: Pareto optimizations based on selecting kart combos and recommending better ones based on a 13-way optimization
if choice == "Mode 1":
    st.write("TODO: Make Mode 1")  # Filler text, to be adjusted

# Mode 2: Pareto optimal combinations based on 3 unique criteria
else:
    # Import data/set page characteristics - cache for loadtime optimization
    @st.cache(allow_output_mutation=True)
    def import_data():
        data = pd.read_csv(r"MK8Data.csv", index_col="Names").dropna()
        coords_2d_data = pd.read_csv(r"2dCoords.csv", index_col=[0, 1]).drop(
            columns="Ind"
        )
        stats_2d_data = pd.read_csv(r"2dStats.csv", index_col=[0, 1]).drop(
            columns="Ind"
        )
        coords_3d_data = pd.read_csv(r"3dCoords.csv", index_col=[0, 1, 2]).drop(
            columns="Ind"
        )
        stats_3d_data = pd.read_csv(r"3dStats.csv", index_col=[0, 1, 2]).drop(
            columns="Ind"
        )
        coords_2d = {
            (a, b): (
                v.reset_index()
                .dropna(axis="columns")
                .drop(columns=["Coord1", "Coord2"])
            )
            for (a, b), v in coords_2d_data.groupby(level=["Coord1", "Coord2"])
        }
        stats_2d = {
            (a, b): (
                v.reset_index()
                .dropna(axis="columns")
                .drop(columns=["Coord1", "Coord2"])
            )
            for (a, b), v in stats_2d_data.groupby(level=["Coord1", "Coord2"])
        }
        coords_3d = {
            (a, b, c): (
                v.reset_index()
                .dropna(axis="columns")
                .drop(columns=["Coord1", "Coord2", "Coord3"])
            )
            for (a, b, c), v in coords_3d_data.groupby(
                level=["Coord1", "Coord2", "Coord3"]
            )
        }
        stats_3d = {
            (a, b, c): (
                v.reset_index()
                .dropna(axis="columns")
                .drop(columns=["Coord1", "Coord2", "Coord3"])
            )
            for (a, b, c), v in stats_3d_data.groupby(
                level=["Coord1", "Coord2", "Coord3"]
            )
        }
        return data, coords_2d, stats_2d, coords_3d, stats_3d

    data, coords_2d, stats_2d, coords_3d, stats_3d = import_data()

    # Remove all characters, karts, etc. that have exactly the same stats
    data = data.drop_duplicates(keep="first")

    # Get character names, kart names, etc.
    karts = data.loc["Standard Kart":"Tanooki Kart"].T
    chars = data.loc["Mario":"Cat Peach"].T
    wheels = data.loc["Standard":"Sponge"].T
    gliders = data.loc["Super Glider":].T

    # Sum up all possible stat combinations and add separate columns for character, kart, etc.
    char_list, kart_list, wheel_list, glider_list = list(
        zip(*[name for name in it.product(chars, karts, wheels, gliders)])
    )
    stat_list = [
        (chars[name[0]] + karts[name[1]] + wheels[name[2]] + gliders[name[3]])
        for name in it.product(chars, karts, wheels, gliders)
    ]
    names = [
        (name[0] + "_" + name[1] + "_" + name[2] + "_" + name[3])
        for name in it.product(chars, karts, wheels, gliders)
    ]
    stats = pd.DataFrame(dict(zip(names, stat_list))).T
    stats["Character"] = char_list
    stats["Kart"] = kart_list
    stats["Wheel"] = wheel_list
    stats["Glider"] = glider_list
    stats = stats.reindex(
        columns=[
            "Character",
            "Kart",
            "Wheel",
            "Glider",
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
    )

    # Streamlit title/subtitle
    row1_1, _, row1_2 = st.columns((1.75, 1.5, 1.5))

    row1_1.header("Three-Way Pareto Optimal Mario Kart Combinations")

    with row1_2:
        st.write("")
        row1_2.subheader("A Web App by [Mike Colella](https://github.com/mcolella326)")

    # Streamlit dropdown selection - updates all dropdowns on update such that you cannot select the same option for 2 or more dropdowns at once
    @st.cache(
        allow_output_mutation=True
    )  # "Remember" output of a function based on input across reruns/adjusting values
    def get_state():  # Retain state upon changing
        return {}

    def display_dropdowns():
        # Get unique options and corresponding index value for each dropdown (unique indices generated for each dropdown for each dropdown combination)
        opts_x = [
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
        opts_x.remove(state["coord_y"])
        opts_x.remove(state["coord_z"])
        x_index = [i for i, opt in enumerate(opts_x) if opt == state["coord_x"]][0]
        opts_y = [
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
        opts_y.remove(state["coord_x"])
        opts_y.remove(state["coord_z"])
        y_index = [i for i, opt in enumerate(opts_y) if opt == state["coord_y"]][0]
        opts_z = [
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
    xy_coords = coords_2d[
        [
            pair
            for pair in it.permutations((coord_x, coord_y), 2)
            if pair in coords_2d.keys()
        ][0]
    ]
    xz_coords = coords_2d[
        [
            pair
            for pair in it.permutations((coord_x, coord_z), 2)
            if pair in coords_2d.keys()
        ][0]
    ]
    yz_coords = coords_2d[
        [
            pair
            for pair in it.permutations((coord_y, coord_z), 2)
            if pair in coords_2d.keys()
        ][0]
    ]

    fig_2d1 = plt.figure()
    ax_2d1 = fig_2d1.add_subplot(111, xlabel=coord_x, ylabel=coord_y)
    ax_2d1.scatter(stats[coord_x], stats[coord_y])
    ax_2d1.plot(xy_coords[coord_x], xy_coords[coord_y], c="black")
    ax_2d1.scatter(xy_coords[coord_x], xy_coords[coord_y], c="black")

    fig_2d2 = plt.figure()
    ax_2d2 = fig_2d2.add_subplot(111, xlabel=coord_x, ylabel=coord_z)
    ax_2d2.scatter(stats[coord_x], stats[coord_z])
    ax_2d2.plot(xz_coords[coord_x], xz_coords[coord_z], c="black")
    ax_2d2.scatter(xz_coords[coord_x], xz_coords[coord_z], c="black")

    fig_2d3 = plt.figure()
    ax_2d3 = fig_2d3.add_subplot(111, xlabel=coord_y, ylabel=coord_z)
    ax_2d3.scatter(stats[coord_y], stats[coord_z])
    ax_2d3.plot(yz_coords[coord_y], yz_coords[coord_z], c="black")
    ax_2d3.scatter(yz_coords[coord_y], yz_coords[coord_z], c="black")

    st.header("2D Projection Pareto Optimal Combinations")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write("{} vs. {}".format(coord_x, coord_y))
        st.pyplot(fig_2d1)

    with col2:
        st.write("{} vs. {}".format(coord_x, coord_z))
        st.pyplot(fig_2d2)

    with col3:
        st.write("{} vs. {}".format(coord_y, coord_z))
        st.pyplot(fig_2d3)

    # 3D Optimization - Read 3d pareto optimal coordinates and statistics and plot 3d graphs of criteria for each character/kart combination
    xyz_coords = coords_3d[
        [
            triplet
            for triplet in it.permutations((coord_x, coord_y, coord_z), 3)
            if triplet in coords_3d.keys()
        ][0]
    ]
    xyz_stats = stats_3d[
        [
            triplet
            for triplet in it.permutations((coord_x, coord_y, coord_z), 3)
            if triplet in coords_3d.keys()
        ][0]
    ]

    fig_3D = go.Figure()
    fig_3D.add_trace(
        go.Mesh3d(x=xyz_coords[coord_x], y=xyz_coords[coord_y], z=xyz_coords[coord_z])
    )
    fig_3D.add_trace(
        go.Scatter3d(
            x=stats[coord_x],
            y=stats[coord_y],
            z=stats[coord_z],
            mode="markers",
            marker=dict(size=4, color="black", opacity=0.5),
        )
    )
    fig_3D.update_layout(
        scene=dict(xaxis_title=coord_x, yaxis_title=coord_y, zaxis_title=coord_z),
        height=1000,
        width=1000,
    )

    st.header("3D Overall Pareto Optimal Combinations")
    st.write("{} vs {} vs {}".format(coord_x, coord_y, coord_z))
    st.plotly_chart(fig_3D)

    st.write("Optmized character/kart combinations for the selected criteria")
    st.dataframe(
        xyz_stats[["Character", "Kart", "Wheel", "Glider", coord_x, coord_y, coord_z]],
        width=2000,
        height=30 * len(xyz_stats),
    )

# Add additional information
_, row4, _ = st.columns((0.1, 3.2, 0.1))
with row4:
    st.markdown("___")
    about = st.expander("About/Additional Info")
    with about:
        """Thanks for checking out my app! It was built entirely using Mario Kart 8 statistic found on [Mario Wiki](https://www.mariowiki.com/Mario_Kart_8_Deluxe_in-game_statistics). Special thanks to 
        [George Ho](https://github.com/eigenfoo) for introducing me to Streamlit.
        This is the first time I have ever built something like this, and any comments/suggestions are appreciated!"""

        """This app aggregates all data from 3 user-selected categories and displays a pareto-optimal curve between each two variables and generates a 3D pareto-optimal surface for all 3 variables. Additionally,
        a set of "best performing" characters for each pareto-optimal point. These statistics are optimized under a set of various statistics described below:"""

        """**Weight** - Weight"""

        """etc."""

        """### Mike Colella, 2022"""