"""Ground narration in computed inputs; never invent news or future dates."""
import re

def price(x):return f'{x:,.2f}'
def direction(x):return f'{abs(x):.2f} percent '+('higher' if x>=0 else 'lower')

def build(a):
    m=a['markets'];spy=m['SPY'];qqq=m['QQQ'];rows=[]
    def add(kind,title,kicker,voice,**kw):rows.append(dict(kind=kind,title=title,kicker=kicker,voice=voice,**kw))
    label='PREVIEW — THROUGH OCT 8' if a['preview'] else 'WEEK OF OCT 5–9, 2026'
    add('hero','THE WEEK.\nTHE NEXT MOVE.',label,
        'Welcome to Market Mind. This is your weekly market briefing for October fifth through ninth, with the road map for October twelfth through sixteenth. We will connect stocks, bonds, oil, the dollar and Bitcoin, examine fifteen Octobers, and put four stocks on a technical watchlist. The goal is context, not a prediction.')
    if a['preview']:rows[-1]['voice']='This is an automation preview using completed data through October eighth. The final edition will require October ninth data after the close. '+rows[-1]['voice']
    add('scoreboard','WHAT CHANGED THIS WEEK','PERFORMANCE • PREVIOUS FRIDAY TO REVIEW DATE',
        f'The S and P five hundred fund, S P Y, finished {direction(spy["weekly_pct"])}. Q Q Q was {direction(qqq["weekly_pct"])}, while the Dow Jones was {direction(m["^DJI"]["weekly_pct"])}. These returns compare the review close with the previous Friday, October second. Comparing all three helps distinguish technology leadership from participation across the wider market.',symbols=['SPY','QQQ','^DJI'])
    add('chart','SPY: THE MARKET REFERENCE','DAILY PRICE • OBSERVED LEVELS',
        f'S P Y closed at {price(spy["close"])}. The fifty day average is {price(spy["ma"]["50"])} and the two hundred day is {price(spy["ma"]["200"])}. An observed support reference is {price(spy["support"])}, with resistance near {price(spy["resistance"])}. A close above an average describes the trend; it does not guarantee that support will hold. Next week, the reaction at these levels matters more than the line itself.',symbol='SPY')
    add('chart','QQQ: CHECK THE LEADERSHIP','TECHNOLOGY • MOMENTUM • PARTICIPATION',
        f'Q Q Q closed at {price(qqq["close"])}. Its fourteen day R S I reads {qqq["rsi"]:.1f}. Support is referenced near {price(qqq["support"])}, and resistance near {price(qqq["resistance"])}. Compare its weekly change with the broad index before calling the move broad based. A strong technology index can coexist with weaker individual stocks. Momentum is evidence to weigh alongside price, volume and breadth.',symbol='QQQ')
    breadth=a['supplemental'].get('breadth');vix=m['^VIX']
    bv=f'The retrieved breadth snapshot is {breadth["value"]:.2f} percent. Its retrieval time is retained with the sources; it is not independently certified as an official daily close. ' if breadth else 'A verified final breadth reading was unavailable, so no percentage is invented. '
    add('breadth','HOW MANY STOCKS JOINED IN?','S5FI • S&P 500 MEMBERS ABOVE THEIR 50-DAY AVERAGE',
        bv+f'This measure asks how many index members are above their fifty day average. A rising index with improving participation is different from a rise carried by a few names. Meanwhile, VIX reads {vix["close"]:.2f}, {direction(vix["weekly_pct"])} over the review week. VIX measures implied volatility, not the direction of the next move.',symbol='^VIX')
    treasury=a['supplemental'].get('treasury');r=m['^TNX'];long=m['^TYX']
    rate_extra=f'The Treasury publishes the twenty year yield at {treasury["latest"]["20y"]:.2f} percent, dated {treasury["latest"]["date"]}. ' if treasury else 'The twenty year official observation could not be verified for this edition. '
    add('rates','THE PRICE OF MONEY','US TREASURY YIELDS • 10 / 20 / 30 YEARS',
        f'The ten year yield reads {r["close"]:.3f} percent and the thirty year {long["close"]:.3f} percent in the market feed. '+rate_extra+
        'Yield changes and bond price changes are different things: rising yields generally mean falling bond prices. Higher long term yields can pressure equity valuations and financing costs. For next week, watch the direction of yields alongside economic releases, rather than treating one number as a forecast.',symbols=['^TNX','^TYX'])
    oil=m['CL=F'];dollar=m['DX-Y.NYB'];btc=m['BTC-USD']
    add('crossasset','OIL. DOLLAR. BITCOIN.','THREE DIFFERENT TRANSMISSION CHANNELS',
        f'WTI futures read {price(oil["close"])} dollars per barrel. The dollar index is {dollar["close"]:.3f}. Bitcoin is around {price(btc["close"])} dollars at the captured snapshot. Bitcoin trades around the clock, so this is not an equity market closing print. Oil can affect inflation expectations, while the dollar influences global financial conditions. For Strategy and the digital infrastructure names, Bitcoin adds another source of volatility.',symbols=['CL=F','DX-Y.NYB','BTC-USD'])
    for s in a['seasonality']:
        add('season',f'{s["symbol"]}: 15 OCTOBERS','2011–2025 • ADJUSTED MONTH-END RETURNS',
            f'Now the October question. Over fifteen completed Octobers, from twenty eleven through twenty twenty five, {"S P Y" if s["symbol"]=="SPY" else "Q Q Q"} was positive in {s["positive"]} years and negative in {s["negative"]}. The average October return was {s["mean"]:.2f} percent; the median was {s["median"]:.2f}. The best was {s["best"]:.2f} percent, and the worst {s["worst"]:.2f}. These are adjusted monthly price returns, with dividends reflected by the data provider. October twenty twenty six is incomplete and excluded. A fifteen year sample describes history, not the odds of a guaranteed outcome.',symbol=s['symbol'])
    news=a['news'][:3]
    for i,n in enumerate(news):
        add('news',n['title'],n['publisher'].upper()+' • '+n['published'][:10],
            f'In the reported news, {n["publisher"]} published this headline: {n["title"]}. This is an attributed report, not proof that the headline caused the market move. For the coming week, separate the announcement from the subsequent evidence: company disclosures, reported results and the actual price response. Publication date and the source link accompany this edition.',news=n)
    if not news:add('news','NEWS VERIFICATION GAP','NO UNSOURCED HEADLINES', 'No eligible current headline could be verified in the connected feed. We will not fill that gap with invented news. The source notes disclose this limitation. Continue to check issuer announcements and authoritative reporting before treating a developing story as an established fact.')
    cal=a['calendar'];events=cal['macro'][:4];earnings=cal['earnings'][:6]
    macro=' '.join(f'On October {int(e["date"][-2:])}, the B L S calendar lists {e["event"]}.' for e in events)
    if not events:macro='A verified B L S release schedule could not be retrieved. Specific release dates are not asserted.'
    add('calendar','NEXT WEEK: OCTOBER 12–16','ECONOMIC RELEASES • EXPECTATIONS VS ACTUALS',macro+' The important distinction is the release versus the consensus expectation. The same headline number can have a different market impact depending on what was priced in. Watch the reaction in yields, the dollar and equity breadth together. Economic calendars can change; recheck the original source before the event.',events=events)
    ev=' '.join(f'{e["symbol"]}, October {int(e["date"][-2:])}.' for e in earnings)
    if not earnings:ev='The upcoming earnings calendar could not be independently retrieved, so no company reporting date is presented as confirmed.'
    add('calendar','EARNINGS ON THE RADAR','OCTOBER 12–16 • CALENDAR DATES ARE ESTIMATES',
        ev+' These dates are calendar estimates unless an issuer announcement confirms them. For earnings, listen beyond the headline profit number: revenue quality, margins, demand and forward guidance often shape the next conversation. An overnight earnings gap can jump across a chart level. That is why the event calendar belongs beside the technical analysis.',earnings=earnings)
    context={'MSTR':'Bitcoin sensitivity and the company capital structure can amplify moves.','IREN':'Watch operating execution and funding disclosures alongside the digital infrastructure theme.','AVGO':'Semiconductor demand and infrastructure spending are the business context; the chart alone cannot confirm either.','CIFR':'This is Cipher Digital, ticker C I F R. Infrastructure execution and financing remain relevant context.'}
    for sym in ['MSTR','IREN','AVGO','CIFR']:
        x=m[sym];vol=f'Volume was {x["relative_volume"]:.2f} times its twenty session average.' if x['relative_volume'] is not None else ''
        add('stock',f'{sym}: LEVELS, NOT PROMISES',x['name'].upper()+' • TECHNICAL WATCHLIST',
            f'{x["name"]} closed at {price(x["close"])} dollars, {direction(x["weekly_pct"])} for the review week. '+context[sym]+f' The observed support reference is {price(x["support"])}, with resistance near {price(x["resistance"])}. R S I is {x["rsi"]:.1f}. '+vol+' Above resistance, watch for a sustained hold and participation. Below support, reassess whether the structure is weakening. These are conditional scenarios, not recommendations.',symbol=sym)
    add('scenarios','TWO PATHS. ONE CHECKLIST.','SCENARIOS, NOT PREDICTIONS',
        'For the constructive scenario, look for the major indexes to hold their support references, breadth to improve, and volatility to remain contained. For the risk scenario, watch support breaks accompanied by weaker participation or rising yields and volatility. Surprise inflation, earnings guidance and geopolitical developments can change the picture quickly. None of these conditions guarantees a move. Let new evidence update the assessment.',symbols=['SPY','QQQ'])
    add('hero','READY FOR NEXT WEEK','MARKET MIND | TRADING BASICS',
        'That is the weekly map: price, participation, cross asset signals and the calendar. Follow Market Mind for clear chart education and the next weekly briefing. This program is education only, not financial advice. I am not a licensed advisor. Nothing here is a recommendation to buy or sell.')
    return rows

