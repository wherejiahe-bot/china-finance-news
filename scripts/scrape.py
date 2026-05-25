"""
抓取国内最新财经新闻
来源: 东方财富网 财经要闻
输出: data/china-finance-news.json
"""

import json
import os
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "china-finance-news.json")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Referer": "https://www.eastmoney.com/",
}


def fetch_eastmoney_news(max_items: int = 30) -> list[dict]:
    """从东方财富首页提取财经新闻"""
    news_list = []
    seen_urls = set()
    
    try:
        resp = requests.get("https://www.eastmoney.com/", headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")
        
            # 提取所有新闻链接
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            # 优先取标签内文本，其次取 title 属性
            title = a_tag.get_text(strip=True) or a_tag.get("title", "")
            
            # 只提取东方财富新闻链接
            if "//finance.eastmoney.com/a/" in href and title and len(title) > 5:
                full_url = href if href.startswith("http") else f"https:{href}"
                if full_url not in seen_urls:
                    seen_urls.add(full_url)
                    news_list.append({
                        "id": "",
                        "title": title.strip(),
                        "url": full_url,
                        "summary": "",
                        "source": "东方财富网",
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "category": "财经",
                    })
        
        # 按页面出现顺序保留前 max_items 条
        news_list = news_list[:max_items]
        
    except Exception as e:
        print(f"东方财富抓取失败: {e}")
    
    return news_list


def main():
    news = []
    
    print("正在抓取国内财经新闻...")
    
    # 主方案: 东方财富
    news = fetch_eastmoney_news(max_items=30)
    
    print(f"获取完成，共 {len(news)} 条新闻")
    
    output = {
        "source": "东方财富网",
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
