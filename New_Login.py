import dash
import dash_html_components as html
from dash.dependencies import Input, Output, State, MATCH
from flask_restful import Resource, Api
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import Posts
import os
import json
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
from flask import Flask, Response, redirect, request, session, abort
import flask
import time
main_path_data = os.path.abspath("./data")
external_stylesheets = [dbc.themes.SOLAR]


#####   WORKING EXAMPLE   #########
server = Flask('WB')
api = Api(server)
dash_app = dash.Dash(__name__,url_base_pathname="/dash1/", server=server,external_stylesheets=external_stylesheets)
dash_app.title = 'WB'

server.config.update(
    DEBUG=True,
    SECRET_KEY='secret_xxx'
)



# flask-login
login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = "login"

# silly user model
class User(UserMixin):

    def __init__(self, id):
        self.id = id
        self.name = str(id)
        self.password = "secret"

    def __repr__(self):
        return "%d/%s/%s" % (self.id, self.name, self.password)


# create some users with ids 1 to 20
users = [User("numpynewb")]



# somewhere to login
@server.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        session['username'] = username
        if password == "1":
            id = username
            user = User(id)
            login_user(user)
            with open(main_path_data + "\\users.json", "r") as file:
                data = json.load(file)
                file.close()
                if id in data:
                    data[id]['times_logged'] = data[id]['times_logged'] + 1
                    data[id]['last_time'] = time.strftime("%Y-%m-%d %H:%M")

                    f = open(main_path_data + "\\users.json", "w")
                    json.dump(data, f)
                    f.close()
                else:
                    data[id] ={
                               "times_logged": 1,
                               "last_time":time.strftime("%Y-%m-%d %H:%M"),
                               "last_req":0
                              }
                    f = open(main_path_data + "\\users.json", "w")
                    json.dump(data, f)
                    f.close()


                return redirect(request.args.get("next"))
        else:
            return abort(401)
    else:
        return Response('''
        <form action="" method="post">
            <p><input type=text name=username>
            <p><input type=password name=password placeholder='пароль "1"'>
            <p><input type=submit value=Login>
        </form>
        ''')


# somewhere to logout
@server.route("/logout")
@login_required
def logout():
    logout_user()
    return Response('<p>Logged out</p>')


# handle login failed
@server.errorhandler(401)
def page_not_found(e):
    return Response('<p>Login failed</p>')


# callback to reload the user object
@login_manager.user_loader
def load_user(userid):
    return User(userid)

def protect_views(app):
    for view_func in app.server.view_functions:
        if view_func.startswith(app.config['url_base_pathname']):
            app.server.view_functions[view_func] = login_required(app.server.view_functions[view_func])

    return app


def serve_layout():
    page = html.Div(children=[
        dbc.Row(style={'max-height': '10vh', 'overflowY': 'hidden', 'padding': '10px', 'margin': '0px'},
                children=dcc.Link('LOGOUT', style={'color': 'azure', 'margin': '10px'}, href='/'),),
        dbc.Row(style={'max-height': '90vh', 'overflowY':'hidden', 'padding': '10px', 'margin': '0px'},
            children=[
            dbc.Col(style={"width": "40%", 'padding': '20px'},
                    children=[
                        dbc.Row(html.H1('USER NAME :')),
                        dbc.Row(dbc.Textarea(className="lg", id="text", placeholder="Напишите свой пост ...")),
                        dbc.Row(style={"text-align": "right", 'padding': '20px'},
                                children=html.Button('Save',
                                            style={'text-align': 'center',
                                                   'max-width': '100px',
                                                   'width': '100px',
                                                   'max-height': '30px',
                                                   "background-color": "palegreen",
                                                   "border-radius": "20px",
                                                   'font-size': '15px'},
                                            id='Save_Post_btn',
                                            n_clicks=0))]),

            dbc.Col(style={
                # "width": "60%",
                'padding': '10px', 'max-height': '99vh', 'overflowY':'scroll'},
                id='all_posts',
                    children=[i for i in Posts.posts()])

        ])

    ])
    return page

