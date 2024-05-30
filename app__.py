import dash
from dash import html, dcc, Input, Output,dash_table
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
import os
import json
from shapely.geometry import shape, MultiPolygon

import psutil
import time
import threading

# メモリ使用量を記録する関数
def log_memory_usage():
    process = psutil.Process(os.getpid())
    while True:
        mem_info = process.memory_info()
        print(f"Memory Usage: {mem_info.rss / 1024 ** 2:.2f} MB")
        time.sleep(5)  # 5秒ごとにメモリ使用量を記録

# メモリ使用量を記録するスレッドを開始
memory_thread = threading.Thread(target=log_memory_usage)
memory_thread.daemon = True
memory_thread.start()


# データの前処理
# --------------------------------------------------------------
persona = pd.read_csv("事業所名で集計.csv", usecols=["pref", "city", "category", "sub_category", "genre", "name", "count", "num_uu_prefcity"], dtype={"pref": "str", "city": "str", "category": "str", "sub_category": "str", "genre": "str", "name": "str", "count": "int32", "num_uu_prefcity": "int32"})
persona['pref_city'] = persona['pref'] + persona['city']
persona.drop(columns=["pref", "city"], inplace=True)
# --------------------------------------------------------------

# ドロップダウンのオプション生成
# --------------------------------------------------------------
def generate_options(df, column):
    unique_values = df[[column]].drop_duplicates().sort_values(column)
    return [{'label': row[column], 'value': row[column]} for index, row in unique_values.iterrows()]

options_pref_city_1 = generate_options(persona, 'pref_city')
options_category = generate_options(persona, 'category')
options_subcategory = generate_options(persona, 'sub_category')
options_genre = generate_options(persona, 'genre')
# --------------------------------------------------------------


# Dashアプリケーションの初期化
# --------------------------------------------------------------
app = dash.Dash(__name__)
# --------------------------------------------------------------

# Dashアプリケーションのレイアウト設定
# --------------------------------------------------------------
app.layout = html.Div([ 
    html.P("Blogwatcher  AreaSurvey", style={'height': '50px','color': '#4A90E2', 'display': 'flex', 'alignItems': 'center','fontFamily': 'Arial, sans-serif','fontSize': '40px','margin': '0'}),
    html.P("賃貸Ｄｉｖ東日本東海賃部東北Ｇ", style={'height': '20px',  'color': '#4A90E2', 'display': 'flex', 'alignItems': 'center','fontFamily': 'Arial, sans-serif','fontSize': '10px','margin': '0'}),
    html.Div([
        html.P("事業所(中分類)の滞在分析", style={'height': '40px', 'backgroundColor': '#4A90E2', 'color': 'white','display': 'flex', 'alignItems': 'center','fontFamily': 'Arial, sans-serif','fontWeight': 'bold'}),
        html.Div([
            html.Div([
                html.P("居住地", style={'margin': '0 10px 0 0', 'color': '#4A90E2','display': 'flex', 'alignItems': 'center','fontFamily': 'Arial, sans-serif'}),
                dcc.Dropdown(
                    id='#1_dropdown',
                    options=options_pref_city_1,
                    value="宮城県仙台市青葉区",
                    style={"flex": "1"},
                ),
            ], style={"display": "flex", "alignItems": "center","width":"25%", "margin": '0 10px 0 10px'}),
            html.Div([
                html.P("事業所の大分類", style={'margin': '0 10px 0 0', 'color': '#4A90E2','display': 'flex', 'alignItems': 'center','fontFamily': 'Arial, sans-serif'}),
                dcc.Dropdown(
                    id='#2_dropdown',
                    options=options_category,
                    value=[],
                    multi=True,
                    style={"flex": "1"},
                ),
            ], style={"display": "flex", "alignItems": "center","width":"75%", "margin": '0 10px 0 10px'}),
        ], style={"display": "flex", "justifyContent": "space-around", 'height': '300px'}),
        
        html.Div([
            dcc.Graph(id='#1_graph', style={'display': 'inline-block', 'width': '98%','height': '95%'}),
        ], style={"display": "flex","justifyContent": "space-around", 'height': '700px'}),

        html.Div([
            html.Div([
                html.P("事業所の中分類", style={'margin': '0 10px 0 0', 'color': '#4A90E2','display': 'flex', 'alignItems': 'center','fontFamily': 'Arial, sans-serif'}),  # 要素間のマージンを設定
                dcc.Dropdown(
                    id='#3_dropdown',
                    options=[],
                    value=None,
                    style={"flex": "1"},
                ),
            ], style={"display": "flex", "alignItems": "center","width":"50%", "margin": '0 10px 0 10px'}),
            html.Div([
                html.P("事業所の小分類", style={'margin': '0 10px 0 0', 'color': '#4A90E2','display': 'flex', 'alignItems': 'center','fontFamily': 'Arial, sans-serif'}),  # 要素間のマージンを設定
                dcc.Dropdown(
                    id='#4_dropdown',
                    options=[],
                    value=None,
                    style={"flex": "1"},
                ),
            ], style={"display": "flex", "alignItems": "center","width":"50%", "margin": '0 10px 0 10px'}),
        ], style={"display": "flex", "justifyContent": "space-around", 'height': '100px'}),

        html.Div([
            dash_table.DataTable(
                id='#1_table',
                columns=[{"name": i, "id": i} for i in ["category", "sub_category", "genre", "name", "score"]],
                data=[],
                filter_action="native",
                sort_action="native",
                fixed_rows={'headers': True},
                page_size=20,
                style_table={'width': '98%', 'height': '95%'},
                style_cell={'textAlign': 'left'},
            ),
        ], style={"display": "flex","justifyContent": "space-around", 'height': '700px'}),
    ],
    style={"backgroundColor": "#F0F4F8",'height': '2000px'},
    ),
])

