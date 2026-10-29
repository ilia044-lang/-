"""Timestamped price/news briefing. Never represents headlines as a call transcript."""
import argparse, datetime as dt, html, json, math
from pathlib import Path
from zoneinfo import ZoneInfo
import pandas as pd
import yfinance as yf
from curl_cffi import requests

ISRAEL=ZoneInfo('Asia/Jerusalem'); NY=ZoneInfo('America/New_York')
EVENT=dt.datetime(2026,10,29,16,tzinfo=NY)

def stamp(epoch):
    return dt.datetime.fromtimestamp(epoch,ISRAEL).strftime('%d.%m %H:%M:%S') if epoch else 'לא זמין'
def pct(a,b): return 100*(a/b-1)
def number(n): return f'{n:,.2f}' if n is not None and math.isfinite(n) else 'לא זמין'
def collect(symbol):
    t=yf.Ticker(symbol); info=t.info
    fields=['regularMarketPrice','regularMarketTime','regularMarketPreviousClose','postMarketPrice','postMarketTime','preMarketPrice','preMarketTime']
    quote={k:info.get(k) for k in fields}
    bars=t.history(period='2y',auto_adjust=False)
    bars=bars[bars.index.strftime('%Y-%m-%d')<='2026-10-29']
    assert len(bars)>200 and str(bars.index[-1].date())=='2026-10-29', f'{symbol}: stale daily data'
    assert ((bars.High>=bars[['Open','Close','Low']].max(axis=1)) & (bars.Low<=bars[['Open','Close','High']].min(axis=1))).all()
    close=float(bars.Close.iloc[-1]);previous=float(bars.Close.iloc[-2])
    candidates=[(quote.get(k),quote.get(tm),label) for k,tm,label in [('postMarketPrice','postMarketTime','מסחר מאוחר'),('preMarketPrice','preMarketTime','טרום מסחר')]]
    candidates=[v for v in candidates if v[0] and v[1] and v[1]>EVENT.timestamp()]
    ext=max(candidates,key=lambda v:v[1]) if candidates else None
    metrics={'close':close,'previous_close':previous,'regular_change_pct':pct(close,previous),'sma':{str(n):float(bars.Close.tail(n).mean()) for n in [20,50,200]},'low20':float(bars.Low.tail(20).min()),'high20':float(bars.High.tail(20).max()),'volume_ratio':float(bars.Volume.iloc[-1]/bars.Volume.iloc[-21:-1].mean())}
    news={}; errors=[]
    for query in [symbol, 'Intel' if symbol=='INTC' else 'Amazon']:
        try:
            r=requests.get('https://query1.finance.yahoo.com/v1/finance/search',params={'q':query,'newsCount':100},impersonate='chrome',timeout=30);r.raise_for_status()
            for n in r.json().get('news',[]):
                if n.get('providerPublishTime',0)>=EVENT.timestamp() and any(k in n.get('title','').lower() for k in ([symbol.lower(),'intel'] if symbol=='INTC' else ['amzn','amazon','aws'])):
                    news[n['link']]=n
        except Exception as e: errors.append(type(e).__name__)
    return {'symbol':symbol,'quote':quote,'extended':ext,'metrics':metrics,'news':sorted(news.values(),key=lambda n:n.get('providerPublishTime',0),reverse=True)[:18],'news_errors':errors},bars