def short_scripts(a):
    s=a['seasonality'][0];m=a['markets'];x=m['SPY']
    return [
      {'kind':'season','symbol':'SPY','title':'IS OCTOBER REALLY PROFITABLE?','kicker':'15 YEARS OF DATA • 2011–2025','voice':f'Is October really profitable? In fifteen completed Octobers, S P Y was positive {s["positive"]} times and negative {s["negative"]}. Its average October return was {s["mean"]:.2f} percent, but the worst was {s["worst"]:.2f}. These are adjusted monthly returns from twenty eleven through twenty twenty five. This October is incomplete and excluded. History is context, not a guarantee. Watch the full Market Mind weekly review for the charts and next week calendar. Education only, not financial advice.'},
      {'kind':'scenarios','title':'NEXT WEEK: WATCH THESE SIGNALS','kicker':'OCTOBER 12–16 • MARKET MIND','symbols':['SPY','QQQ'],'voice':f'Before next week, connect three signals. First, S P Y support near {price(x["support"])} and resistance near {price(x["resistance"])}. Second, whether more stocks participate in the move. Third, the reaction in yields and volatility around economic releases and earnings. Our technical watchlist includes Strategy, IREN, Broadcom and Cipher Digital. A level is a reference, not a promise. Watch the full weekly review for context and both scenarios. Education only, not financial advice.'}
    ]

def caption_chunks(text):
    chunks=[]
    for sentence in re.split(r'(?<=[.!?])\s+(?=[A-Z])',text):
        words=sentence.split()
        while words:
            # Synthesize each visible caption independently: timings come from actual audio.
            take=min(14,len(words));chunks.append(' '.join(words[:take]));words=words[take:]
    return chunks
