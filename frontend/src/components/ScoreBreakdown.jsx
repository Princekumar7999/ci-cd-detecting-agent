import { useState, useEffect } from 'react';

export default function ScoreBreakdown({ data }) {
    const [now, setNow] = useState(Date.now());

    // Update time for live duration
    useEffect(() => {
        if (data.status === 'running') {
            const interval = setInterval(() => setNow(Date.now()), 1000);
            return () => clearInterval(interval);
        }
    }, [data.status]);

    const startTime = new Date(data.start_time).getTime();
    const endTime = data.end_time ? new Date(data.end_time).getTime() : now;
    const durationMs = Math.max(0, endTime - startTime);
    const durationMinutes = durationMs / 60000;

    const baseScore = 100;
    const speedBonus = durationMinutes < 5 ? 10 : 0;
    const commits = data.fixed_issues?.length || 0;
    const efficiencyPenalty = Math.max(0, (commits - 20) * 2);

    const totalScore = Math.max(0, baseScore + speedBonus - efficiencyPenalty);

    // Format duration
    const mins = Math.floor(durationMs / 60000);
    const secs = Math.floor((durationMs % 60000) / 1000);
    const timeString = `${mins}m ${secs}s`;

    return (
        <div className="card space-y-4 border-l-4 border-l-yellow-500 flex flex-col justify-between">
            <div className="flex justify-between items-start">
                <h2 className="text-xl font-bold text-slate-200 flex items-center gap-2">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-yellow-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                    </svg>
                    Score Breakdown
                </h2>
                <div className="text-right">
                    <div className="text-xs text-slate-400 uppercase">Duration</div>
                    <div className="font-mono text-yellow-400 font-bold">{timeString}</div>
                </div>
            </div>

            <div className="space-y-3 flex-grow justify-center flex flex-col">
                <div className="flex justify-between items-center text-sm border-b border-slate-700/50 pb-2">
                    <span className="text-slate-400">Base Score</span>
                    <span className="font-mono text-slate-200">100</span>
                </div>
                <div className="flex justify-between items-center text-sm border-b border-slate-700/50 pb-2">
                    <span className="text-slate-400">Speed Bonus (&lt; 5m)</span>
                    <span className={`font-mono ${speedBonus > 0 ? 'text-green-400' : 'text-slate-600'}`}>
                        {speedBonus > 0 ? '+' : ''}{speedBonus}
                    </span>
                </div>
                <div className="flex justify-between items-center text-sm border-b border-slate-700/50 pb-2">
                    <span className="text-slate-400">Efficiency Penalty (&gt; 20 commits)</span>
                    <span className={`font-mono ${efficiencyPenalty > 0 ? 'text-red-400' : 'text-slate-600'}`}>
                        -{efficiencyPenalty}
                    </span>
                </div>
            </div>

            <div className="pt-2 text-center">
                <div className="text-xs text-slate-500 uppercase tracking-widest mb-1">Total Score</div>
                <div className="text-5xl font-black text-transparent bg-clip-text bg-gradient-to-br from-yellow-300 to-amber-600">
                    {totalScore}
                </div>
            </div>
        </div>
    )
}
