import pandas as pd
import numpy as np
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from datetime import timedelta


def return_figures():
    """Creates plotly visualizations

    Args:
        None

    Returns:
        list (dict): list containing the four plotly visualizations

    """


    ##### Importing and filtering data #####
    
    df = pd.read_csv('data/serie_ibov_diario.csv', parse_dates=['Data'], 
                     index_col='Data')
    #df.head()
    
    # Avaliando qual é o último dia útil do ano anterior para fazer o pct_change()
#    df['1999-12'].tail(1)
    df = df.loc['1999-12-30':,'Ibov']



    ##### Defining plots parameters #####
    
    # Buttons for navegating through time frames
    my_buttons = [
        
    {
     'label': "Dia", 
     'method': "update", 
     'args': [{"visible": [True, False, False, False]}]
     },
    
    {
     'label': "Semana", 
     'method': "update", 
     'args': [{"visible": [False, True, False, False]}]
     },
    
    {
     'label': "Mês", 
     'method': "update", 
     'args': [{"visible": [False, False, True, False]}]
     },
    
    {
     'label': "Ano", 
     'method': "update", 
     'args': [{"visible": [False, False, False, True]}]
     },
    
    ]
    
    # Cut-points and labels for frequency plot
    cut_values = [-1, -0.1, -0.05, -0.015, -0.005, 0.005, 0.015, 0.05, 0.1, 1]
    cut_labels = ['abaixo de -10%', '-10% a -5%', '-5% a -1,5%', '-1,5% a -0,5%',
                  '-0,5% a 0,5%', '0,5% a 1,5%','1,5% a 5%', '5% a 10%',
                  'acima de 10%']
    
    # Colors for bottom 5 (red) and top 5 (green) returns
    bar_colors = str(5*'#EF553B ' + 5*'#00CC96 ').split() # 5 red and 5 green
    
    # Time frames: daily (D), weekly(W), monthly (M) and annual (A)
    list_time_frames = ['D','W','M','A']
    
    # Creating dictionary with lists of returns by time frame
    returns ={}
    
    for time_frame in list_time_frames:
        returns_time_frame = df.resample(time_frame).last().pct_change().dropna()
        returns[time_frame] = round(returns_time_frame,4)

    returns['W'].index = returns['W'].index - timedelta(days=2)
    
    ### Creating plots ###
    
    # Defining the figure frame for 4 plots
    fig = make_subplots(rows=2, cols=2, vertical_spacing = 0.15, 
                        horizontal_spacing = 0.05,
                        subplot_titles=['Série temporal','Distribuição', 
                                        'Frequência por faixa',
                                        '5 menores e 5 maiores'])
        
    
    # Line plots of returns for each time frame
    for time_frame in list_time_frames:
        
        hover = [str(t)+'<br>'+str(r) for t, r in 
                 zip(returns[time_frame].index.date, returns[time_frame])]
        
        if time_frame=='D':
    
            fig.add_trace(
                go.Scatter(x=returns[time_frame].index, y=returns[time_frame],
                           name='', hoverinfo='text', hovertext=hover,
                           showlegend=False, mode='lines'),
                row=1, col=1
                )
            
        elif time_frame=='W':    
            
            fig.add_trace(
                go.Scatter(x=returns[time_frame].index, y=returns[time_frame],
                           name='', hoverinfo='text', hovertext=hover,
                           showlegend=False, mode='lines', visible=False),
                row=1, col=1
                )
            
        elif time_frame=='A':    
            
            x_values = returns[time_frame].index.year
            hover = [f'({y}, {r})' for y, r in zip(x_values, returns[time_frame])]
            
            fig.add_trace(
                go.Scatter(x=x_values, y=returns[time_frame],
                           name='', hoverinfo='text', hovertext=hover, 
                           showlegend=False, mode='lines', visible=False),
                row=1, col=1
                )
        else:
            
            fig.add_trace(
                go.Scatter(x=returns[time_frame].index, y=returns[time_frame], name='', 
                           showlegend=False, mode='lines', visible=False),
                row=1, col=1
                )
    
    
    # Boxplot of returns for each time frame
    for time_frame in list_time_frames:

        if time_frame=='D':
            fig.add_trace(
                go.Box(x=returns[time_frame], name='', showlegend=False, 
                       marker_color='#FFA15A'),
                row=1, col=2
                )
        else:
            fig.add_trace(
                go.Box(x=returns[time_frame], name='', showlegend=False, 
                       marker_color='#FFA15A', visible=False),
                row=1, col=2
                )

    
    # Bar chart with frequencies for each time frame
    for time_frame in list_time_frames:    
        
        freq = pd.Series(pd.cut(returns[time_frame], cut_values).value_counts(normalize=True).sort_index())
        hover = [str(round(p*100,1))+'%' for p in freq]        
        
        if time_frame=='D':
    
            fig.add_trace(
                go.Bar(x=cut_labels, y=freq, showlegend=False, name='', 
                       marker_color='#AB63FA', hoverinfo='text',  hovertext=hover), 
                row=2, col=1
                )
        else:
            
            fig.add_trace(
                go.Bar(x=cut_labels, y=freq, showlegend=False, name='', 
                       marker_color='#AB63FA', hoverinfo='text',  hovertext=hover,
                       visible=False), 
                row=2, col=1
                )

    # Bar chart with 5 highest (best) and 5 lowest (worst) returns for each 
    # time frame
    for time_frame in list_time_frames:    
        
        best_worst = pd.Series(returns[time_frame].sort_values().head())
        best_worst = best_worst.append(returns[time_frame].sort_values().tail())
        best_worst.index = best_worst.index.date
    
        if time_frame=='M': x_values = [x.strftime("%Y-%m") for x in best_worst.index]
        elif time_frame=='A': x_values = [x.strftime("%Y") for x in best_worst.index]
        else: x_values = [str(x) for x in best_worst.index]
        
        if time_frame=='D':
        
            fig.add_trace(
                go.Bar(x=np.array(x_values), y=best_worst, name='', showlegend=False, 
                       marker_color=bar_colors), 
                row=2, col=2
                )
    
        else:
    
            fig.add_trace(
                go.Bar(x=np.array(x_values), y=best_worst, name='', showlegend=False, 
                       marker_color=bar_colors, visible=False), 
                row=2, col=2
                )

    
        # Adjusting bar charts x-axis labels
        fig.update_xaxes(row=2, col=1, tickangle=-45)
        fig.update_xaxes(row=2, col=2, tickangle=-45 , type='category')
        
        
    # Adding predefined buttons
    fig.update_layout(
        {
            
#        'title': {
#            'text': 'Retornos históricos Ibovespa (2000-2021)', 
#                   'font':{'size':20, 'color':'#3366CC'}, 
#                   'x': 0.5, 'y': 0.95
#                   },
        
        'updatemenus': [{
            'showactive': True, 
            'active': 0, 
            'type': 'buttons',
            'direction': 'down',
            'buttons': my_buttons,
            'bgcolor':'#E2E2E2',
            'bordercolor':'darkgrey'
            }]
        
        }
        
    )
    
    fig.update_annotations(
        font_color='#0D2A63', 
        font_family="Old Standard TT",
        font_size=21)

    fig.update_layout(
        autosize=False, 
        width=1200,
        height=700,
        margin=dict(l=20, r=20, b=20, t=45),
        #paper_bgcolor="LightSteelBlue",
        paper_bgcolor='rgb(203,213,232)',
        hoverlabel=dict(bgcolor="white")
        )
    

    # append all charts to the figures list
    figures = []
    figures.append(dict(data=fig, layout=fig.layout))

    return figures

#return_figures()
