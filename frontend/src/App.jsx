import React, { useState } from 'react';
import { Search, Bell, Settings, LayoutDashboard, Briefcase, Activity, FileText, User, AlertTriangle, ShieldCheck, CheckCircle2, ChevronRight, Copy } from 'lucide-react';

function App() {
  const [ticker, setTicker] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleAnalyze = async () => {
    if (!ticker.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch(`http://localhost:8000/api/analyze?ticker=${ticker}`);
      const data = await response.json();
      
      if (data.error) {
        setError(data.error);
      } else {
        setResult(data);
      }
    } catch (err) {
      setError("Failed to connect to the analysis server.");
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = () => {
    if (result && result.report) {
      navigator.clipboard.writeText(result.report);
      alert("Report copied to clipboard!");
    }
  };

  return (
    <div className="flex h-screen bg-background text-textPrimary overflow-hidden font-sans">
      
      {/* SIDEBAR */}
      <aside className="w-64 border-r border-border bg-background flex flex-col hidden md:flex">
        <div className="p-6 border-b border-border/50">
          <div className="flex items-center gap-2 text-accentGreen font-bold text-xl tracking-wide">
            <Activity size={24} />
            <span>QUANTEDGE</span>
          </div>
          <div className="text-xs text-textSecondary mt-1 uppercase tracking-wider font-semibold flex items-center gap-1">
            <span className="w-4 h-4 bg-card rounded flex items-center justify-center text-[10px]">AI</span>
            INSTITUTIONAL GRADE
          </div>
        </div>

        <nav className="flex-1 py-6 flex flex-col gap-2 px-2">
          <div className="nav-item active">
            <LayoutDashboard size={20} />
            <span>Terminal</span>
          </div>
          <div className="nav-item">
            <Briefcase size={20} />
            <span>Portfolio</span>
          </div>
          <div className="nav-item">
            <Activity size={20} />
            <span>Signals</span>
          </div>
          <div className="nav-item">
            <FileText size={20} />
            <span>Reports</span>
          </div>
          <div className="nav-item">
            <Settings size={20} />
            <span>Settings</span>
          </div>
        </nav>

        <div className="p-6 border-t border-border/50">
          <button className="btn-primary w-full">NEW ANALYSIS</button>
        </div>
      </aside>

      {/* MAIN CONTENT */}
      <main className="flex-1 flex flex-col overflow-hidden">
        
        {/* TOPBAR */}
        <header className="h-16 border-b border-border bg-background flex items-center justify-between px-8">
          <div className="flex items-center gap-6 text-sm font-medium text-textSecondary">
            <span className="text-accentGreen border-b-2 border-accentGreen pb-1 text-textPrimary">Terminal</span>
            <span className="hover:text-textPrimary cursor-pointer">Portfolio</span>
            <span className="hover:text-textPrimary cursor-pointer">Signals</span>
            <span className="hover:text-textPrimary cursor-pointer">Reports</span>
          </div>
          <div className="flex items-center gap-4 text-textSecondary">
            <Bell size={20} className="hover:text-textPrimary cursor-pointer" />
            <Settings size={20} className="hover:text-textPrimary cursor-pointer" />
            <div className="w-8 h-8 rounded-full bg-accentRed/20 flex items-center justify-center text-accentRed border border-accentRed/50">
              <User size={16} />
            </div>
          </div>
        </header>

        {/* DASHBOARD AREA */}
        <div className="flex-1 overflow-y-auto p-8">
          
          {/* MARKET QUERY */}
          <div className="card-panel mb-6">
            <h2 className="text-xs uppercase tracking-widest text-textSecondary mb-4 font-semibold">MARKET QUERY</h2>
            <div className="flex gap-4">
              <div className="flex-1 relative">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-textSecondary" size={20} />
                <input 
                  type="text" 
                  placeholder="e.g., RELIANCE.NS, AAPL" 
                  value={ticker}
                  onChange={(e) => setTicker(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleAnalyze()}
                  className="w-full bg-background border border-border rounded py-3 pl-12 pr-4 focus:outline-none focus:border-accentGreen transition-colors text-lg uppercase"
                />
              </div>
              <button onClick={handleAnalyze} className="btn-primary" disabled={loading}>
                {loading ? 'ANALYZING...' : 'ANALYZE'}
              </button>
            </div>
            {error && <div className="mt-4 text-accentRed text-sm flex items-center gap-2"><AlertTriangle size={16}/> {error}</div>}
          </div>

          {result && result.data && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              
              {/* LEFT COLUMN */}
              <div className="col-span-2 space-y-6">
                
                {/* STOCK HEADER */}
                <div className="card-panel flex justify-between items-start">
                  <div>
                    <h1 className="text-2xl font-bold">{result.data.stock_name}</h1>
                    <div className="text-textSecondary mt-1 flex items-center gap-2">
                      <span className="text-textPrimary">{result.data.symbol}</span>
                      <span>•</span>
                      <span>{result.data.sector} Sector</span>
                    </div>
                    <div className="flex gap-3 mt-6">
                      <div className={`px-4 py-1 rounded-full border text-xs tracking-wider uppercase font-bold ${
                        result.data.trend === 'BULLISH' ? 'border-accentGreen text-accentGreen' : 
                        result.data.trend === 'BEARISH' ? 'border-accentRed text-accentRed' : 
                        'border-textSecondary text-textSecondary'
                      }`}>
                        {result.data.trend}
                      </div>
                      <div className={`px-4 py-1 rounded-full border text-xs tracking-wider uppercase font-bold ${
                        result.data.vol_state.includes('SQUEEZE') ? 'border-accentGreen text-accentGreen' : 'border-textSecondary text-textSecondary'
                      }`}>
                        {result.data.vol_state}
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-mono text-accentGreen">₹{result.data.current_price.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits:2})}</div>
                    <div className="text-textSecondary mt-1 text-sm">₹{result.data.market_cap} Market Cap</div>
                  </div>
                </div>

                {/* TECHNICAL INDICATORS */}
                <div className="card-panel">
                  <h2 className="text-xs uppercase tracking-widest text-textSecondary mb-4 font-semibold">TECHNICAL INDICATORS</h2>
                  <div className="w-full">
                    <div className="grid grid-cols-3 text-textSecondary pb-3 border-b border-border text-sm font-semibold">
                      <div>Metric</div>
                      <div>Value</div>
                      <div>Signal</div>
                    </div>
                    {result.data.metrics.map((m, i) => (
                      <div key={i} className="grid grid-cols-3 py-4 table-row-custom items-center">
                        <div className="font-medium text-textPrimary">{m.name}</div>
                        <div className="font-mono text-textPrimary">{m.value}</div>
                        <div className={`text-sm ${
                          m.signal.includes('Bullish') || m.signal.includes('Above') || m.signal.includes('Support') || m.signal === 'Oversold' 
                          ? 'text-accentGreen' 
                          : m.signal.includes('Bearish') || m.signal.includes('Below') || m.signal.includes('Resistance') || m.signal === 'Overbought'
                          ? 'text-accentRed'
                          : 'text-textSecondary'
                        }`}>{m.signal}</div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* AI SYNTHESIS */}
                <div className="card-panel border-l-2 border-l-accentGreen bg-card/80">
                  <h2 className="text-xs uppercase tracking-widest text-accentGreen mb-3 font-semibold flex items-center gap-2">
                    <ShieldCheck size={16} />
                    AI INTELLIGENCE SYNTHESIS
                  </h2>
                  <p className="text-textPrimary/90 leading-relaxed text-sm">
                    {result.data.reasoning}
                  </p>
                </div>
              </div>

              {/* RIGHT COLUMN */}
              <div className="space-y-6">
                
                {/* SCORE METER */}
                <div className="card-panel">
                  <h2 className="text-xs uppercase tracking-widest text-textSecondary mb-6 text-center font-semibold">QUANTEDGE SCORE</h2>
                  <div className="relative h-2 bg-gradient-to-r from-accentRed via-border to-accentGreen rounded-full mb-4">
                    <div 
                      className="absolute top-1/2 -translate-y-1/2 w-4 h-4 bg-white rounded-full shadow-[0_0_10px_white]"
                      style={{ left: `${((result.data.score + 10) / 20) * 100}%`, transform: 'translate(-50%, -50%)' }}
                    ></div>
                  </div>
                  <div className="flex justify-between text-xs text-textSecondary">
                    <span>-10 (Bearish)</span>
                    <span className={`font-mono font-bold ${result.data.score > 0 ? 'text-accentGreen' : result.data.score < 0 ? 'text-accentRed' : 'text-textSecondary'}`}>
                      {result.data.score > 0 ? '+' : ''}{result.data.score}
                    </span>
                    <span>+10 (Bullish)</span>
                  </div>
                </div>

                {/* DECISION BADGE */}
                <div className="card-panel flex flex-col items-center justify-center py-8">
                  <div className={`w-full py-6 rounded text-center text-4xl font-bold tracking-widest uppercase text-background mb-6 shadow-lg ${
                    result.data.decision === 'BUY' ? 'bg-accentGreen shadow-accentGreen/20' :
                    result.data.decision === 'SELL' ? 'bg-accentRed shadow-accentRed/20' :
                    'bg-accentYellow shadow-accentYellow/20'
                  }`}>
                    {result.data.decision}
                  </div>
                  <div className="flex gap-2 mb-4 text-accentGreen">
                    {[1, 2, 3].map(star => (
                      <svg key={star} width="24" height="24" viewBox="0 0 24 24" fill={star <= result.data.confidence_stars ? "currentColor" : "none"} stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
                      </svg>
                    ))}
                  </div>
                  <div className="text-textSecondary text-sm uppercase tracking-wider font-semibold">
                    {result.data.confidence_level} Grade Confidence
                  </div>
                </div>

                {/* LIVE SIGNALS */}
                <div className="card-panel">
                  <h2 className="text-xs uppercase tracking-widest text-textSecondary mb-4 font-semibold">LIVE SIGNALS</h2>
                  <div className="flex flex-wrap gap-2">
                    {result.data.scored_signals.map((sig, i) => {
                      const isBull = sig.includes('(+');
                      return (
                        <div key={i} className={`px-2 py-1 rounded text-[11px] border bg-background/50 whitespace-nowrap ${
                          isBull ? 'border-accentGreen/40 text-accentGreen' : 'border-accentRed/40 text-accentRed'
                        }`}>
                          {sig.split('(')[1]?.replace(')', '') || ''} {sig.split(' (')[0]}
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* RISK EXPOSURE */}
                <div className="card-panel border border-accentYellow/30 bg-[#1f1a10]">
                  <h2 className="text-xs uppercase tracking-widest text-accentYellow mb-3 font-semibold flex items-center gap-2">
                    <AlertTriangle size={16} />
                    RISK EXPOSURE
                  </h2>
                  <ul className="text-accentYellow/80 text-sm space-y-2">
                    {result.data.risk_notes.slice(0, 3).map((r, i) => (
                      <li key={i} className="flex gap-2 items-start">
                        <span className="text-accentYellow mt-1">•</span>
                        <span>{r.replace('• ', '')}</span>
                      </li>
                    ))}
                  </ul>
                </div>

              </div>
            </div>
          )}

          {/* FOOTER ACTIONS */}
          {result && (
            <div className="flex justify-end gap-4 mt-8 border-t border-border pt-6 pb-12">
              <button className="flex items-center gap-2 px-6 py-2 border border-border text-textPrimary hover:bg-white/5 rounded transition-colors text-sm uppercase tracking-widest font-semibold">
                Share Insight
              </button>
              <button onClick={handleCopy} className="flex items-center gap-2 px-6 py-2 bg-background border border-accentGreen/50 text-accentGreen hover:bg-accentGreen hover:text-background rounded transition-colors text-sm uppercase tracking-widest font-semibold">
                <Copy size={16} /> Copy Report
              </button>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