# #1_graph
# --------------------------------------------------------------
@app.callback(
    Output('#1_graph', 'figure'),
    [Input('#1_dropdown', 'value'), Input('#2_dropdown', 'value')]
)
def update_graph_1(selected_pref_city, selected_category):
    if not selected_pref_city or not selected_category:
        return go.Figure()
    
    filtered_df = persona[(persona['pref_city'] == selected_pref_city) & (persona["category"].isin(selected_category))]
    filtered_df = filtered_df[["category", "sub_category", "genre", "count", "num_uu_prefcity"]]

    grouped = filtered_df.groupby(["category", "sub_category", "genre"], as_index=False).agg({
        "count": "sum",
        'num_uu_prefcity': 'min'
    })

    grouped["subcate_genre"] = "[" + grouped["sub_category"] + "]" + grouped["genre"]
    grouped["score"] = grouped["count"] / grouped["num_uu_prefcity"]
    grouped.sort_values(by="score", ascending=False, inplace=True)

    traces = [go.Bar(x=group['subcate_genre'], y=group['score'], name=category) for category, group in grouped.groupby('category')]

    fig = go.Figure(data=traces)
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        coloraxis_showscale=False,
        xaxis_title="中分類",
        yaxis_title="スコア"
    )

    return fig
# --------------------------------------------------------------

@app.callback(
    Output('#3_dropdown', 'options'),
    [Input('#2_dropdown', 'value')]
)
def update_dropdown_3(selected_categories):
    if not selected_categories:
        return []
    
    # 選択されたカテゴリに基づいてサブカテゴリをフィルタリング
    filtered_subcategories = persona[persona['category'].isin(selected_categories)][['sub_category']].drop_duplicates().sort_values('sub_category')
    
    # サブカテゴリの選択肢を生成
    options_subcategory = [
        {'label': row['sub_category'], 'value': row['sub_category']}
        for index, row in filtered_subcategories.iterrows()
    ]
    
    return options_subcategory

@app.callback(
    Output('#4_dropdown', 'options'),
    Input('#3_dropdown', 'value')
)
def update_dropdown_4(selected_subcategory):
    if not selected_subcategory:
        return []
    
    # 選択されたサブカテゴリに基づいてジャンルをフィルタリング
    filtered_genres = persona[persona['sub_category']==selected_subcategory][['genre']].drop_duplicates().sort_values('genre')
    
    # ジャンルの選択肢を生成
    options_genre = [
        {'label': row['genre'], 'value': row['genre']}
        for index, row in filtered_genres.iterrows()
    ]
    
    return options_genre


# #1_table
# --------------------------------------------------------------
@app.callback(
    Output('#1_table', 'data'),
    Output('#1_table', 'columns'),
    [Input('#1_dropdown', 'value'), Input('#2_dropdown', 'value'), Input('#3_dropdown', 'value'), Input('#4_dropdown', 'value')]
)
def update_table_1(selected_pref_city, selected_category, selected_subcategory, selected_genre):
    if not selected_pref_city or not selected_category or not selected_subcategory or not selected_genre:
        return [], [{"name": i, "id": i} for i in ["category", "sub_category", "genre", "name", "score"]]
    
    if isinstance(selected_category, str):
        selected_category = [selected_category]
    if isinstance(selected_subcategory, str):
        selected_subcategory = [selected_subcategory]
    if isinstance(selected_genre, str):
        selected_genre = [selected_genre]
    
    filtered_df = persona[
        (persona['pref_city'] == selected_pref_city) & 
        (persona["category"].isin(selected_category)) &
        (persona["sub_category"].isin(selected_subcategory)) &
        (persona["genre"].isin(selected_genre))
    ]
    filtered_df = filtered_df[["category", "sub_category", "genre", "name", "count", "num_uu_prefcity"]]
    filtered_df["score"] = filtered_df["count"] / filtered_df["num_uu_prefcity"]

    data = filtered_df.to_dict('records')
    columns = [{"name": i, "id": i} for i in ["category", "sub_category", "genre", "name", "score"]]

    return data, columns
# --------------------------------------------------------------



# サーバー起動
# --------------------------------------------------------------
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8050))
    app.run_server(host='0.0.0.0', port=port,debug=True)
    # app.run_server(debug=True)
# --------------------------------------------------------------