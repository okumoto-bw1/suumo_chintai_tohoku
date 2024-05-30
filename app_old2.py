import dash
from dash import html, dcc, Input, Output
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
import os
import json
from shapely.geometry import shape, MultiPolygon

# データの前処理(引越し元)
# --------------------------------------------------------------
persona = pd.read_csv("事業所名で集計.csv",dtype="str")
persona["count"]=persona["count"].astype(int)
persona["num_uu_prefcity"]=persona["num_uu_prefcity"].astype(int)
persona['pref_city'] = persona['pref'] + persona['city']
# --------------------------------------------------------------

# GeoJSONデータの読み込み
# --------------------------------------------------------------
with open('N03-21_210101.json', 'r', encoding='utf-8') as f:
    geojson = json.load(f)
# GeoJSONデータの各フィーチャーに新しいプロパティを追加
for feature in geojson['features']:
    props = feature['properties']
    # None 値を空文字列で置き換える
    n03_001 = props['N03_001'] if props['N03_001'] is not None else ''
    n03_003 = props['N03_003'] if props['N03_003'] is not None else ''
    n03_004 = props['N03_004'] if props['N03_004'] is not None else ''
    combined_key = n03_001 + n03_003 + n03_004
    props['combined_key'] = combined_key
# --------------------------------------------------------------

# ドロップダウン(personaのpref_city)
# --------------------------------------------------------------
# 重複を排除し、昇順にソート
unique_pref_city_1 = persona[['pref_city']].drop_duplicates().sort_values('pref_city')

# 都道府県と市区郡の組み合わせの選択肢を昇順で生成
options_pref_city_1 = [
    {'label': row['pref_city'], 'value': row['pref_city']}
    for index, row in unique_pref_city_1.iterrows()
]
# --------------------------------------------------------------

# ドロップダウン(personaのcategory)
# --------------------------------------------------------------
# 重複を排除し、昇順にソート
unique_category = persona[['category']].drop_duplicates().sort_values('category')

# 都道府県と市区郡の組み合わせの選択肢を昇順で生成
options_category = [
    {'label': row['category'], 'value': row['category']}
    for index, row in unique_category.iterrows()
]
# --------------------------------------------------------------

# ドロップダウン(personaのsub_category)
# --------------------------------------------------------------
# 重複を排除し、昇順にソート
unique_subcategory = persona[['sub_category']].drop_duplicates().sort_values('sub_category')

# 都道府県と市区郡の組み合わせの選択肢を昇順で生成
options_subcategory = [
    {'label': row['sub_category'], 'value': row['sub_category']}
    for index, row in unique_subcategory.iterrows()
]
# --------------------------------------------------------------

# ドロップダウン(personaのgenre)
# --------------------------------------------------------------
# 重複を排除し、昇順にソート
unique_genre = persona[['genre']].drop_duplicates().sort_values('genre')

# 都道府県と市区郡の組み合わせの選択肢を昇順で生成
options_genre = [
    {'label': row['genre'], 'value': row['genre']}
    for index, row in unique_genre.iterrows()
]
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
                html.P("居住地", style={'margin': '0 10px 0 0', 'color': '#4A90E2','display': 'flex', 'alignItems': 'center','fontFamily': 'Arial, sans-serif'}),  # 要素間のマージンを設定
                dcc.Dropdown(
                    id='#1_dropdown',
                    options=options_pref_city_1,
                    value="宮城県仙台市青葉区",
                    # multi=True,  # 複数選択を可能にする
                    style={"flex": "1"},
                ),
            ], style={"display": "flex", "alignItems": "center","width":"25%", "margin": '0 10px 0 10px'}),
            html.Div([
                html.P("事業所の大分類", style={'margin': '0 10px 0 0', 'color': '#4A90E2','display': 'flex', 'alignItems': 'center','fontFamily': 'Arial, sans-serif'}),  # 要素間のマージンを設定
                dcc.Dropdown(
                    id='#2_dropdown',
                    options=options_category,
                    value=[option['value'] for option in options_category],
                    multi=True,  # 複数選択を可能にする
                    style={"flex": "1"},
                ),
            ], style={"display": "flex", "alignItems": "center","width":"75%", "margin": '0 10px 0 10px'}),
        ], style={"display": "flex", "justifyContent": "space-around", 'height': '300px'}),
        
        html.Div([
            dcc.Graph(id='#1_graph', style={'display': 'inline-block', 'width': '98%','height': '95%'}),
        ], style={"display": "flex","justifyContent": "space-around", 'height': '700px'}),

        html.Div([
                html.P("事業所の中分類", style={'margin': '0 10px 0 0', 'color': '#4A90E2','display': 'flex', 'alignItems': 'center','fontFamily': 'Arial, sans-serif'}),  # 要素間のマージンを設定
                dcc.Dropdown(
                    id='#3_dropdown',
                    options=[],
                    value=None,
                    style={"flex": "1"},
                ),
            ], style={"display": "flex", "alignItems": "center","width":"100%", "margin": '0 10px 0 10px'},
        ),

        html.Div([
            dcc.Graph(id='#2_graph', style={'display': 'inline-block', 'width': '98%','height': '95%'}),
        ], style={"display": "flex","justifyContent": "space-around", 'height': '700px'}),
    ],
    style={"backgroundColor": "#F0F4F8",'height': '2000px'},
    ),
])

