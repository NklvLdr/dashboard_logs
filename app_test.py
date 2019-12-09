from flask import Flask, render_template, request

import plotly
import plotly.graph_objs as go
from plotly.subplots import make_subplots

import pandas as pd
import numpy as np
import json

from viz_methods import *

app = Flask(__name__)

df = pd.read_csv('../senders.csv')
df.dat = pd.to_datetime(df.dat)
edge_list = pd.read_csv('../edge_list.csv')
centrality = pd.read_csv('../centrality.csv')
academy_emails = pd.read_csv('../academy_emails.csv') #emails with centrality measurements and grades
prepared_stats = prepare_activity_stats(df)

@app.route('/')
def index():
    centralities = centralities_subplots(centrality)
    c_table = centrality_table(centrality)
    return render_template('index.html',
                            centralities=centralities,
                            c_table=c_table)

@app.route('/update_grade_centralities')
def process():
    grade = request.args.get('grade', 'all')
    centrality_parameter = request.args.get('centrality', 'betw')
    if centrality_parameter == 'eigenvalue':
        centrality_parameter = 'eig'
    else:
        centrality_parameter = 'betw'
    '''
    if grade == 'all':
        return centralities_subplots(centrality, centrality=centrality_parameter, selected_grade=None)
    else:
        grade = int(grade)
        return centralities_subplots(centrality, centrality=centrality_parameter, selected_grade=grade)
    '''

    #modification of centralities subplots
    mess = {}
    if grade == 'all':
        mess[1] = centralities_subplots(centrality, centrality=centrality_parameter, selected_grade=None) #without returning json
    else:
        mess[1] = centralities_subplots(centrality, centrality=centrality_parameter, selected_grade=int(grade)) #without returning json
    
    #modification of centralities table
    mess[2] = centrality_table(centrality, centrality=centrality_parameter, grade=grade)

    return json.dumps(mess)

@app.route('/activity')
def activity():
    activity_by_day = activity_plot(df, key_email=None, academy_mails=academy_emails['0'])
    table_with_stats = activity_stats(prepared_stats)
    return render_template('activity.html',
                            activity_by_day=activity_by_day,
                            table_with_stats=table_with_stats)

@app.route('/update_activity')
def update_p2p():
    sort_param = request.args.get('sort_param', None)
    if sort_param:
        return activity_stats(prepared_stats, sort_by=sort_param)

    email = request.args.get('email', None)
    if email:
        email = json.loads(email)
        return activity_plot(df, key_email=email)

@app.route('/interactions')
def interactions():
    p2p_activity = p2p_activity_barplot(edge_list, key_email='email60')
    communication_array, x_labels, y_labels = prepare_for_communication_heatmap(edge_list, centrality_data=centrality, list_of_emails=None, sort_nodes='grade')
    heatmap_graph = communication_heatmap(communication_array, x_labels=x_labels, y_labels=y_labels, max_values=None)
    return render_template('interactions.html',
                            p2p_activity=p2p_activity,
                            heatmap_graph=heatmap_graph)

@app.route('/interactions/update')
def p2p_interaction_update():
    email = request.args.get('email', None)
    return p2p_activity_barplot(edge_list, key_email=email)

@app.route('/heatmap/update')
def heatmap_update():
    list_of_emails = json.loads(request.args['emails'])
    communication_array, x_labels, y_labels = prepare_for_communication_heatmap(edge_list, list_of_emails=list_of_emails)
    heatmap_graph = communication_heatmap(communication_array, x_labels=x_labels, y_labels=y_labels, max_values=50)
    return heatmap_graph

@app.route('/heatmap/users')
def send_users():
    return json.dumps(academy_emails['0'].to_list())

@app.route('/update_timelines')
def update_timelines():
    new_mail = request.args['selected']
    return activity_plot(df, key_email=new_mail)





    
        

if __name__ == '__main__':
    app.run(debug=True)