home = html.Div(children=[
    html.H1('Logged out'),
])

dash_app.layout = html.Div([
    dcc.Location(id='url', refresh=True),
    html.Div(id='page-content'),

])


dash_app1 = protect_views(dash_app)


@server.route('/')
@server.route('/dash1')
def render_dashboard():
    return flask.redirect('/dash1')


############   API   ###############################
class HelloWorld(Resource):
    def get(self):
        uu = open(main_path_data + "\\users.json", "r")
        user_data = json.load(uu)
        uu.close()
        data = {}

        for k,v in user_data.items():
            d = {k:{"login_last":v["last_time"], "last_request":v["last_req"]}}
            data.update(d)

        return data
api.add_resource(HelloWorld, '/all_users')

class likes(Resource):
    def get(self):
        args = request.args
        no1 = args["date_from"]
        no2 = args["date_to"]

        uu = open(main_path_data + "\\posts.json", "r")
        post_data = json.load(uu)
        uu.close()

        data = {}
        # print(data)

        for k, v in post_data.items():
            for d, r in v['like'].items():
                if r['date'] in data:
                    likes = data[r['date']] + r['like']
                    d = {r['date']: likes}
                    data.update(d)
                else:
                    d = {r['date']: r['like']}
                    data.update(d)

        dd = {}
        for k, v in data.items():
            if k > no1 and k < no2:
                dar = {k: v}
                dd.update(dar)
        return dd
api.add_resource(likes, '/api/likes/', endpoint='likes/')

class likes(Resource):
    def get(self):
        args = request.args
        no1 = args["date_from"]
        no2 = args["date_to"]

        uu = open(main_path_data + "\\posts.json", "r")
        post_data = json.load(uu)
        uu.close()

        data = {}
        # print(data)

        for k, v in post_data.items():
            for d, r in v['dislike'].items():
                if r['date'] in data:
                    likes = data[r['date']] + r['dislike']
                    d = {r['date']: likes}
                    data.update(d)
                else:
                    d = {r['date']: r['dislike']}
                    data.update(d)

        dd = {}
        for k, v in data.items():
            if k > no1 and k < no2:
                dar = {k: v}
                dd.update(dar)
        return dd
api.add_resource(likes, '/api/dislikes/', endpoint='dislikes/')