def build(out):
    out.mkdir(parents=True,exist_ok=True); now=dt.datetime.now(ISRAEL)
    data={'retrieved_at':now.isoformat(),'daily_data_date':'2026-10-29','full_reports_reviewed':False,'calls_reviewed':False,'companies':{}}
    lines=['# Amazon ו־Intel — עדכון בעקבות הדוחות',f'עודכן: **{now:%d.%m.%Y %H:%M} שעון ישראל**.',
    '**סטטוס: עדכון מחירים וכותרות בלבד; ניתוח הדוחות ושיחות המשקיעים עדיין חסר.**',
    'נתוני המסחר הרגיל הם מסגירת 29.10. מחיר מאוחר/מוקדם מוצג בנפרד עם שעתו. בשעה 08:00 בישראל טרום המסחר בארה״ב עדיין לא נפתח; אין כאן תגובה מהמסחר הרגיל של יום שישי.',
    '## המסקנה המעשית',
    'אפשר להכניס לרשימת מעקב, אך ירידה חדה לבדה אינה הוכחה למחיר אטרקטיבי. ללא בדיקת התחזית והתזרים וללא התייצבות במסחר הרגיל, אין בסיס בדוח זה לקבוע שמדובר בדיפ מוצלח. רמות מלפני הדוח עלולות להפוך להתנגדות לאחר פער ירידה.',
    'למסחר קצר: עקוב אחר הפסקת יצירת שפלים, חזרה מעל רמה שנשברה, בדיקה חוזרת שמחזיקה ונפח מסחר. אלה תנאים למעקב, לא אישור אוטומטי לעסקה. להשקעה ארוכה: דרושה בחינת שווי מול רווחים ותזרים עתידיים לאחר עדכון התחזיות.']
    for symbol in ['AMZN','INTC']:
        d,bars=collect(symbol);data['companies'][symbol]=d;bars.to_csv(out/f'{symbol}_daily.csv');m=d['metrics'];e=d['extended']
        lines += [f'## {symbol}',f"סגירת 29.10: **${m['close']:.2f}**, שינוי יומי **{m['regular_change_pct']:+.2f}%**."]
        if e:
            p,ts,label=e
            lines += [f"{label}: **${p:.2f}**, **{pct(p,m['close']):+.2f}%** מול הסגירה; חותמת מחיר **{stamp(ts)} בישראל**.",f"שינוי כולל מול סגירת 28.10: **{pct(p,m['previous_close']):+.2f}%**. זהו בסיס השוואה אחר מהשינוי במסחר המאוחר."]
        else: lines += ['אין מחיר מסחר מאוחר/מוקדם תקף לאחר הדוח; אין להסיק שינוי מהציטוט הרגיל בלבד.']
        lines += ['| מדד יומי עד 29.10 | ערך |','|---|---:|']
        for n,v in m['sma'].items(): lines.append(f'| SMA{n} | ${v:.2f} |')
        lines += [f"| שפל 20 ימי מסחר | ${m['low20']:.2f} |", f"| מחזור יום הדוח / ממוצע 20 הימים הקודמים | {m['volume_ratio']:.2f}x |",'ממוצעים אלה מבוססים על סגירות רגילות ואינם כוללים את פער המחיר אחרי הדוח. שפל תקופתי אינו תמיכה מובטחת.']
        if e:
            broken=[f'SMA{n} (${v:.2f})' for n,v in m['sma'].items() if e[0]<v]
            lines.append('המחיר המאוחר נמצא מתחת ל־'+', '.join(broken)+'.' if broken else 'המחיר המאוחר נמצא מעל הממוצעים שנמדדו; אין בכך לבדו אישור להתאוששות.')
            if e[0]<m['low20']:lines.append(f"המחיר המאוחר גם מתחת לשפל 20 הימים (${m['low20']:.2f}); זו אינדיקציה לפגיעה במבנה המחיר, שצריך לאמת במסחר הרגיל הבא.")
        lines += ['### כותרות מאז פרסום הדוח', 'הפריטים הבאים הם כותרות מקור, ללא אימות גוף הכתבה או שיוך סיבתי ודאי לירידה.']
        for n in d['news']:lines.append(f"- [{n['title']}]({n['link']}) — {n.get('publisher','')}, {stamp(n.get('providerPublishTime'))}.")
        if not d['news']:lines.append('לא התקבלו כותרות מתאימות במקור הזמין. אין להסיק מכך שלא פורסמו תוצאות.')
        lines += ['### מה חייבים לבדוק בדוח ובשיחה']
        if symbol=='AMZN':lines += ['- הכנסות ורווח לעומת הקונצנזוס, תחזית Q4 והכנסה תפעולית.', '- צמיחת AWS, רווחיות הענן, השקעות הון ותזרים חופשי לאחר השקעות.', '- תשובות ההנהלה על ביקוש AI, מגבלות קיבולת והחזר ההשקעה. הפרדה בין הוצאות זמניות לבין פגיעה מתמשכת.','מקור ראשוני לבדיקה: https://ir.aboutamazon.com/quarterly-results/default.aspx']
        else:lines += ['- הכנסות, EPS מתואם ורווח גולמי לעומת התחזית; הנחיות לרבעון הבא.', '- התקדמות 18A, לקוחות חיצוניים לפאונדרי והפסדי פעילות הייצור.', '- תזרים, השקעות, מזומן ומימון; מה אמרה ההנהלה על מועדי אספקה וביקוש.','מקור ראשוני לבדיקה: https://www.intc.com/financial-info/financial-results']
        lines += ['**אין כאן עדיין ציטוטים או מסקנות משיחת המשקיעים.**']
    lines += ['## מקורות ושיטה','מחירים והיסטוריה: Yahoo Finance דרך yfinance. כותרות: Yahoo Finance Search API; קישורים למקורות מופיעים למעלה. הממוצעים חושבו מסגירות לא מתואמות, ולכן יש לבדוק אירועי פיצול לפני שימוש ברמות.','זהו עדכון אוטומטי על פי כללים מוגדרים, לא סקירה אנושית חדשה של שיחת משקיעים. חוסרים אינם מוחלפים בהשערות.','לימוד בלבד, לא ייעוץ השקעות ולא המלצה לקנייה או מכירה.']
    text=('\n\n'.join(lines)+'\n').replace('|\n\n|','|\n|');(out/'Summary_HE.md').write_text(text);(out/'evidence.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
    import markdown
    body=markdown.markdown(text,extensions=['tables'])
    (out/'Summary_HE.html').write_text('<!doctype html><html lang="he" dir="rtl"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>AMZN + INTC</title><style>body{font:18px/1.7 Arial,sans-serif;max-width:900px;margin:35px auto;padding:20px;background:#f5f7fa;color:#172332}h1,h2{color:#175eaa}a{overflow-wrap:anywhere}table{border-collapse:collapse;width:100%;background:white}td,th{padding:10px;border-bottom:1px solid #ddd}li{margin:8px 0}</style>'+body+'</html>')
    print(json.dumps({'updated':now.isoformat(),'files':len(list(out.iterdir())),'calls_reviewed':False}))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();build(a.output)
