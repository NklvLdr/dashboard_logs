import plotly
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import json
import pandas as pd
import numpy as np

def prepare_activity_stats(senders):
    e = senders[senders.sender.str.contains('rosatom-academy.ru')].copy()
    off_time = e[(e.dat.dt.hour<7) | (e.dat.dt.hour>19)].groupby(by=['sender',e.dat.dt.hour]).size().groupby(level='sender').sum()
    off_time = off_time.reset_index()
    off_time.columns=['sender','off_time']
    
    all_mess = e.groupby(by='sender').size()
    all_mess = all_mess.reset_index()
    all_mess.columns=['sender','all_mess']
    
    mean = e[(e['dat'].dt.weekday.isin([0,1,2,3,4]))][['sender','dat']].groupby(by=['sender', e.dat.dt.day]).size().groupby(level='sender').mean()
    mean = mean.reset_index()
    mean.columns=['sender','mean']
    
    weekends = e[(e['dat'].dt.weekday.isin([5,6]))][['sender','dat']].groupby(by=['sender', e.dat.dt.day]).size().groupby(level='sender').sum().reset_index()
    weekends.columns=['sender','weekends']
    
    e = pd.merge(off_time, all_mess, left_on='sender', right_on='sender')
    e = pd.merge(e, mean, left_on='sender', right_on='sender')
    e = pd.merge(e, weekends, left_on='sender', right_on='sender')
    
    return e

def activity_stats(mess, sort_by=None, grade='all'):
    #df = mess if grade=='all' else mess[mess['grade']==grade]
    df = mess
    if sort_by:
        df.sort_values(by=sort_by, inplace=True, ascending=False)
    fig = go.Figure()
    fig.add_trace(
        go.Table(
            header=dict(values=list(['Email', 'Всего сообщений', 'Во внерабочее время','На выходных','В среднем за рабочий день']),
                fill_color='rgb(250, 105, 0)',
                align='left'),
            cells=dict(values=[df.sender,
               df.all_mess,
               df.off_time,
               df.weekends,
               df['mean'].round(1)],
            fill_color='rgb(224,238,241)',align='left'))
                             )
    fig.update_layout(height=300, margin=dict(l=0, r=0, t=0, b=10))

    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def centrality_table(centrality_df, centrality='betw', grade='all'):
    df = centrality_df if grade=='all' else centrality_df[centrality_df['grade']==int(grade)]

    df.sort_values(by=centrality, inplace=True, ascending=False)
    fig = go.Figure(data=[go.Table(
    header=dict(values=list(['Email', 'Грэйд', 'Посредничество' if centrality=='betw' else 'Влиятельность']),
                fill_color='rgb(250, 105, 0)',
                align='left'),
    cells=dict(values=[df.email,
                       df.grade,
                       df[centrality].round(3)],
               fill_color='rgb(224,238,241)',
               align='left'))
                         ])
    fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=600)
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def prepare_for_communication_heatmap(edge_list, centrality_data=None, list_of_emails=None, sort_nodes=False):
    if list_of_emails:
        e = edge_list[(edge_list.sources.isin(list_of_emails)) & edge_list.destinations.isin(list_of_emails)].reset_index(drop=True)
    else:
        e = edge_list[(edge_list.sources.str.contains('@rosatom-academy.ru')) & edge_list.destinations.str.contains('@rosatom-academy.ru')].reset_index(drop=True)[:1000]
        e = e[e.destinations.isin(e.sources.unique())]
        
    if isinstance(centrality_data, pd.DataFrame):
        e = pd.merge(e, centrality_data, left_on='sources', right_on='email')
        if sort_nodes:
            e.sort_values(by=sort_nodes, inplace=True)
        
    e = e.pivot_table(values='weights', index='sources', columns='destinations').fillna(0)
    x_labels = e.columns.to_list()
    y_labels = e.index.to_list()
    return e.values, x_labels, y_labels
    
def communication_heatmap(array, x_labels=None, y_labels=None, max_values=None):
    if y_labels:
        assert array.shape[0]==len(y_labels)
    if x_labels:
        assert array.shape[1]==len(x_labels)

    if max_values:
        array_max = array.max()
        if max_values > array_max:
            max_values = array_max
        array = np.where(array>max_values, max_values, array)
        
    fig = go.Figure(data=go.Heatmap(z=array,
                                    x=[x.split('@')[0] for x in x_labels],
                                    y=[y.split('@')[0] for y in y_labels],
                                   colorscale=[[0, 'rgb(224,238,241)'],[1, 'rgb(250,105,0)']]))
    #fig.update_layout(height=300, width=300)
    fig.update_layout(margin=dict(l=0,t=0, b=0, r=0))
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


