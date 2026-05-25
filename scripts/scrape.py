"""
抓取国内最新财经新闻
来源: 东方财富网 财经要闻
输出: data/china-finance-news.json
"""

import json
import os
import re
import requests
from datetime import datetime

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "china-finance-news.json")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Referer": "https://finance.eastmoney.com/",
}


def fetch_eastmoney_news(max_items: int = 30) -> list[dict]:
    """从东方财富网获取财经新闻列表"""
    # 东方财富财经要闻API
    url = (
        "https://push2ex.eastmoney.com/getArticleList"
        "?cid=1001&pz=30&pn=1&type=0"
        "&callback=jQuery"
    )
    
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        
        text = resp.text
        # 提取 JSON 数据 (JSONP 格式)
        match = re.search(r'jQuery\((.*)\)', text)
        if not match:
            # 尝试其他格式
            match = re.search(r'\[.*\]', text)
        if not match:
            print("无法解析东方财富 API 返回数据")
            return []
        
        data = json.loads(match.group(1))
        articles = data.get("data", data.get("list", []))
        
        news_list = []
        for item in articles[:max_items]:
            art_code = item.get("art_code", "")
            date_str = item.get("date", "")
            
            news_list.append({
                "id": art_code,
                "title": item.get("title", ""),
                "url": f"https://finance.eastmoney.com/a/{art_code}.html" if art_code else "",
                "summary": item.get("short_abstract", "") or item.get("abstract", "") or "",
                "source": item.get("source", "东方财富网"),
                "date": date_str,
                "date_display": item.get("date_display", ""),
                "category": item.get("category_name", "财经"),
            })
        
        return news_list
    
    except Exception as e:
        print(f"东方财富 API 请求失败: {e}")
        return []


def fetch_163_finance(max_items: int = 15) -> list[dict]:
    """备选: 网易财经新闻"""
    try:
        resp = requests.get(
            "https://money.163.com/special/00251G50/ttkb.html",
            headers=HEADERS, timeout=10
        )
        resp.raise_for_status()
        
        # 尝试提取新闻列表
        pattern = r'<a\s+href="(https?://money\.163\.com/\d+/\d+/\d+/[^"]+)"[^>]*>([^<]+)</a>'
        matches = re.findall(pattern, resp.text)
        
        news_list = []
        seen = set()
        for href, title in matches:
            if title.strip() and title.strip() not in seen:
                seen.add(title.strip())
                news_list.append({
                    "id": "",
                    "title": title.strip(),
                    "url": href,
                    "summary": "",
                    "source": "网易财经",
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "date_display": "",
                    "category": "财经",
                })
                if len(news_list) >= max_items:
                    break
        
        return news_list
    
    except Exception as e:
        print(f"网易财经请求失败: {e}")
        return []


def main():
    news = []
    
    print("正在抓取国内财经新闻...")
    
    # 主方案: 东方财富
    news = fetch_eastmoney_news(max_items=30)
    
    # 如果东方财富失败，备选网易财经
    if len(news) < 5:
        print(f"东方财富仅获取到 {len(news)} 条，使用网易财经补充...")
        backup = fetch_163_finance(max_items=20)
        existing_titles = {n["title"] for n in news}
        for n in backup:
            if n["title"] not in existing_titles:
                news.append(n)
                if len(news) >= 30:
                    break
    
    print(f"获取完成，共 {len(news)} 条新闻")
    
    output = {
        "source": "东方财富网/网易财经",
        "description": "国内最新财经新闻",
        "language": "zh-CN",
        "scraped_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "total_count": len(news),
        "data": news,
    }
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"数据已保存到 {OUTPUT_FILE}")
    print(f"\n最新新闻:")
    for n in news[:10]:
        print(f"  {n['title'][:50]}")


if __name__ == "__main__":
    main()
