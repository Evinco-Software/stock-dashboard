import yfinance as yf
import json
from datetime import datetime
import time

def fetch_real_data():
    print("⏳ 正在啟動真實數據抓取引擎...")
    
    # 定義前端介面名稱對應到 Yahoo Finance 的實際代號 (Ticker)
    symbols_map = {
        'VTI': 'VTI',
        'MSFT': 'MSFT',
        'GOOG': 'GOOG',
        'NVDA': 'NVDA',
        'KO': 'KO',
        'S&P 500': '^GSPC',  
        'NASDAQ': '^IXIC',   
        'DJI': '^DJI',       
        'VIX': '^VIX'        
    }

    all_data = {}

    # 依序抓取每一檔標的資料
    for display_name, yf_ticker in symbols_map.items():
        print(f"📥 正在下載 {display_name} ({yf_ticker}) 的歷史資料...")
        try:
            ticker = yf.Ticker(yf_ticker)
            df = ticker.history(period="1y")
            
            if not df.empty:
                df.index = df.index.tz_localize(None)
                dates = df.index.strftime('%Y/%m/%d').tolist()
                closes = df['Close'].tolist()
                
                all_data[display_name] = {
                    'dates': dates,
                    'closePrices': closes
                }
            else:
                print(f"⚠️ 警告: 無法獲取 {display_name} 的資料")
                
            time.sleep(0.5)
            
        except Exception as e:
            print(f"❌ 獲取 {display_name} 時發生錯誤: {e}")

    json_data_str = json.dumps(all_data)
    print(f"\n✅ 數據抓取完成！共取得 {len(all_data)} 檔標的資料。")
    print("⏳ 正在將真實數據融合並生成 HTML...")

    # ==========================================
    # HTML 介面模板 (移除 AI 版，使用 Raw String 避免語法錯誤)
    # ==========================================
    html_template = r"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>專業技術分析儀表板 (真實數據版)</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://unpkg.com/@phosphor-icons/web"></script>
    <style>
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
        ::-webkit-scrollbar-thumb:hover { background: #94a3b8; }
        .table-container { max-height: 450px; overflow-y: auto; }
        .hide-scrollbar::-webkit-scrollbar { display: none; }
        .hide-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
    </style>
</head>
<body class="bg-slate-50 text-slate-800 font-sans antialiased min-h-screen flex flex-col">

    <nav class="bg-white border-b border-slate-200 sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
            <div class="flex items-center gap-3">
                <div>
                    <h1 id="main-title" class="text-xl font-bold text-slate-900 leading-tight">量化儀表板</h1>
                    <p id="sub-title" class="text-xs text-slate-500 font-medium">載入中...</p>
                </div>
            </div>
            <div class="flex items-center gap-3">
                <span class="flex items-center gap-1.5 px-3 py-1.5 bg-emerald-100 text-emerald-800 rounded-full text-xs font-bold border border-emerald-200 shadow-sm">
                    <span class="relative flex h-2 w-2">
                        <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                        <span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                    </span>
                    真實數據模式 (已連線)
                </span>
            </div>
        </div>
    </nav>

    <main class="flex-grow max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 w-full space-y-6">
        
        <div class="flex items-center gap-6 overflow-x-auto bg-white px-5 py-3 rounded-xl shadow-sm border border-slate-200 hide-scrollbar" id="index-ticker">
            <div class="animate-pulse h-5 w-full bg-slate-100 rounded"></div>
        </div>

        <div class="flex items-center gap-1 overflow-x-auto pb-0 border-b border-slate-200 hide-scrollbar" id="asset-selector"></div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-200 hover:shadow-md transition-shadow">
                <div class="flex justify-between items-start mb-2">
                    <h3 class="text-sm font-semibold text-slate-500">真實收盤價</h3>
                    <i class="ph ph-currency-dollar text-slate-400 text-lg"></i>
                </div>
                <div class="flex items-baseline gap-2">
                    <p id="card-price" class="text-3xl font-bold text-slate-900">--</p>
                    <span id="card-price-change" class="text-sm font-medium">--</span>
                </div>
            </div>
            
            <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-200 hover:shadow-md transition-shadow">
                <div class="flex justify-between items-start mb-2">
                    <h3 class="text-sm font-semibold text-slate-500">20日均線趨勢</h3>
                    <i class="ph ph-chart-line text-slate-400 text-lg"></i>
                </div>
                <p id="card-sma" class="text-3xl font-bold text-slate-900 mb-1">--</p>
                <p id="card-sma-status" class="text-xs text-slate-500">--</p>
            </div>

            <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-200 hover:shadow-md transition-shadow">
                <div class="flex justify-between items-start mb-2">
                    <h3 class="text-sm font-semibold text-slate-500">RSI 動能 (14日)</h3>
                    <i class="ph ph-gauge text-slate-400 text-lg"></i>
                </div>
                <div class="flex items-center gap-3 mt-1">
                    <p id="card-rsi" class="text-3xl font-bold text-slate-900">--</p>
                    <span id="card-rsi-badge" class="px-2 py-1 rounded text-xs font-bold bg-slate-100 text-slate-600 border border-slate-200">計算中</span>
                </div>
            </div>

            <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-200 hover:shadow-md transition-shadow">
                <div class="flex justify-between items-start mb-2">
                    <h3 class="text-sm font-semibold text-slate-500">最新訊號觸發</h3>
                    <i class="ph ph-broadcast text-slate-400 text-lg"></i>
                </div>
                <div id="card-signals" class="mt-2 flex flex-col gap-1.5"></div>
            </div>
        </div>

        <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
            <h2 class="text-lg font-bold text-slate-800 flex items-center gap-2 mb-4">
                <i class="ph ph-newspaper text-indigo-500 text-xl"></i>
                近期重點新聞
            </h2>
            <div id="news-container" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"></div>
        </div>

        <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
            <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 gap-4">
                <h2 class="text-lg font-bold text-slate-800 flex items-center gap-2">
                    <i class="ph ph-chart-polar text-indigo-500 text-xl"></i>
                    股價走勢與技術訊號
                </h2>
                <div class="flex bg-slate-100 p-1 rounded-lg border border-slate-200">
                    <button onclick="filterData(30)" id="btn-30" class="time-btn px-4 py-1.5 text-sm font-medium rounded-md text-slate-500 hover:text-slate-900 transition-colors">1個月</button>
                    <button onclick="filterData(90)" id="btn-90" class="time-btn px-4 py-1.5 text-sm font-medium rounded-md text-slate-500 hover:text-slate-900 transition-colors">3個月</button>
                    <button onclick="filterData(130)" id="btn-130" class="time-btn px-4 py-1.5 text-sm font-medium rounded-md text-slate-500 hover:text-slate-900 transition-colors">半年</button>
                    <button onclick="filterData(250)" id="btn-250" class="time-btn px-4 py-1.5 text-sm font-medium rounded-md bg-white text-indigo-600 shadow-sm border border-slate-200 transition-colors">1年</button>
                </div>
            </div>
            <div class="relative h-[450px] w-full"><canvas id="priceChart"></canvas></div>
        </div>

        <div class="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
            <div class="px-6 py-4 border-b border-slate-200 flex justify-between items-center bg-slate-50/50">
                <h2 class="text-lg font-bold text-slate-800 flex items-center gap-2">
                    <i class="ph ph-table text-indigo-500 text-xl"></i>
                    歷史數據明細
                </h2>
                <span class="text-xs text-slate-500 font-medium">高亮顯示發生訊號的交易日</span>
            </div>
            <div class="table-container">
                <table class="w-full text-left border-collapse relative">
                    <thead class="sticky top-0 bg-slate-100 shadow-sm z-10">
                        <tr class="text-slate-500 text-xs font-bold uppercase tracking-wider">
                            <th class="px-6 py-3">日期</th>
                            <th class="px-6 py-3">當日訊號</th>
                            <th class="px-6 py-3 text-right">收盤價</th>
                            <th class="px-6 py-3 text-right">SMA (20)</th>
                            <th class="px-6 py-3 text-right">RSI (14)</th>
                            <th class="px-6 py-3 text-right">MACD 柱狀圖</th>
                        </tr>
                    </thead>
                    <tbody id="data-table-body" class="divide-y divide-slate-100 text-slate-700 text-sm bg-white"></tbody>
                </table>
            </div>
        </div>

    </main>

    <script>
        // === 接收來自 Python 的真實數據 ===
        const serverData = __DATA_PLACEHOLDER__;

        let globalFullData = [];
        let currentChart = null;
        let currentSymbol = 'VTI';
        let currentTimeFrame = 250;
        
        const ASSETS = {
            'VTI': { name: 'Vanguard Total Stock Market ETF' },
            'MSFT': { name: 'Microsoft Corporation' },
            'GOOG': { name: 'Alphabet Inc.' },
            'NVDA': { name: 'NVIDIA Corporation' },
            'KO': { name: 'The Coca-Cola Company' },
            'S&P 500': { name: '標普 500 指數 (S&P 500)' },
            'NASDAQ': { name: '納斯達克綜合指數 (NASDAQ)' },
            'DJI': { name: '道瓊工業平均指數 (Dow Jones)' },
            'VIX': { name: '恐慌指數 (CBOE Volatility Index)' }
        };

        const MOCK_NEWS = {
            'VTI': [
                { title: '美股大盤持續震盪，聯準會利率決策成市場焦點', time: '2 小時前', source: '華爾街日報' },
                { title: 'Vanguard 宣布調整部分 ETF 費用率，吸引長期投資人', time: '5 小時前', source: '彭博社' },
                { title: '科技股領漲帶動大盤，全市場 ETF 淨流入創本月新高', time: '1 天前', source: '路透社' }
            ],
            'MSFT': [
                { title: '微軟 Copilot 企業版訂閱超預期，AI 變現能力顯現', time: '1 小時前', source: 'CNBC' },
                { title: 'Azure 雲端營收強勢成長，市佔率進一步逼近 AWS', time: '4 小時前', source: '金融時報' },
                { title: '微軟宣佈加碼投資新一代 AI 基礎設施與冷卻技術', time: '昨天', source: 'TechCrunch' }
            ],
            'GOOG': [
                { title: 'Google I/O 大會發表全新 Gemini 模型，效能大幅躍進', time: '3 小時前', source: 'The Verge' },
                { title: 'Alphabet 廣告營收回溫，YouTube 貢獻強勁成長', time: '6 小時前', source: '彭博社' },
                { title: 'Waymo 自動駕駛計程車獲准擴展至洛杉磯市區', time: '2 天前', source: '路透社' }
            ],
            'NVDA': [
                { title: '輝達新一代 AI 晶片面臨供不應求，台積電急單湧入', time: '15 分鐘前', source: '華爾街日報' },
                { title: '黃仁勳演講：AI 工業革命才剛開始，主權 AI 需求爆發', time: '3 小時前', source: 'CNBC' },
                { title: '華爾街分析師全面上調 NVIDIA 目標價，看好後市', time: '1 天前', source: 'Barron\'s' }
            ],
            'KO': [
                { title: '可口可樂最新財報擊敗預期，展現強大品牌定價能力', time: '4 小時前', source: '彭博社' },
                { title: '巴菲特持續長抱，KO 股息連續 62 年穩定成長', time: '12 小時前', source: 'CNBC' },
                { title: '無糖系列產品銷量大增，帶動新興市場整體營收', time: '昨天', source: '金融時報' }
            ]
        };

        const TA = {
            sma: (data, period) => {
                let res = new Array(data.length).fill(null);
                for (let i = period - 1; i < data.length; i++) {
                    let sum = 0; for (let j = 0; j < period; j++) sum += data[i - j];
                    res[i] = sum / period;
                }
                return res;
            },
            ema: (data, period) => {
                let res = new Array(data.length).fill(null);
                let multiplier = 2 / (period + 1);
                let start = data.findIndex(v => v !== null);
                if (start === -1) return res;
                res[start] = data[start];
                for (let i = start + 1; i < data.length; i++) {
                    if (data[i] !== null) res[i] = (data[i] - res[i - 1]) * multiplier + res[i - 1];
                }
                return res;
            },
            rsi: (data, period = 14) => {
                let res = new Array(data.length).fill(null);
                let gains = [], losses = [];
                for (let i = 1; i < data.length; i++) {
                    let diff = data[i] - data[i - 1];
                    gains.push(diff > 0 ? diff : 0);
                    losses.push(diff < 0 ? Math.abs(diff) : 0);
                }
                if (gains.length < period) return res;
                
                let avgGain = gains.slice(0, period).reduce((a, b) => a + b, 0) / period;
                let avgLoss = losses.slice(0, period).reduce((a, b) => a + b, 0) / period;
                for (let i = period; i < data.length; i++) {
                    if (i > period) {
                        avgGain = (avgGain * (period - 1) + gains[i - 1]) / period;
                        avgLoss = (avgLoss * (period - 1) + losses[i - 1]) / period;
                    }
                    let rs = avgLoss === 0 ? 100 : avgGain / avgLoss;
                    res[i] = avgLoss === 0 ? 100 : 100 - (100 / (1 + rs));
                }
                return res;
            }
        };

        function renderIndexTicker() {
            const tickerContainer = document.getElementById('index-ticker');
            tickerContainer.innerHTML = '';
            
            const tickerSymbols = ['S&P 500', 'NASDAQ', 'DJI', 'VIX'];

            tickerSymbols.forEach(sym => {
                const raw = serverData[sym];
                if (!raw || !raw.closePrices || raw.closePrices.length < 2) return;
                
                const closes = raw.closePrices;
                const currentClose = closes[closes.length - 1];
                const prevClose = closes[closes.length - 2];
                const change = currentClose - prevClose;
                const changePct = (change / prevClose) * 100;

                const isPositive = change >= 0;
                const colorClass = isPositive ? 'text-emerald-600' : 'text-rose-600';
                const bgClass = isPositive ? 'bg-emerald-50' : 'bg-rose-50';
                const icon = isPositive ? 'ph-caret-up' : 'ph-caret-down';
                const sign = isPositive ? '+' : '';

                const itemDiv = document.createElement('div');
                itemDiv.className = "flex flex-col min-w-max border-r border-slate-100 pr-6 last:border-0 last:pr-0";
                itemDiv.innerHTML = `
                    <span class="text-slate-400 font-bold text-[10px] uppercase tracking-wider mb-0.5">${sym}</span>
                    <div class="flex items-center gap-2 font-semibold">
                        <span class="text-slate-800">${currentClose.toFixed(2)}</span>
                        <span class="text-[11px] flex items-center ${bgClass} ${colorClass} px-1.5 py-0.5 rounded font-bold">
                            <i class="ph ${icon} mr-0.5"></i> ${sign}${change.toFixed(2)} (${sign}${changePct.toFixed(2)}%)
                        </span>
                    </div>
                `;
                tickerContainer.appendChild(itemDiv);
            });
        }

        function renderAssetTabs() {
            const container = document.getElementById('asset-selector');
            container.innerHTML = '';
            
            Object.keys(ASSETS).forEach(sym => {
                if(!serverData[sym]) return;

                const btn = document.createElement('button');
                const isSelected = sym === currentSymbol;
                
                btn.innerText = sym;
                btn.onclick = () => switchAsset(sym);
                
                if (isSelected) {
                    btn.className = "px-6 py-2.5 text-sm font-bold rounded-t-lg border-b-2 border-indigo-600 text-indigo-700 bg-white shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.05)] transition-all";
                } else {
                    btn.className = "px-6 py-2.5 text-sm font-medium rounded-t-lg border-b-2 border-transparent text-slate-500 hover:text-slate-800 hover:bg-slate-200/50 transition-all";
                }
                container.appendChild(btn);
            });
        }

        function switchAsset(symbol) {
            if (currentSymbol === symbol) return;
            currentSymbol = symbol;
            
            document.getElementById('main-title').innerText = `${symbol} 量化儀表板`;
            document.getElementById('sub-title').innerText = ASSETS[symbol].name;

            renderAssetTabs();
            processDataForCurrentSymbol();
            renderNews(); 
        }

        function renderNews() {
            const container = document.getElementById('news-container');
            container.innerHTML = '';
            
            const newsList = MOCK_NEWS[currentSymbol] || [
                { title: '美國非農就業數據超預期，市場重新評估降息機率', time: '1 小時前', source: '華爾街日報' },
                { title: '通膨數據溫和降溫，美股三大指數早盤集體開高', time: '3 小時前', source: '彭博社' },
                { title: '地緣政治風險降溫，VIX 恐慌指數回落至歷史均值以下', time: '1 天前', source: '路透社' }
            ];

            newsList.forEach(news => {
                const newsCard = document.createElement('div');
                newsCard.className = "flex items-start gap-3 p-4 rounded-xl border border-slate-100 hover:border-indigo-100 hover:bg-indigo-50/30 transition-all cursor-pointer shadow-sm hover:shadow";
                newsCard.innerHTML = `
                    <div class="mt-0.5 bg-slate-100 text-slate-500 p-2 rounded-lg flex-shrink-0">
                        <i class="ph-fill ph-article text-lg"></i>
                    </div>
                    <div>
                        <h4 class="text-sm font-bold text-slate-800 mb-1.5 leading-snug">${news.title}</h4>
                        <div class="flex items-center gap-2 text-xs text-slate-500 font-medium">
                            <span class="text-indigo-600">${news.source}</span>
                            <span>•</span>
                            <span>${news.time}</span>
                        </div>
                    </div>
                `;
                container.appendChild(newsCard);
            });
        }

        function processDataForCurrentSymbol() {
            const raw = serverData[currentSymbol];
            if (!raw) return;

            const dates = raw.dates;
            const closes = raw.closePrices;

            const sma20 = TA.sma(closes, 20);
            const rsi14 = TA.rsi(closes, 14);
            const ema12 = TA.ema(closes, 12);
            const ema26 = TA.ema(closes, 26);
            const macdLine = closes.map((_, i) => (ema12[i] !== null && ema26[i] !== null) ? ema12[i] - ema26[i] : null);
            const macdSignal = TA.ema(macdLine, 9);
            const macdHist = closes.map((_, i) => (macdLine[i] !== null && macdSignal[i] !== null) ? macdLine[i] - macdSignal[i] : null);

            const signals = new Array(closes.length).fill().map(() => []);
            const buyPoints = new Array(closes.length).fill(null);
            const sellPoints = new Array(closes.length).fill(null);

            for(let i = 1; i < closes.length; i++) {
                let hasBuy = false, hasSell = false;
                
                if (sma20[i-1] !== null) {
                    if (closes[i-1] <= sma20[i-1] && closes[i] > sma20[i]) { signals[i].push({ type: 'buy', text: '站上月線' }); hasBuy = true; }
                    else if (closes[i-1] >= sma20[i-1] && closes[i] < sma20[i]) { signals[i].push({ type: 'sell', text: '跌破月線' }); hasSell = true; }
                }
                if (macdLine[i-1] !== null) {
                    if (macdLine[i-1] <= macdSignal[i-1] && macdLine[i] > macdSignal[i]) { signals[i].push({ type: 'buy', text: 'MACD 金叉' }); hasBuy = true; }
                    else if (macdLine[i-1] >= macdSignal[i-1] && macdLine[i] < macdSignal[i]) { signals[i].push({ type: 'sell', text: 'MACD 死叉' }); hasSell = true; }
                }
                if (rsi14[i-1] !== null) {
                    if (rsi14[i-1] >= 30 && rsi14[i] < 30) { signals[i].push({ type: 'buy', text: 'RSI 超賣' }); hasBuy = true; }
                    else if (rsi14[i-1] <= 70 && rsi14[i] > 70) { signals[i].push({ type: 'sell', text: 'RSI 超買' }); hasSell = true; }
                }

                if (hasBuy) buyPoints[i] = closes[i];
                if (hasSell) sellPoints[i] = closes[i];
            }

            globalFullData = dates.map((date, index) => ({
                date, close: closes[index], prevClose: index > 0 ? closes[index-1] : closes[index],
                sma20: sma20[index], rsi: rsi14[index], macd: macdLine[index], macdSignal: macdSignal[index], macdHist: macdHist[index],
                signals: signals[index], buyPoint: buyPoints[index], sellPoint: sellPoints[index]
            }));

            filterData(currentTimeFrame); 
        }

        function initDashboard() {
            if (!serverData || Object.keys(serverData).length === 0) {
                alert("未接收到真實數據，請確認 Python 腳本執行狀態。");
                return;
            }
            if (!serverData[currentSymbol]) {
                currentSymbol = Object.keys(serverData)[0];
            }

            renderIndexTicker(); 
            renderAssetTabs();
            processDataForCurrentSymbol();
            renderNews(); 
        }

        function filterData(days) {
            currentTimeFrame = days; 
            document.querySelectorAll('.time-btn').forEach(btn => {
                btn.className = "time-btn px-4 py-1.5 text-sm font-medium rounded-md text-slate-500 hover:text-slate-900 transition-colors";
            });
            const activeBtn = document.getElementById(`btn-${days}`);
            if(activeBtn) activeBtn.className = "time-btn px-4 py-1.5 text-sm font-medium rounded-md bg-white text-indigo-600 shadow-sm border border-slate-200 transition-colors";

            const slicedData = globalFullData.slice(-days);
            
            updateCards(globalFullData[globalFullData.length - 1]);
            renderChart(slicedData);
            renderTable(slicedData.slice().reverse()); 
        }

        function updateCards(latest) {
            const priceChange = latest.close - latest.prevClose;
            const priceChangePct = (priceChange / latest.prevClose) * 100;
            document.getElementById('card-price').innerText = `$${latest.close.toFixed(2)}`;
            const changeEl = document.getElementById('card-price-change');
            if(priceChange >= 0) {
                changeEl.innerHTML = `<i class="ph ph-trend-up"></i> +${priceChange.toFixed(2)} (+${priceChangePct.toFixed(2)}%)`;
                changeEl.className = "text-sm font-bold text-emerald-600 flex items-center gap-1";
            } else {
                changeEl.innerHTML = `<i class="ph ph-trend-down"></i> ${priceChange.toFixed(2)} (${priceChangePct.toFixed(2)}%)`;
                changeEl.className = "text-sm font-bold text-rose-600 flex items-center gap-1";
            }

            document.getElementById('card-sma').innerText = latest.sma20 ? `$${latest.sma20.toFixed(2)}` : '--';
            const smaStatusEl = document.getElementById('card-sma-status');
            if(latest.sma20) {
                if(latest.close > latest.sma20) smaStatusEl.innerHTML = `<span class="text-emerald-600 font-bold">強勢</span> · 股價站上月線`;
                else smaStatusEl.innerHTML = `<span class="text-rose-600 font-bold">弱勢</span> · 股價跌破月線`;
            }

            if (latest.rsi) {
                document.getElementById('card-rsi').innerText = latest.rsi.toFixed(1);
                const badge = document.getElementById('card-rsi-badge');
                if (latest.rsi > 70) { badge.innerText = "超買區"; badge.className = "px-2 py-0.5 rounded text-xs font-bold bg-rose-100 text-rose-700 border border-rose-200"; } 
                else if (latest.rsi < 30) { badge.innerText = "超賣區"; badge.className = "px-2 py-0.5 rounded text-xs font-bold bg-emerald-100 text-emerald-700 border border-emerald-200"; } 
                else { badge.innerText = "中性動能"; badge.className = "px-2 py-0.5 rounded text-xs font-bold bg-slate-100 text-slate-600 border border-slate-200"; }
            }

            const signalsContainer = document.getElementById('card-signals');
            if (latest.signals.length > 0) {
                signalsContainer.innerHTML = latest.signals.map(s => {
                    const style = s.type === 'buy' 
                        ? 'bg-emerald-50 text-emerald-700 border-emerald-200 shadow-sm' 
                        : 'bg-rose-50 text-rose-700 border-rose-200 shadow-sm';
                    const icon = s.type === 'buy' ? 'ph-arrow-up-right' : 'ph-arrow-down-right';
                    return `<div class="flex items-center gap-2 px-3 py-1.5 rounded-lg border ${style} text-sm font-bold w-max">
                                <i class="ph ${icon} text-lg"></i> ${s.text}
                            </div>`;
                }).join('');
            } else {
                signalsContainer.innerHTML = '<div class="text-slate-400 text-sm font-medium mt-1">今日無觸發特殊訊號</div>';
            }
        }

        function renderChart(data) {
            const ctx = document.getElementById('priceChart').getContext('2d');
            if(currentChart) currentChart.destroy();

            let gradient = ctx.createLinearGradient(0, 0, 0, 400);
            gradient.addColorStop(0, 'rgba(99, 102, 241, 0.2)'); 
            gradient.addColorStop(1, 'rgba(99, 102, 241, 0.0)');

            currentChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.map(d => d.date),
                    datasets: [
                        {
                            label: '買進訊號', data: data.map(d => d.buyPoint), 
                            pointStyle: 'triangle', pointBackgroundColor: '#10b981', pointBorderColor: '#047857', pointBorderWidth: 1, pointRadius: 9, pointHoverRadius: 12, showLine: false, order: 1 
                        },
                        {
                            label: '賣出訊號', data: data.map(d => d.sellPoint), 
                            pointStyle: 'triangle', rotation: 180, pointBackgroundColor: '#f43f5e', pointBorderColor: '#be123c', pointBorderWidth: 1, pointRadius: 9, pointHoverRadius: 12, showLine: false, order: 1 
                        },
                        {
                            label: '收盤價', data: data.map(d => d.close), 
                            borderColor: '#6366f1', 
                            backgroundColor: gradient,
                            borderWidth: 2.5,
                            pointRadius: 0, pointHitRadius: 15,
                            fill: true, tension: 0.1, order: 3 
                        },
                        {
                            label: '20 日均線', data: data.map(d => d.sma20), 
                            borderColor: '#f59e0b', 
                            borderWidth: 1.5,
                            borderDash: [5, 5],
                            pointRadius: 0, fill: false, tension: 0.1, order: 2 
                        }
                    ]
                },
                options: {
                    responsive: true, maintainAspectRatio: false,
                    interaction: { mode: 'index', intersect: false },
                    plugins: { 
                        legend: { display: false }, 
                        tooltip: {
                            backgroundColor: 'rgba(15, 23, 42, 0.9)', 
                            titleFont: { size: 14, family: 'sans-serif' },
                            bodyFont: { size: 13, family: 'sans-serif' },
                            padding: 12,
                            cornerRadius: 8,
                            callbacks: {
                                label: function(context) {
                                    let label = context.dataset.label || '';
                                    if (label && !label.includes('訊號')) { label += ': '; }
                                    if (context.parsed.y !== null && !label.includes('訊號')) { 
                                        label += '$' + context.parsed.y.toFixed(2); 
                                    }
                                    return label;
                                }
                            }
                        }
                    },
                    scales: { 
                        x: { grid: { display: false }, ticks: { maxTicksLimit: 6, color: '#64748b' } }, 
                        y: { grid: { color: '#f1f5f9' }, ticks: { color: '#64748b' } } 
                    }
                }
            });
        }

        function renderTable(recentData) {
            const tbody = document.getElementById('data-table-body');
            tbody.innerHTML = ''; 
            const formatNum = (val, dec = 2) => val !== null ? val.toFixed(dec) : '-';

            recentData.forEach(row => {
                const tr = document.createElement('tr');
                
                let rowBgClass = "hover:bg-slate-50 transition-colors border-b border-slate-100";
                let hasBuy = row.signals.some(s => s.type === 'buy');
                let hasSell = row.signals.some(s => s.type === 'sell');
                
                if (hasBuy && hasSell) rowBgClass = "bg-amber-50/50 hover:bg-amber-50 transition-colors border-b border-amber-100"; 
                else if (hasBuy) rowBgClass = "bg-emerald-50/40 hover:bg-emerald-50 transition-colors border-b border-emerald-100";
                else if (hasSell) rowBgClass = "bg-rose-50/40 hover:bg-rose-50 transition-colors border-b border-rose-100";

                tr.className = rowBgClass;
                
                let badges = row.signals && row.signals.length > 0 
                    ? row.signals.map(s => {
                        const style = s.type === 'buy' ? 'bg-emerald-100 text-emerald-700 border-emerald-200' : 'bg-rose-100 text-rose-700 border-rose-200';
                        return `<span class="inline-block px-2 py-0.5 rounded-md text-[11px] font-bold border ${style} mr-1 shadow-sm">${s.text}</span>`;
                    }).join('') 
                    : '<span class="text-slate-300 font-medium">-</span>';

                let macdColor = row.macdHist !== null ? (row.macdHist > 0 ? 'text-emerald-600' : 'text-rose-600') : '';

                tr.innerHTML = `
                    <td class="px-6 py-3.5 whitespace-nowrap text-slate-900 font-medium font-mono text-sm">${row.date}</td>
                    <td class="px-6 py-3.5 whitespace-nowrap">${badges}</td>
                    <td class="px-6 py-3.5 whitespace-nowrap text-right text-slate-900 font-bold">$${formatNum(row.close)}</td>
                    <td class="px-6 py-3.5 whitespace-nowrap text-right text-slate-500">${formatNum(row.sma20)}</td>
                    <td class="px-6 py-3.5 whitespace-nowrap text-right text-slate-500">${formatNum(row.rsi)}</td>
                    <td class="px-6 py-3.5 whitespace-nowrap text-right font-bold ${macdColor}">${formatNum(row.macdHist, 3)}</td>
                `;
                tbody.appendChild(tr);
            });
        }

        window.onload = initDashboard;
    </script>
</body>
</html>
"""

    # 將真實數據轉換並替換掉佔位符
    final_html = html_template.replace("__DATA_PLACEHOLDER__", json_data_str)

    # 匯出的檔名已更改為 index.html (方便直接推上 Github Pages 使用)
    filename = "index.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(final_html)

    print(f"✅ 大功告成！已成功生成：{filename}")
    print(f"👉 請在您的電腦資料夾中找到 '{filename}'，點兩下用瀏覽器打開即可觀看即時真實數據分析！")

if __name__ == "__main__":
    fetch_real_data()