"""
RSS источники для различных категорий новостей
Включает как русскоязычные, так и международные источники
"""

RSS_FEEDS = {
    "Искусственный интеллект": [
        "https://feeds.feedburner.com/oreilly/radar",
        "https://machinelearningmastery.com/feed/",
        "https://towardsdatascience.com/feed",
        "https://www.artificialintelligence-news.com/feed/",
        "https://venturebeat.com/ai/feed/",
        "https://www.technologyreview.com/feed/",
        "https://openai.com/blog/rss/",
        "https://deepmind.com/blog/feed/basic/",
        "https://ai.googleblog.com/feeds/posts/default",
        "https://blogs.nvidia.com/feed/",
        "https://habr.com/ru/rss/hub/artificial_intelligence/",
        "https://vc.ru/rss/ai",
        "https://www.cnews.ru/inc/rss/news.xml",
        "https://3dnews.ru/news/rss/",
        "https://www.computerra.ru/feed/"
    ],
    
    "Технологии": [
        "https://techcrunch.com/feed/",
        "https://www.theverge.com/rss/index.xml",
        "https://arstechnica.com/feed/",
        "https://www.wired.com/feed/",
        "https://www.engadget.com/rss.xml",
        "https://www.zdnet.com/news/rss.xml",
        "https://www.cnet.com/rss/news/",
        "https://gizmodo.com/rss",
        "https://www.techmeme.com/feed.xml",
        "https://rss.cnn.com/rss/edition_technology.rss",
        "https://habr.com/ru/rss/hub/it/",
        "https://vc.ru/rss/tech",
        "https://www.cnews.ru/inc/rss/news_it.xml",
        "https://3dnews.ru/news/rss/",
        "https://www.ixbt.com/export/news.rss"
    ],
    
    "Игры": [
        "https://www.gamespot.com/feeds/news/",
        "https://www.ign.com/articles?format=rss",
        "https://kotaku.com/rss",
        "https://www.polygon.com/rss/index.xml",
        "https://www.pcgamer.com/rss/",
        "https://www.eurogamer.net/?format=rss",
        "https://www.destructoid.com/rss.phtml",
        "https://www.gamasutra.com/rss/news.xml",
        "https://www.rockpapershotgun.com/feed",
        "https://www.gamesindustry.biz/feed",
        "https://dtf.ru/rss/all",
        "https://stopgame.ru/rss/news.xml",
        "https://www.playground.ru/rss/news",
        "https://4pda.ru/feed/",
        "https://habr.com/ru/rss/hub/gamedev/"
    ],
    
    "Крипта": [
        "https://cointelegraph.com/rss",
        "https://coindesk.com/arc/outboundfeeds/rss/",
        "https://decrypt.co/feed",
        "https://www.coinbase.com/blog/rss.xml",
        "https://blog.binance.com/en/rss.xml",
        "https://bitcoinmagazine.com/.rss/full/",
        "https://www.theblockcrypto.com/rss.xml",
        "https://cryptonews.com/news/feed/",
        "https://u.today/rss",
        "https://ambcrypto.com/feed/",
        "https://forklog.com/feed/",
        "https://bits.media/feed/",
        "https://coinspot.io/feed/",
        "https://incrypted.com/feed/",
        "https://mining-cryptocurrency.ru/feed/"
    ],
    
    "Наука": [
        "https://www.nature.com/nature.rss",
        "https://www.sciencemag.org/rss/news_current.xml",
        "https://www.newscientist.com/feed/home/",
        "https://www.scientificamerican.com/rss/news/",
        "https://phys.org/rss-feed/",
        "https://www.livescience.com/feeds/all",
        "https://www.space.com/feeds/all",
        "https://www.sciencedaily.com/rss/all.xml",
        "https://www.popsci.com/rss.xml",
        "https://www.nationalgeographic.com/news/rss/",
        "https://nplus1.ru/rss",
        "https://naked-science.ru/feed",
        "https://www.popmech.ru/feed/",
        "https://scientificrussia.ru/rss",
        "https://indicator.ru/rss.xml"
    ],
    
    "Политика": [
        "https://rss.cnn.com/rss/edition_politics.rss",
        "https://www.politico.com/rss/politics08.xml",
        "https://www.reuters.com/rssFeed/politicsNews",
        "https://www.bbc.com/news/politics/rss.xml",
        "https://www.theguardian.com/politics/rss",
        "https://www.washingtonpost.com/politics/?outputType=rss",
        "https://www.nytimes.com/section/politics/rss.xml",
        "https://www.foxnews.com/politics.rss",
        "https://abcnews.go.com/Politics/rss",
        "https://www.nbcnews.com/politics/feed",
        "https://lenta.ru/rss/news/politics",
        "https://ria.ru/export/rss2/archive/index.xml",
        "https://tass.ru/rss/v2.xml",
        "https://www.interfax.ru/rss.asp",
        "https://www.kommersant.ru/RSS/news.xml"
    ],
    
    "Экономика": [
        "https://feeds.bloomberg.com/markets/news.rss",
        "https://www.reuters.com/rssFeed/businessNews",
        "https://rss.cnn.com/rss/money_latest.rss",
        "https://www.wsj.com/xml/rss/3_7085.xml",
        "https://www.ft.com/rss/home/us",
        "https://www.economist.com/finance-and-economics/rss.xml",
        "https://www.cnbc.com/id/100003114/device/rss/rss.html",
        "https://www.marketwatch.com/rss/topstories",
        "https://finance.yahoo.com/news/rss",
        "https://seekingalpha.com/feed.xml",
        "https://www.rbc.ru/rss/economics",
        "https://www.vedomosti.ru/rss/news",
        "https://www.kommersant.ru/RSS/section-economics.xml",
        "https://quote.rbc.ru/news/rss",
        "https://www.banki.ru/xml/news.rss"
    ],
    
    "Культура": [
        "https://www.artforum.com/rss.xml",
        "https://www.theartnewspaper.com/rss",
        "https://hyperallergic.com/feed/",
        "https://www.timeout.com/rss.xml",
        "https://www.vulture.com/rss/index.xml",
        "https://www.rollingstone.com/music/rss/",
        "https://pitchfork.com/rss/news/",
        "https://www.billboard.com/feed/",
        "https://variety.com/feed/",
        "https://www.hollywoodreporter.com/feed/",
        "https://www.culture.ru/rss",
        "https://www.afisha.ru/rss/news/",
        "https://daily.afisha.ru/rss/",
        "https://www.colta.ru/rss/all/",
        "https://knife.media/feed/"
    ],
    
    "Мир": [
        "https://rss.cnn.com/rss/edition_world.rss",
        "https://www.bbc.com/news/world/rss.xml",
        "https://www.reuters.com/rssFeed/worldNews",
        "https://www.theguardian.com/world/rss",
        "https://www.aljazeera.com/xml/rss/all.xml",
        "https://www.dw.com/en/rss/rss-en-world/rss.xml",
        "https://www.france24.com/en/rss",
        "https://www.euronews.com/rss",
        "https://abcnews.go.com/International/rss",
        "https://www.npr.org/rss/rss.php?id=1004",
        "https://lenta.ru/rss/news/world",
        "https://ria.ru/export/rss2/world/index.xml",
        "https://tass.ru/rss/v2.xml",
        "https://www.interfax.ru/rss.asp?id=world",
        "https://www.rt.com/rss/"
    ],
    
    "Кино": [
        "https://variety.com/c/film/rss/",
        "https://www.hollywoodreporter.com/c/movies/feed/",
        "https://deadline.com/category/film/feed/",
        "https://www.indiewire.com/c/film/feed/",
        "https://www.slashfilm.com/feed/",
        "https://www.empireonline.com/movies/rss/",
        "https://www.cinemablend.com/rss_all.php",
        "https://collider.com/rss/",
        "https://www.joblo.com/rss.php",
        "https://www.comingsoon.net/feed",
        "https://www.kinopoisk.ru/rss/news.xml",
        "https://www.film.ru/rss/news",
        "https://www.kino-teatr.ru/rss/news.xml",
        "https://www.cinematograph.ru/rss.xml",
        "https://www.filmpro.ru/rss/news/"
    ],
    
    "Медицина": [
        "https://www.nejm.org/action/showFeed?type=etoc&feed=rss",
        "https://www.thelancet.com/rssfeed/lancet_current.xml",
        "https://jamanetwork.com/rss/site_508/509.xml",
        "https://www.bmj.com/rss/research.xml",
        "https://www.nature.com/nm.rss",
        "https://www.sciencemag.org/rss/news_current.xml",
        "https://www.medscape.com/rss/news",
        "https://www.webmd.com/rss/rss.aspx?RSSSource=RSS_PUBLIC",
        "https://www.healthline.com/rss/health-news",
        "https://www.medicalnewstoday.com/rss",
        "https://medvestnik.ru/rss/news.xml",
        "https://www.remedium.ru/rss/news/",
        "https://www.vademecum.ru/rss/news/",
        "https://www.pharmvestnik.ru/rss/news.xml",
        "https://medportal.ru/rss/news/"
    ]
}

def get_feeds_for_category(category: str) -> list:
    """Получает RSS ленты для указанной категории"""
    return RSS_FEEDS.get(category, [])

def get_all_categories() -> list:
    """Возвращает список всех доступных категорий"""
    return list(RSS_FEEDS.keys())

def get_total_feeds_count() -> int:
    """Возвращает общее количество RSS лент"""
    return sum(len(feeds) for feeds in RSS_FEEDS.values())