#############  Dash Callbacks  ###############
@dash_app.callback(
    Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/dash1/':
         return serve_layout()
    elif pathname == '/':
        logout_user()
        # shutdown()
        return home
    else:
        return '404'


@dash_app.callback(
    [Output('all_posts', 'children')],
    [Input('Save_Post_btn', 'n_clicks')],
    [State('text', 'value')])
def save(n_clicks, text):
    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')


    if button_id[0] == 'Save_Post_btn':
        if n_clicks > 0:
            print("###################################   NEW POST  ########################################", '\n')

            # print(current_user.get_id())

            with open(main_path_data + "\\posts.json", "r") as file:
                param = []
                data = json.load(file)
                file.close()
                for k, v in data.items():
                    param.append(k)


                uu = open(main_path_data + "\\users.json", "r")
                user_data = json.load(uu)
                uu.close()
                user_data[session['username']]['last_req'] = time.strftime("%Y-%m-%d %H:%M")
                uf = open(main_path_data + "\\users.json", "w")
                json.dump(user_data, uf)
                uf.close()

                if not param:
                    next_id = 1
                    data[next_id] = {"text": text,
                                      "likes": 0,
                                     "like":{},
                                     "dislikes": 0,
                                     "dislike": {}
                                    }
                    f = open(main_path_data + "\\posts.json", "w")
                    json.dump(data, f)
                    f.close()
                else:
                    next_id = str(int(param[-1]) + 1)
                    data[next_id] = {"text": text,
                                      "likes": 0,
                                     "like": {},
                                     "dislikes": 0,
                                     "dislike": {}
                                    }
                    f = open(main_path_data + "\\posts.json", "w")
                    json.dump(data, f)
                    f.close()
                return [[i for i in Posts.posts()]]
        else:
            return [[i for i in Posts.posts()]]
    else:
        raise dash.exceptions.PreventUpdate


@dash_app.callback(
    [Output({'type': 'likes', 'index': MATCH}, 'children')],
    [Input({'type': 'like-button', 'index': MATCH}, 'n_clicks')],
    [State({'type': 'likes', 'index': MATCH}, 'children'),
     State({'type': 'like-button', 'index': MATCH}, 'id')]
)

def save_likes(n_clicks, n_likes, id):
    ctx = dash.callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate
    else:
        pass
    if n_clicks > 0:
        with open(main_path_data + "\\posts.json", "r") as file:
            data = json.load(file)
            file.close()

            list = data[id['index']]["like"]
            ses_user= session['username']

            uu = open(main_path_data + "\\users.json", "r")
            user_data = json.load(uu)
            uu.close()
            user_data[session['username']]['last_req'] = time.strftime("%Y-%m-%d %H:%M")
            uf = open(main_path_data + "\\users.json", "w")
            json.dump(user_data, uf)
            uf.close()

            if ses_user in list:
                del list[ses_user]
                newlikes = int(n_likes) - 1
                data[id['index']]["likes"] = newlikes
                data[id['index']]['last_time'] = time.strftime("%Y-%m-%d %H:%M")
                data[id['index']]["like"] = list
                f = open(main_path_data + "\\posts.json", "w")
                json.dump(data, f)
                f.close()
            else:
                d = {ses_user:{"date": time.strftime("%Y-%m-%d"), "like": 1}}
                list.update(d)
                newlikes = int(n_likes)+1
                data[id['index']]["likes"] = newlikes
                data[id['index']]['last_time'] = time.strftime("%Y-%m-%d %H:%M")
                data[id['index']]["like"] = list

                f = open(main_path_data + "\\posts.json", "w")
                json.dump(data, f)
                f.close()
        return [newlikes]
    else:
        raise dash.exceptions.PreventUpdate


@dash_app.callback(
    [Output({'type': 'dislikes', 'index': MATCH}, 'children')],
    [Input({'type': 'dislike-button', 'index': MATCH}, 'n_clicks')],
    [State({'type': 'dislikes', 'index': MATCH}, 'children'),
     State({'type': 'dislike-button', 'index': MATCH}, 'id')]
)

def save_dislikes(n_clicks, n_likes, id):
    ctx = dash.callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate
    else:
        pass
    if n_clicks > 0:
        with open(main_path_data + "\\posts.json", "r") as file:
            data = json.load(file)
            file.close()

            list = data[id['index']]["dislike"]
            ses_user= session['username']

            uu = open(main_path_data + "\\users.json", "r")
            user_data = json.load(uu)
            uu.close()
            user_data[session['username']]['last_req'] = time.strftime("%Y-%m-%d %H:%M")
            uf = open(main_path_data + "\\users.json", "w")
            json.dump(user_data, uf)
            uf.close()

            if ses_user in list:
                del list[ses_user]
                newlikes = int(n_likes) - 1
                data[id['index']]["dislikes"] = newlikes
                data[id['index']]['last_time'] = time.strftime("%Y-%m-%d %H:%M")
                data[id['index']]["dislike"] = list
                f = open(main_path_data + "\\posts.json", "w")
                json.dump(data, f)
                f.close()
            else:
                d = {ses_user:{"date": time.strftime("%Y-%m-%d"), "dislike": 1}}
                list.update(d)
                newlikes = int(n_likes)+1
                data[id['index']]["dislikes"] = newlikes
                data[id['index']]['last_time'] = time.strftime("%Y-%m-%d %H:%M")
                data[id['index']]["dislike"] = list

                f = open(main_path_data + "\\posts.json", "w")
                json.dump(data, f)
                f.close()
        return [newlikes]
    else:
        raise dash.exceptions.PreventUpdate


if __name__ == '__main__':
    server.run()