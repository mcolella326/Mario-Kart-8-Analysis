import streamlit as st
import pandas as pd
import itertools as it


@st.cache
def get_stats():
    """ Get combined statistics for each combination of character, kart, wheel, and glider """
    # Import data
    data = pd.read_csv(r"MK8Data.csv", index_col="Names").dropna()

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
    return stats


# 2D optimization
def simple_cull_2d(coord1, coord2):
    """ Algorithm to obtain pareto optimal coordinates for 2 dimensions """
    stats = get_stats()
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
            if (candidateRow >= row).all():
                inputPoints = inputPoints.drop([rowNr]).reset_index(drop=True)
            elif (row >= candidateRow).all():
                nonDominated = False
                rowNr += 1
            else:
                rowNr += 1
        if nonDominated:
            pareto_points = pareto_points.append([candidateRow], ignore_index=True)

        if len(inputPoints) == 0:
            break
    coords = pareto_points.sort_values(coord1)
    coords_renamed = coords.rename(columns={coord1: coord1, coord2: "Max " + coord2})
    merged = stats.merge(coords_renamed, on=coord1)
    stats_best = merged[merged[coord2] == merged["Max " + coord2]]
    stats_best = stats_best.drop(columns="Max " + coord2).sort_values(coord1)
    return coords, stats_best


# Create MultiIndex DF for coords/stats and export to CSV
def export_csv_2d():
    """ Export simple cull algo results as CSV (2dCoords/Stats.csv) """
    choices = [
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
    combs = [pair for pair in it.combinations(choices, 2)]
    results = list(zip(*[simple_cull_2d(*name) for name in combs]))
    coords_2d = results[0]
    stats_best_2d = results[1]

    coords_2d_dict = {choice: coord for choice, coord in zip(combs, coords_2d)}
    stats_best_2d_dict = {choice: stat for choice, stat in zip(combs, stats_best_2d)}
    coords_2d_df = pd.concat(
        coords_2d_dict.values(),
        keys=coords_2d_dict.keys(),
        names=["Coord1", "Coord2", "Ind"],
    )
    coords_2d_df.to_csv("2dCoords.csv")
    stats_best_2d_df = pd.concat(
        stats_best_2d_dict.values(),
        keys=stats_best_2d_dict.keys(),
        names=["Coord1", "Coord2", "Ind"],
    )
    stats_best_2d_df.to_csv("2dStats.csv")
    return


# 3D Optimization
def simple_cull_3d(coord1, coord2, coord3):
    """ Algorithm to obtain pareto optimal coordinates for 3 dimensions """
    stats = get_stats()
    inputPoints = (
        stats[[coord1, coord2, coord3]].drop_duplicates().reset_index(drop=True)
    )
    candidateRowNr = 0
    pareto_points = pd.DataFrame({coord1: [], coord2: [], coord3: []})
    while True:
        candidateRow = inputPoints.iloc[candidateRowNr]
        inputPoints = inputPoints.drop([candidateRowNr]).reset_index(drop=True)
        rowNr = 0
        nonDominated = True
        while len(inputPoints) != 0 and rowNr < len(inputPoints):
            row = inputPoints.iloc[rowNr]
            if (candidateRow >= row).all():
                inputPoints = inputPoints.drop([rowNr]).reset_index(drop=True)
            elif (row >= candidateRow).all():
                nonDominated = False
                rowNr += 1
            else:
                rowNr += 1
        if nonDominated:
            pareto_points = pareto_points.append([candidateRow], ignore_index=True)

        if len(inputPoints) == 0:
            break
    coords = pareto_points.sort_values(coord1)
    coords_renamed = coords.rename(
        columns={coord1: coord1, coord2: coord2, coord3: "Max " + coord3}
    )
    merged = stats.merge(coords_renamed, on=[coord1, coord2])
    stats_best = merged[merged[coord3] == merged["Max " + coord3]]
    stats_best = stats_best.drop(columns="Max " + coord3).sort_values(coord1)
    return coords, stats_best


# Create MultiIndex DF for coords/stats and export to CSV
def export_csv_3d():
    """ Export simple cull algo results as CSV (3dCoords/Stats.csv) """
    choices = [
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
    combs = [triplet for triplet in it.permutations(choices, 3)]
    results = list(zip(*[simple_cull_3d(*name) for name in combs]))
    coords_3d = results[0]
    stats_best_3d = results[1]

    coords_3d_dict = {choice: coord for choice, coord in zip(combs, coords_3d)}
    stats_best_3d_dict = {choice: stat for choice, stat in zip(combs, stats_best_3d)}
    coords_3d_df = pd.concat(
        coords_3d_dict.values(),
        keys=coords_3d_dict.keys(),
        names=["Coord1", "Coord2", "Coord3", "Ind"],
    )
    coords_3d_df.to_csv("3dCoords.csv")
    stats_best_3d_df = pd.concat(
        stats_best_3d_dict.values(),
        keys=stats_best_3d_dict.keys(),
        names=["Coord1", "Coord2", "Coord3", "Ind"],
    )
    stats_best_3d_df.to_csv("3dStats.csv")
    return


def simple_cull_13d():
    """ Algorithm to obtain pareto optimal coordinates for all 13 criteria """
    stats = get_stats()
    inputPoints = stats.copy().drop_duplicates().reset_index(drop=True)
    candidateRowNr = 0
    choices = [
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
    pareto_points = pd.DataFrame(columns=choices)
    while True:
        candidateRow = inputPoints.iloc[candidateRowNr]
        inputPoints = inputPoints.drop([candidateRowNr]).reset_index(drop=True)
        rowNr = 0
        nonDominated = True
        while len(inputPoints) != 0 and rowNr < len(inputPoints):
            row = inputPoints.iloc[rowNr]
            if (candidateRow >= row).all():
                inputPoints = inputPoints.drop([rowNr]).reset_index(drop=True)
            elif (row >= candidateRow).all():
                nonDominated = False
                rowNr += 1
            else:
                rowNr += 1
        if nonDominated:
            pareto_points = pareto_points.append([candidateRow], ignore_index=True)

        if len(inputPoints) == 0:
            break

    coords = pareto_points.sort_values("Weight")
    return coords


def export_csv_13d():
    """ Export simple cull algo results as CSV (AllCoords.csv) """
    coords_13d = simple_cull_13d()
    coords_13d.to_csv("AllCoords.csv")
    return


if __name__ == "__main__":
    export_csv_2d()
    export_csv_3d()
    export_csv_13d()
