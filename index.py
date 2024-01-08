from flask import Flask, request, jsonify, abort
from requests_html import HTMLSession, HTML
from fake_useragent import UserAgent
from flask_caching import Cache
import json

app = Flask(__name__)

# 配置缓存
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.route('/api')
@cache.cached(timeout=300)
def scrape_videos():
    page_number = request.args.get('num', default=1, type=int)

    if page_number < 1 or page_number > 5000:  # 假设有效页码范围是 1 到 10
        abort(400, "Invalid page number")

    url = f'https://www.youporn.com/?page={page_number}'

    session = HTMLSession()
    ua = UserAgent()
    headers = {
        'User-Agent': ua.random
    }
    response = session.get(url, headers=headers).text

    html = HTML(html=response)

    video_blocks = html.find('.video-box')
    videos = []
    for video_block in video_blocks:
        video_id = video_block.find('.video-box-image', first=True).attrs['href']
        image_src = video_block.find('.thumb-image', first=True).attrs['data-poster']
        resolution = video_block.find('.video-best-resolution', first=True).text
        title = video_block.find('.video-title', first=True).text

        video = {
            'id': video_id,
            'image': image_src,
            'res': resolution,
            'title': title
        }
        videos.append(video)

    json_data = json.dumps(videos)  # 将列表转换为 JSON 字符串

    return json_data, 200, {'Content-Type': 'application/json'}

if __name__ == "__main__":
    app.run(debug=False)
