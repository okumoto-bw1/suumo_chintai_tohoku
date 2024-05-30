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
persona = pd.read_csv("事業所サブカテで集計.csv",dtype="str")
persona["count"]=persona["count"].astype(int)
persona["ratio"]=persona["ratio"].astype(float)
persona["user_num"]=persona["user_num"].astype(int)
persona['pref_city'] = persona['pref'] + persona['city']

# ratioをスケーリングして最大値を100にする
max_ratio = persona["ratio"].max()
persona["ratio"] = (persona["ratio"] / max_ratio) * 100
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
    ],
    style={"backgroundColor": "#F0F4F8",'height': '1100px'},
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
    
    # ratioが多い順にソート
    filtered_df = filtered_df.sort_values(by="ratio", ascending=False)

    # categoryごとにデータをグループ化
    grouped = filtered_df.groupby('category')

    # 棒グラフのトレースを作成
    traces = []
    for category, group in grouped:
        traces.append(go.Bar(
            x=group['sub_category'],
            y=group['ratio'],
            name=category,
        ))

    # フィギュアを作成
    fig = go.Figure(data=traces)
    
    # レイアウトの設定
    fig.update_layout(
        barmode='stack',
        paper_bgcolor='rgba(0,0,0,0)',
        coloraxis_showscale=False,
        xaxis_title="中分類",
        yaxis_title="スコア"
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