# #1_graph
# --------------------------------------------------------------
@app.callback(
    Output('#1_graph', 'figure'),
    [Input('#1_dropdown', 'value'),Input('#2_dropdown', 'value')]
)
def update_graph_1(selected_pref_city,selected_category):
    if not selected_pref_city or not selected_category:
        return go.Figure()
    
    # データフレームをフィルタリング/グループ化
    filtered_df = persona[(persona['pref_city'] == selected_pref_city) & (persona["category"].isin(selected_category))].copy()
    filtered_df = filtered_df[["category","sub_category","genre","name","count","num_uu_prefcity"]]

    grouped = filtered_df[["category","sub_category","genre","count","num_uu_prefcity"]].groupby(["category","sub_category","genre"],as_index=False).agg({
        "count":"sum",
        'num_uu_prefcity': 'min'
    })

    grouped["subcate_genre"] = "["+grouped["sub_category"]+"]"+grouped["genre"]
    grouped["score"] = grouped["count"] / grouped["num_uu_prefcity"]

    # ratioが多い順にソート
    grouped.sort_values(by="score", ascending=False,inplace=True)

    # categoryごとにデータをグループ化
    grouped2 = grouped.groupby('category')

    # 棒グラフのトレースを作成
    traces = []
    for category, group in grouped2:
        traces.append(go.Bar(
            x=group['subcate_genre'],
            y=group['score'],
            name=category,
        ))

    # フィギュアを作成
    fig = go.Figure(data=traces)
    
    # レイアウトの設定
    fig.update_layout(
        # barmode='stack',
        paper_bgcolor='rgba(0,0,0,0)',
        coloraxis_showscale=False,
        xaxis_title="中分類",
        yaxis_title="スコア"
    )

    return fig
# --------------------------------------------------------------


# #3_dropdown
# --------------------------------------------------------------
@app.callback(
    Output('#3_dropdown', 'options'),
    [Input('#2_dropdown', 'value')]
)
def update_dropdown_3(selected_categories):
    if not selected_categories:
        return []
    
    # 選択されたカテゴリに基づいてサブカテゴリをフィルタリング
    filtered_categories = persona[persona['category'].isin(selected_categories)][['category']].drop_duplicates().sort_values('category')
    
    # サブカテゴリの選択肢を生成
    options_category = [
        {'label': row['category'], 'value': row['category']}
        for index, row in filtered_categories.iterrows()
    ]
    
    return options_category
# --------------------------------------------------------------

# #2_graph
# --------------------------------------------------------------
@app.callback(
    Output('#2_graph', 'figure'),
    [Input('#1_dropdown', 'value'),Input('#3_dropdown', 'value')]
)
def update_graph_2(selected_pref_city, selected_category):
    if not selected_pref_city or not selected_category:
        return go.Figure()
    
    # データフレームをフィルタリング/グループ化
    filtered_df = persona[(persona['pref_city'] == selected_pref_city) & (persona["category"]==selected_category)].copy()
    filtered_df = filtered_df[["category", "sub_category", "genre", "name", "count", "num_uu_prefcity"]]

    # categoryごとにデータをグループ化し、nameの数が多い順にソート
    grouped = filtered_df.groupby(["category", "name"], as_index=False).agg({
        "count": "sum"
    }).sort_values(by="count", ascending=False)

    # categoryごとにデータをグループ化
    grouped2 = grouped.groupby('category')

    # 棒グラフのトレースを作成
    traces = []
    for category, group in grouped2:
        traces.append(go.Bar(
            x=group['name'],
            y=group['count'],
            name=category,
        ))

    # フィギュアを作成
    fig = go.Figure(data=traces)
    
    # レイアウトの設定
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        coloraxis_showscale=False,
        xaxis_title="事業所名",
        yaxis_title="カウント"
    )

    return fig
# --------------------------------------------------------------



# サーバー起動
# --------------------------------------------------------------
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8050))
    app.run_server(host='0.0.0.0', port=port,debug=True)
    # app.run_server(debug=True)
# --------------------------------------------------------------