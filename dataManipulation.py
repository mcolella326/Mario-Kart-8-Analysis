import streamlit as st
import pandas as pd
from matplotlib import pyplot as plt
import itertools as it
import plotly.graph_objects as go
from computeParetoPoints import get_stats

# Import data/set page characteristics - cache for loadtime optimization
@st.cache
def df_to_dict_2d(df):
    dict_2d = {
        (a, b): (
            v.reset_index().dropna(axis="columns").drop(columns=["Coord1", "Coord2"])
        )
        for (a, b), v in df.groupby(level=["Coord1", "Coord2"])
    }
    return dict_2d


@st.cache
def df_to_dict_3d(df):
    dict_3d = {
        (a, b, c): (
            v.reset_index()
            .dropna(axis="columns")
            .drop(columns=["Coord1", "Coord2", "Coord3"])
        )
        for (a, b, c), v in df.groupby(level=["Coord1", "Coord2", "Coord3"])
    }
    return dict_3d


@st.cache
def import_data_2d():
    coords_2d_data = pd.read_csv(r"2dCoords.csv", index_col=[0, 1]).drop(columns="Ind")
    coords_2d = df_to_dict_2d(coords_2d_data)
    return coords_2d


@st.cache
def import_data_3d():
    coords_3d_data = pd.read_csv(r"3dCoords.csv", index_col=[0, 1, 2]).drop(
        columns="Ind"
    )
    stats_3d_data = pd.read_csv(r"3dStats.csv", index_col=[0, 1, 2]).drop(columns="Ind")
    coords_3d, stats_3d = df_to_dict_3d(coords_3d_data), df_to_dict_3d(stats_3d_data)
    return coords_3d, stats_3d


def plot_2d(coord1, coord2):
    stats = get_stats()
    coords_2d = import_data_2d()
    coords_proj = coords_2d[
        [
            pair
            for pair in it.permutations((coord1, coord2), 2)
            if pair in coords_2d.keys()
        ][0]
    ]
    fig = plt.figure()
    ax = fig.add_subplot(111, xlabel=coord1, ylabel=coord2)
    ax.scatter(stats[coord1], stats[coord2])
    ax.plot(coords_proj[coord1], coords_proj[coord2], c="black")
    ax.scatter(coords_proj[coord1], coords_proj[coord2], c="black")
    st.write(f"{coord1} vs. {coord2}")
    st.pyplot(fig)
    return


def plot_3d(coord1, coord2, coord3):
    stats = get_stats()
    coords_3d, stats_3d = import_data_3d()
    ind = [
        triplet
        for triplet in it.permutations((coord1, coord2, coord3), 3)
        if triplet in coords_3d.keys()
    ][0]
    coords_df = coords_3d[ind]
    stats_df = stats_3d[ind]
    fig_3d = go.Figure()
    fig_3d.add_trace(
        go.Mesh3d(x=coords_df[coord1], y=coords_df[coord2], z=coords_df[coord3])
    )
    fig_3d.add_trace(
        go.Scatter3d(
            x=stats[coord1],
            y=stats[coord2],
            z=stats[coord3],
            mode="markers",
            marker=dict(size=4, color="black", opacity=0.5),
        )
    )
    fig_3d.update_layout(
        scene=dict(xaxis_title=coord1, yaxis_title=coord2, zaxis_title=coord3),
        height=750,
        width=750,
    )
    st.write(f"{coord1} vs. {coord2} vs. {coord3}")
    st.plotly_chart(fig_3d)
    st.write("Optmized character/kart combinations for the selected criteria")
    st.dataframe(
        stats_df[["Character", "Kart", "Wheel", "Glider", coord1, coord2, coord3]],
        width=2000,
        height=30 * len(stats),
    )
    return


def get_selected_pareto(char, kart, wheel, glider):
    pareto = pd.read_csv(r"AllCoords.csv")
    selected = pareto[
        (pareto["Character"] == char)
        & (pareto["Kart"] == kart)
        & (pareto["Wheel"] == wheel)
        & (pareto["Glider"] == glider)
    ]
    selected = selected[
        [
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
    ]
    return selected


def get_options():
    stats = get_stats()
    char_list = stats["Character"].unique()
    kart_list = stats["Kart"].unique()
    wheel_list = stats["Wheel"].unique()
    glider_list = stats["Glider"].unique()
    return char_list, kart_list, wheel_list, glider_list


def get_dominated(char, kart, wheel, glider):
    stats = get_stats()
    selected = stats[
        (stats["Character"] == char)
        & (stats["Kart"] == kart)
        & (stats["Wheel"] == wheel)
        & (stats["Glider"] == glider)
    ]
    stats = stats.drop(selected.index)
    stats_numeric = stats[
        [
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
    ]
    selected = selected[
        [
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
    ].reset_index(drop=True)
    dominated = stats[(stats_numeric >= selected.squeeze()).all(1)].reset_index(
        drop=True
    )
    st.dataframe(dominated, width=20000, height=30 * len(stats))
    return


if __name__ == "__main__":
    plot_2d("Weight", "Acceleration")
    plot_3d("Weight", "Acceleration", "On-road Traction")
