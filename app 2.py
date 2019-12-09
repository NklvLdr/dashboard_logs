from flask import Flask, render_template, request

import plotly
import plotly.graph_objs as go
import plotly.express as px

import pandas as pd
import numpy as np
import json

app = Flask(__name__)

df = pd.read_csv('WA_Fn-UseC_-HR-Employee-Attrition.csv', sep=';')
df.Attrition.replace({'Yes':1, 'No':0}, inplace=True)

@app.route('/')
def index():
    bar = create_barplot()
    scatter = create_scatterplot()
    heatmap = create_heatmap(df)
    return render_template('index3.html',
                            barplot=bar,
                            scatterplot=scatter,
                            heatmapplot=heatmap)

@app.route('/bar')
def create_feature():
    feature = request.args['selected']
    print(feature)
    d = df[df.Gender==feature]
    print(d.shape)
    return create_heatmap(d)


def create_heatmap(df):
    pivot = df.pivot_table(index='Department', columns='JobLevel', aggfunc='count', values='Attrition')
    left = df.pivot_table(index='Department', columns='JobLevel', aggfunc='sum', values='Attrition')
    headmap_data = (left/pivot).round(2)
    color = px.colors.sequential.Darkmint
    data = [go.Heatmap(
        z = headmap_data.values,
        x = ['1st Grade','2nd Grade', '3d Grade', '4th Grade', ' 5th Grade'],
        y = headmap_data.index,
        colorscale=color)]
    return json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

def create_barplot():
    data = [
        go.Histogram(
            x=df.YearsAtCompany
        )
    ]
    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

def create_scatterplot():
    N = 1000
    random_x = np.random.randn(N)
    random_y = np.random.randn(N)

    # Create a trace
    data = [go.Scatter(
        x = random_x,
        y = random_y,
        mode = 'markers'
    )]

    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

if __name__ == '__main__':
    app.run(debug=True)