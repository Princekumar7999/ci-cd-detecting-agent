export default function FixesTable({ data }) {
    const fixes = data.fixed_issues || [];

    return (
        <div className="card h-full">
            <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-bold text-slate-200">Fixes Applied</h3>
                <span className="bg-slate-700 text-xs px-2 py-1 rounded text-slate-300">{fixes.length} Total</span>
            </div>

            <div className="overflow-x-auto">
                <table className="w-full text-left text-sm text-slate-400">
                    <thead className="bg-slate-700/50 text-slate-200 uppercase text-xs font-semibold">
                        <tr>
                            <th className="px-4 py-3 rounded-l-lg min-w-[150px]">File</th>
                            <th className="px-4 py-3">Bug Type</th>
                            <th className="px-4 py-3">Line</th>
                            <th className="px-4 py-3 min-w-[200px]">Commit Message</th>
                            <th className="px-4 py-3 rounded-r-lg text-center">Status</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-700">
                        {fixes.length === 0 ? (
                            <tr><td colSpan="5" className="px-4 py-8 text-center text-slate-500 italic">No fixes recorded yet. Waiting for analysis...</td></tr>
                        ) : (
                            fixes.map((fix, idx) => (
                                <tr key={idx} className="hover:bg-slate-800/50 transition-colors animate-fade-in-up" style={{ animationDelay: `${idx * 100}ms` }}>
                                    <td className="px-4 py-3 font-mono text-blue-400 font-medium">{fix.file}</td>
                                    <td className="px-4 py-3">
                                        <span className={`px-2 py-1 rounded text-xs font-bold border ${fix.bug_type === 'SYNTAX' ? 'bg-red-500/10 border-red-500/20 text-red-400' :
                                                fix.bug_type === 'LINTING' ? 'bg-yellow-500/10 border-yellow-500/20 text-yellow-400' :
                                                    'bg-blue-500/10 border-blue-500/20 text-blue-400'
                                            }`}>{fix.bug_type}</span>
                                    </td>
                                    <td className="px-4 py-3 font-mono">{fix.line}</td>
                                    <td className="px-4 py-3 text-slate-300 truncate max-w-xs" title={fix.commit_message}>
                                        {fix.commit_message}
                                    </td>
                                    <td className="px-4 py-3 text-center">
                                        {fix.status === 'Fixed' ? (
                                            <span className="text-green-400 font-bold flex items-center justify-center gap-1">
                                                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
                                                Fixed
                                            </span>
                                        ) : (
                                            <span className="text-red-400 font-bold flex items-center justify-center gap-1">
                                                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
                                                Failed
                                            </span>
                                        )}
                                    </td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    )
}