def centralities_subplots(e, centrality='betw',selected_grade=None):

    fig = make_subplots(rows=2, cols=1,
                        vertical_spacing=0.15,
                        horizontal_spacing=0.05,
                        specs=[[{}],[{}]])
    if selected_grade:
        e1 = e[e.grade != selected_grade]
        e2 = e[e.grade == selected_grade] 
        
        fig.append_trace(go.Scatter(x=e1['betw'], y=e1['eig'], mode='markers', hovertext=e1['email'],
                                    showlegend = False, marker_color='rgb(105,210,231)'),
                         row=1, col=1)
        fig.append_trace(go.Scatter(x=e2['betw'], y=e2['eig'], mode='markers', hovertext=e2['email'],
                                    showlegend = False, marker_color='rgb(250,105,0)'),
                         row=1, col=1)
        
        x = sorted(e2.grade.unique())
        fig.add_trace(go.Box(y=e2[centrality].values,
                                 name=str(selected_grade),
                                 marker_color = 'rgb(250,105,0)', showlegend=False, boxpoints='all', jitter=0.3), row=2, col=1)

    else:
        fig.append_trace(go.Scatter(x=e['betw'], y=e['eig'], mode='markers', hovertext=e['email'],
                                    showlegend = False, marker_color='rgb(250,105,0)'),
                         row=1, col=1)
        x = sorted(e.grade.unique())
        for grade in x:
            fig.add_trace(go.Box(y=e[e.grade==grade][centrality].values,
                                 name=str(grade),
                                 marker_color = 'rgb(250,105,0)', showlegend=False, boxpoints=None, jitter=0.3), row=2, col=1)
        
    #fig.update_xaxes(showticklabels=False, row=1, col=2)
    fig.update_xaxes(title_text="Посредничество", row=1, col=1)
    fig.update_xaxes(title_text="Грейды", row=2, col=1)
    
    fig.update_yaxes(title_text="Влиятельность", automargin = False, row=1, col=1)
    fig.update_yaxes(title_text="Посредничество" if centrality=='betw' else 'Влиятельность', row=2, col=1)
    #fig.update_layout(showlegend=False, row=1, col=1)
    #height=400, width=1000, 
    fig.update_layout(margin=dict(l=00, r=00, t=10, b=00), plot_bgcolor='rgb(224,238,241)', height=600)
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def centrality_scatter(e):
    betw_75 = e.betw.quantile(0.90)
    betw_max = e.betw.max()+0.01
    eig_75 = e.eig.quantile(0.90)
    eig_max = e.eig.max()+0.025

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=e['betw'], y=e['eig'], mode='markers', hovertext=e['email']))
    fig.add_trace(go.Scatter(x=[betw_75, betw_75], y=[0,eig_max], mode='lines', hoverinfo='skip',
                            line=dict(color="LightSeaGreen")))
    fig.add_trace(go.Scatter(x=[0, betw_max], y=[eig_75,eig_75], mode='lines', hoverinfo='skip',
                            line=dict(color="LightSeaGreen")))

    fig.update_layout(height=450, width=450)
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def p2p_activity_barplot(edge_list, key_email=None):
    e = edge_list[(edge_list.sources.str.contains(key_email)) | (edge_list.destinations.str.contains(key_email))].sort_values(by='weights', ascending=False).reset_index(drop=True)
    all_mails = list(set(list(e['sources'].unique())+list(e['destinations'].unique())))
    all_mails.pop(all_mails.index(key_email))
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
    alls = alls[:20]
    
    x = [x[0].split('@')[0] for x in alls]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=x, y=[x[1] for x in alls], name='Отправлено',
                        hovertemplate = 'Отправлено: %{text}<extra></extra>',
                         text = [x[1] for x in alls],
                         marker_color='rgb(250,105,0)'))
    fig.add_trace(go.Bar(x=x, y=[-x[2] for x in alls], name='Получено',
                         hovertemplate = 'Получено: %{text}<extra></extra>',
                         text = [x[2] for x in alls],
                         marker_color='rgb(105,210,231)'
                        ))

    fig.update_layout(height=400, width=900, barmode='relative', margin=dict(l=0,t=10,b=10, r=0),
                    legend=dict(orientation='h',yanchor='top',xanchor='center',y=1.1,x=0.5),
                    plot_bgcolor='rgb(224,238,241)')
    fig.update_yaxes(showticklabels=False)
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def activity_plot(d, key_email=None, academy_mails=None):
    
    def day_activity(d, key_email=None, academy_mails=academy_mails):
        if key_email==None:
            t = d[(d['dat'].dt.weekday.isin([0,1,2,3,4])) & (d.sender.isin(academy_mails))][['sender','dat']]
        else:
            t = d[(d['dat'].dt.weekday.isin([0,1,2,3,4])) & (d.sender.str.contains(key_email))][['sender','dat']]
        t = t.groupby(by=['sender',d['dat'].dt.weekday, d['dat'].dt.hour]).size()
        return t.groupby(level=[2]).mean()

    def week_activity(d, key_email=None, academy_mails=academy_mails):
        if key_email==None:
            t = d[d.sender.isin(academy_mails)].groupby(by=['sender',d['dat'].dt.weekday]).size()
        else:
            t = d[d.sender.str.contains(key_email)].groupby(by=['sender',d['dat'].dt.weekday]).size()
        return t.groupby(level=1).mean()

    def calendar_activity(d, key_email=None, academy_mails=academy_mails):
        if key_email==None:
            t = d[d.sender.isin(academy_mails)].copy()
        else:
            t = d[d.sender.str.contains(key_email)].copy()
        t = t.groupby(by=[t.sender,t.dat.dt.strftime('%y-%m-%d')]).size()
        t = t.groupby(level=1).mean().sort_index()
        idx = pd.date_range(start=d.dat.min(), end=d.dat.max())
        return t.reindex([x.strftime('%y-%m-%d') for x in idx], fill_value=0)

    company_day_mean = day_activity(d, academy_mails=academy_mails).rolling(1).mean()
    company_week_mean = week_activity(d, academy_mails=academy_mails).rolling(1).mean()    
    company_calendar_mean = calendar_activity(d, academy_mails=academy_mails).rolling(1).mean()
    
    if key_email!=None:
        employee_day_week = day_activity(d, key_email=key_email).rolling(1).mean()
        employee_week_week = week_activity(d, key_email=key_email).rolling(1).mean()
        employee_calendar_week = calendar_activity(d, key_email=key_email).rolling(1).mean()

    fig = make_subplots(rows=2, cols=2,
                        y_title='Среднее число сообщений',
                        vertical_spacing=0.1,
                        horizontal_spacing=0.05,
                        specs=[[{"colspan": 2}, None],
                        [{}, {}]],
                        )
    fig.append_trace(go.Scatter(x=company_calendar_mean.index.to_list(),
                             y=company_calendar_mean,
                        mode='lines',
                        name='В среднем по Академии',
                        line_color='rgb(105,210,231)'), row=1, col=1)
    fig.append_trace(go.Scatter(x=company_day_mean.index.to_list(),
                             y=company_day_mean,
                        mode='lines',
                        name='В среднем по Академии',
                        line_color='rgb(105,210,231)',
                        showlegend=False), row=2, col=1)
    fig.append_trace(go.Scatter(x=company_week_mean.index.to_list(),
                             y=company_week_mean,
                        mode='lines',
                        name='В среднем по Академии',
                        line_color='rgb(105,210,231)',
                        showlegend=False), row=2, col=2)
    if key_email!=None:
        fig.append_trace(go.Scatter(x=employee_calendar_week.index.to_list(),
                                 y=employee_calendar_week,
                            mode='lines',
                            name='Работник',
                            line_color='rgb(250, 105, 0)',
                            showlegend=True), row=1, col=1)
        fig.append_trace(go.Scatter(x=employee_day_week.index,
                                 y=employee_day_week,
                            mode='lines',
                            name='Работник',line=dict(color="rgb(250, 105, 0)"),showlegend=False), row=2, col=1)
        fig.append_trace(go.Scatter(x=employee_week_week.index.to_list(),
                                 y=employee_week_week,
                            mode='lines',
                            name='Работник',
                            line_color='rgb(250, 105, 0)',showlegend=False), row=2, col=2)

    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0),
                    legend=dict(orientation='h',yanchor='top',xanchor='center',y=1.1,x=0.5),
                    plot_bgcolor='rgb(224,238,241)')

    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)