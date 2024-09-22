import json
import math
import random
from itertools import cycle
from random import uniform

import dash
import dash_cytoscape as cyto
from dash import Input, Output, dcc, html, callback, State

from demos import dash_reusable_components as drc

cyto.load_extra_layouts()
app = dash.Dash(__name__)
server = app.server

# ###################### DATA PREPROCESSING ######################
# Load data
with open("demos/data/sample_network.txt", "r", encoding="utf-8") as f:
    network_data = f.read().split("\n")

# We select the first 750 edges and associated nodes for an easier visualization
edges = network_data[:750]
nodes = set()

cy_edges = []
cy_nodes = []

for network_edge in edges:
    source, target = network_edge.split(" ")

    if source not in nodes:
        nodes.add(source)
        cy_nodes.append({"data": {"id": source, "label": "User #" + source[-5:]}, "position": {'x': 0, 'y': 0}})
    if target not in nodes:
        nodes.add(target)
        cy_nodes.append({"data": {"id": target, "label": "User #" + target[-5:]}, "position": {'x': 0, 'y': 0}})

    cy_edges.append({"data": {"source": source, "target": target}})

default_stylesheet = [
    {
        "selector": "node",
        "style": {
            "opacity": 0.65,
        },
    },
    {"selector": "edge", "style": {"curve-style": "bezier", "opacity": 0.65}},
]

styles = {
    "json-output": {
        "overflow-y": "scroll",
        "height": "calc(50% - 25px)",
        "border": "thin lightgrey solid",
    },
    "tab": {"height": "calc(98vh - 105px)"},
}

app.layout = html.Div(
    [
        html.Div(
            className="eight columns",
            children=[
                cyto.Cytoscape(
                    id="cytoscape",
                    elements=cy_edges + cy_nodes,
                    style={"height": "95vh", "width": "100%"},
                    layout={"name": "cola"},
                    wheelSensitivity=0.1,
                )
            ],
        ),
        html.Div(
            className="four columns",
            children=[
                dcc.Tabs(
                    id="tabs",
                    children=[
                        dcc.Tab(
                            label="Control Panel",
                            children=[
                                drc.NamedDropdown(
                                    name="Layout",
                                    id="dropdown-layout",
                                    options=drc.DropdownOptionsList(
                                        "random",
                                        "grid",
                                        "circle",
                                        "concentric",
                                        "breadthfirst",
                                        "cose",
                                    ),
                                    value="grid",
                                    clearable=False,
                                ),
                                drc.NamedDropdown(
                                    name="Node Shape",
                                    id="dropdown-node-shape",
                                    value="ellipse",
                                    clearable=False,
                                    options=drc.DropdownOptionsList(
                                        "ellipse",
                                        "triangle",
                                        "rectangle",
                                        "diamond",
                                        "pentagon",
                                        "hexagon",
                                        "heptagon",
                                        "octagon",
                                        "star",
                                        "polygon",
                                    ),
                                ),
                                drc.NamedInput(
                                    name="Followers Color",
                                    id="input-follower-color",
                                    type="text",
                                    value="#ff0000",
                                ),
                                drc.NamedInput(
                                    name="Following Color",
                                    id="input-following-color",
                                    type="text",
                                    value="#FF4136",
                                ),
                            ],
                        ),
                        dcc.Tab(
                            label="JSON",
                            children=[
                                html.Div(
                                    style=styles["tab"],
                                    children=[
                                        html.P("Node Object JSON:"),
                                        html.Pre(
                                            id="tap-node-json-output",
                                            style=styles["json-output"],
                                        ),
                                        html.P("Edge Object JSON:"),
                                        html.Pre(
                                            id="tap-edge-json-output",
                                            style=styles["json-output"],
                                        ),
                                    ],
                                )
                            ],
                        ),
                    ],
                ),
            ],
        ),
    ]
)


@callback(Output("tap-node-json-output", "children"), Input("cytoscape", "tapNode"))
def display_tap_node(data):
    return json.dumps(data, indent=2)


@callback(Output("tap-edge-json-output", "children"), Input("cytoscape", "tapEdge"))
def display_tap_edge(data):
    return json.dumps(data, indent=2)


# @callback(Output("cytoscape", "layout", allow_duplicate=True), Input("dropdown-layout", "value"))
# def update_cytoscape_layout(layout):
#     return {"name": layout}


