import dash_html_components as html
import dash_bootstrap_components as dbc
from New_Login import dash_app
import os
import json

dash_app.config['suppress_callback_exceptions'] = True
main_path_data = os.path.abspath("./data")


def posts():
    dataj = open(main_path_data + "\\posts.json", "r")
    data = json.load(dataj)
    dataj.close()

    all_posts = []

    for k, v in data.items():
        post = html.Div(
            style={'margin':'20px','padding':'5px', 'background-color': '#A9BDBD'},
            children=[
                    dbc.Row(style={'min-height':'100px','max-height':'100px', 'overflowY':'hidden'},
                            children=[html.H6(v['text'], style={'padding':'20px', 'color':'black'})]),
                    dbc.Row(style={'min-height':'50px','max-height':'50px', 'margin-top':'10px','overflowY':'hidden'},
                            children=[
                                dbc.Col(dbc.Button(
                                    id={'type': 'like-button',
                                        'index': k},
                                    children=["like-button", dbc.Badge(v['likes'],
                                                                       id={'type': 'likes',
                                                                           'index': k},
                                                                       color="light",
                                                                       className="ml-1")],
                                    color="primary",
                                    n_clicks=0
                                    )),
                                dbc.Col(dbc.Button(
                                    id={'type': 'dislike-button',
                                        'index': k},
                                    children=["dislike-button", dbc.Badge(v['dislikes'],
                                                                          id={'type': 'dislikes',
                                                                           'index': k},
                                                                          color="light",
                                                                          className="ml-1")],
                                    color="danger",
                                    n_clicks=0
                                    ))
                            ])])

        all_posts.append(post)

    return all_posts




