from flask import Flask, render_template, request

import plotly
import plotly.graph_objs as go
import plotly.express as px

import pandas as pd
import numpy as np
import json

app = Flask(__name__)

df = pd.read_csv('senders.csv')
df.dat = pd.to_datetime(df.dat)

edge_list = pd.read_csv('edge_list.csv')

def p2p_activity_barplot(e, key_mail=None):
    all_mails = list(set(list(e['sources'].unique())+list(e['destinations'].unique())))
    all_mails.pop(all_mails.index(key_mail))
    label = []
    sended = []
    recieved = []
    for mail in all_mails:
        label.append(mail)
        p = e[e.destinations.str.contains(mail)]['weights']
        if p.shape[0] == 0:
            sended.append(0)
        else:
            sended.append(p.values[0])
        p = e[e.sources.str.contains(mail)]['weights']
        if p.shape[0] == 0:
            recieved.append(0)
        else:
            recieved.append(p.values[0]) 
    alls = sorted(zip(label, sended, recieved), key=lambda x: x[1]+x[2], reverse=True)

    x = [x[0] for x in alls]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=x, y=[x[1] for x in alls], name='Отправлено'))
    fig.add_trace(go.Bar(x=x, y=[-x[2] for x in alls], name='Получено'))

    fig.update_layout(barmode='relative', title_text=key_mail)
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def montly_activity(d):

    def month_day_activity(d, key_email=None):
        if key_email==None:
            key_email = 'rosatom-academy.ru'
        t = d[d.sender.str.contains(key_email)].copy()
        t = t.groupby(by=[t.sender,t.dat.dt.strftime('%y-%m-%d')]).size()
        t = t.groupby(level=1).mean().sort_index()
        idx = pd.date_range(start=d.dat.min(), end=d.dat.max())
        return t.reindex([x.strftime('%y-%m-%d') for x in idx], fill_value=0)

    all_company = d[d.sender.str.contains('rosatom-academy.ru')].groupby(by=['sender',d.dat.dt.strftime('%y-%m-%d')]).size().reset_index()

    all_company = all_company[all_company[0]<100].sort_values(by='dat')

    company_mean = month_day_activity(d).rolling(2).mean()
    personal_mean = month_day_activity(d, key_email='email58@rosatom-academy.ru').rolling(2).mean()

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=all_company['dat'],
                             y=all_company[0],
                        mode='markers',
                        name='Все работники Академии'))
    fig.add_trace(go.Scatter(x=company_mean.index,
                             y=company_mean,
                        mode='lines',
                        name='В среднем по компании'))
    fig.add_trace(go.Scatter(x=personal_mean.index,
                             y=personal_mean,
                        mode='lines',
                        name='Работник'))
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def week_activity(d):

    def month_day_activity(d, key_email=None):
        if key_email==None:
            key_email = 'rosatom-academy.ru'
        t = d[d.sender.str.contains(key_email)].groupby(by=['sender',d['dat'].dt.weekday]).size()
        return t.groupby(level=1).mean()

    company_week_mean = month_day_activity(d)
    employee_week = month_day_activity(d, key_email='email174@rosatom-academy.ru')
    all_employees = d[d.sender.str.contains('rosatom-academy.ru')].groupby(by=['sender',d['dat'].dt.weekday]).size().reset_index()


    fig = go.Figure()


    fig.add_trace(go.Scatter(x=all_employees['dat'],
                             y=all_employees[0],
                        mode='markers',
                        name='Все работники Академии'))

    fig.add_trace(go.Scatter(x=company_week_mean.index,
                             y=company_week_mean,
                        mode='lines',
                        name='В среднем по Академии'))

    fig.add_trace(go.Scatter(x=employee_week.index,
                             y=employee_week,
                        mode='lines',
                        name='Работник'))
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def day_activity(d):
    def activity(d, key_email=None):
        if key_email==None:
            key_email = 'rosatom-academy.ru'
        t = d[(d['dat'].dt.weekday.isin([0,1,2,3,4])) & (d.sender.str.contains(key_email))][['sender','dat']]
        t = t.groupby(by=['sender',d['dat'].dt.weekday, d['dat'].dt.hour]).size()
        return t.groupby(level=[2]).mean()
    all_employees = d[(d['dat'].dt.weekday.isin([0,1,2,3,4])) & (d.sender.str.contains('rosatom-academy.ru'))][['sender','dat']]
    all_employees = all_employees.groupby(by=['sender',all_employees['dat'].dt.hour]).size().reset_index()
    all_employees = all_employees[all_employees[0]<150]
    company_week_mean = activity(d).rolling(2).mean()
    employee_week = activity(d, key_email='email174@rosatom-academy.ru').rolling(2).mean()


    fig = go.Figure()

    fig.add_trace(go.Scatter(x=all_employees['dat'],
                             y=all_employees[0],
                        mode='markers',
                        name='Все работники Академии'))

    fig.add_trace(go.Scatter(x=company_week_mean.index.to_list(),
                             y=company_week_mean,
                        mode='lines',
                        name='Все работники Академии'))

    fig.add_trace(go.Scatter(x=employee_week.index,
                             y=employee_week,
                        mode='lines',
                        name='Работник'))
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    

@app.route('/')
def index():
    key_mail = 'email674@rosatom.ru'
    e = edge_list[(edge_list.sources.str.contains(key_mail)) | (edge_list.destinations.str.contains(key_mail))].sort_values(by='weights',ascending=False).reset_index(drop=True)

    p2p_bar = p2p_activity_barplot(e,key_mail=key_mail)
    activity_by_month = montly_activity(df)
    activity_by_week = week_activity(df)
    activity_by_day = day_activity(df)
    return render_template('index3.html',
                            p2p_bar=p2p_bar,
                            acitivity_by_month=activity_by_month,
                            activity_by_week=activity_by_week,
                            activity_by_day=activity_by_day)

@app.route('/update')
def update_plots():
    key_mail = request.args['selected']
    e = edge_list[(edge_list.sources.str.contains(key_mail)) | (edge_list.destinations.str.contains(key_mail))].sort_values(by='weights',ascending=False).reset_index(drop=True)
    print(key_mail)
    return p2p_activity_barplot(e, key_mail=key_mail)


if __name__ == '__main__':
    app.run(debug=True)