@callback(
    [
        Output("cytoscape", "stylesheet"),
        Output("cytoscape", "elements"),
        Output("cytoscape", "layout"),
    ],
    [
        Input("cytoscape", "tapNode"),
        Input("input-follower-color", "value"),
        Input("input-following-color", "value"),
        Input("dropdown-node-shape", "value"),
    ],
    State("cytoscape", "elements"),
)
def generate_stylesheet(node, follower_color, following_color, node_shape, elements):
    default_layout = {"name": "cola"}
    if not node:
        return default_stylesheet, elements, default_layout

    if node.get('data').get("expanded"):
        for element in elements:
            if node.get('data')["id"] == element.get("data").get("id"):
                element["data"]["expanded"] = False
                return default_stylesheet, elements, default_layout
        return default_stylesheet, elements, default_layout
    else:
        for element in elements:
            if node.get('data')["id"] == element.get("data").get("id"):
                element["data"]["expanded"] = True
                break

    node_id = node["data"]["id"]
    stylesheet = [
        {"selector": "node", "style": {"opacity": 0.3, "shape": node_shape}},
        {
            "selector": "edge",
            "style": {
                "opacity": 0.2,
                "curve-style": "bezier",
            },
        },
        {
            "selector": f'node[id = "{node_id}"]',
            "style": {
                "background-color": "#B10DC9",
                "border-color": "purple",
                "border-width": 2,
                "border-opacity": 1,
                "opacity": 1,
                "label": "data(label)",
                "color": "#B10DC9",
                "text-opacity": 1,
                "font-size": 12,
                "z-index": 9999,
            },
        },
    ]

    colours = cycle([
        "#ff5733",
        "#33ff57",
        "#3357ff",
        "#ff33a1",
        "#a1ff33",
        "#33a1ff",
        "#ff8c33",
        "#8cff33",
        "#338cff",
        "#ff33d4"
    ])

    parents_and_children = dict()
    parents_and_children[node_id] = []

    for edge in node["edgesData"]:
        if edge["source"] == node_id:
            parents_and_children[node_id].append(edge["target"])
            parents_and_children[edge["target"]] = []
            colour = next(colours)
            stylesheet.append(
                {
                    "selector": f'node[id = "{edge["target"]}"]',
                    "style": {"background-color": colour, "opacity": 0.9},
                }
            )
            stylesheet.append(
                {
                    "selector": f'edge[id= "{edge["id"]}"]',
                    "style": {
                        "mid-target-arrow-color": colour,
                        "mid-target-arrow-shape": "vee",
                        "line-color": colour,
                        "opacity": 0.9,
                        "z-index": 500000,
                    },
                }
            )

            # Highlight children of the child nodes in green
            for element in elements:
                child_source = element.get('data').get("source")
                if child_source == edge["target"]:
                    child_target = element["data"]["target"]
                    parents_and_children[edge["target"]].append(child_target)
                    stylesheet.append(
                        {
                            "selector": f'node[id = "{child_target}"]',
                            "style": {"background-color": colour, "opacity": 0.9, 'shape': 'triangle'},
                        }
                    )
                    stylesheet.append(
                        {
                            "selector": f'edge[source= "{child_source}"]',
                            "style": {
                                "mid-target-arrow-color": colour,
                                "mid-target-arrow-shape": "vee",
                                "mid-target-arrow-size": 1.5,
                                "line-color": colour,
                                "opacity": 0.9,
                                "z-index": 50000,
                            },
                        }
                    )

        if edge["target"] == node_id:
            stylesheet.append(
                {
                    "selector": f'node[id = "{edge["source"]}"]',
                    "style": {
                        "background-color": follower_color,
                        "opacity": 0.9,
                        "z-index": 9999,
                    },
                }
            )
            stylesheet.append(
                {
                    "selector": f'edge[id= "{edge["id"]}"]',
                    "style": {
                        "mid-target-arrow-color": follower_color,
                        "mid-target-arrow-shape": "vee",
                        "line-color": follower_color,
                        "opacity": 1,
                        "z-index": 5000,
                    },
                }
            )
    # Adjust positions of child nodes to be closer to the parent
    new_child_positions = dict()
    nodes_already_changed = set()
    parent_id = node_id
    print(parent_id, node["position"])
    print("-----------------")
    # parent_position = node.get("position")
    # next((n["position"] for n in elements if n["data"]["id"] == parent_id and n.get("position")), None)
    for parent_id, children in parents_and_children.items():
        if parent_id == node_id:
            parent_position = node.get("position")
        else:
            if parent_id in new_child_positions:
                parent_position = new_child_positions[parent_id]
            else:
                parent_position = next((n.get("position") for n in elements if n["data"]["id"] == parent_id), None)
        # parent_position = node.get("position")
        if parent_position:
            print(parent_id, parent_position)
            num_children = len(children) + random.randint(0, 2)  # Add some randomness to the number of children
            if num_children == 0:
                continue
            radius = 500 if parent_id == node_id else 250  # Adjust the radius as needed
            angle_step = 2 * math.pi / num_children
            random_angle_offset = uniform(0, 2 * math.pi)  # Generate a random angle offset

            for i, child_id in enumerate(children):
                if child_id in nodes_already_changed:
                    continue
                angle = i * angle_step + random_angle_offset
                x_offset = radius * math.cos(angle)
                y_offset = radius * math.sin(angle)

                for n in elements:
                    nid = n["data"]["id"]
                    if nid == child_id and nid != node_id:
                        new_pos = {
                            "x": parent_position["x"] + x_offset,
                            "y": parent_position["y"] + y_offset,
                        }
                        print(f"\t {parent_id} -> {child_id}: {new_pos}")
                        n["position"] = new_pos
                        nodes_already_changed.add(child_id)
                        if parent_id == node.get("data").get("id"):
                            new_child_positions[child_id] = new_pos
    return stylesheet, elements, {'name': 'preset'}


if __name__ == "__main__":
    app.run_server(debug=True)
