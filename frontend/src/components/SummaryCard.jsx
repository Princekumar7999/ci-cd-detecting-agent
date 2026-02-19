export default function SummaryCard({ data }) {
    const failures = (data.lint_errors?.length || 0) + (data.test_failures?.length || 0);
    const fixes = data.fixed_issues?.length || 0;

    // Construct branch name exactly as required
    const branchName = `${data.team_name}_${data.leader_name}_AI_Fix`
        .toUpperCase()
        .replace(/ /g, '_');

    // Determine Pass/Fail Status
    // If it's completed and no errors remain, it passed.
    // "check_health" returns "passed" if empty errors.
    // We can infer current health from the lists.
    const currentFailures = (data.lint_errors?.length || 0) + (data.test_failures?.length || 0);
    const isPassed = data.status === 'completed' && currentFailures === 0;
    const isRunning = data.status === 'running';

    return (
        <div className="card space-y-4 border-l-4 border-l-blue-500">
            <h2 className="text-xl font-bold text-slate-200 flex items-center gap-2">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                Run Summary
            </h2>

            <div className="grid grid-cols-2 gap-y-4 gap-x-2 text-sm">
                <div>
                    <p className="text-slate-400 uppercase text-xs tracking-wider">Repository</p>
                    <a href={data.repo_url} target="_blank" rel="noopener noreferrer" className="font-mono text-blue-400 hover:text-blue-300 truncate block transition-colors">
                        {data.repo_url.replace('https://github.com/', '')}
                    </a>
                </div>
                <div>
                    <p className="text-slate-400 uppercase text-xs tracking-wider">Target Branch</p>
                    <p className="font-mono text-purple-400 truncate text-xs" title={branchName}>{branchName}</p>
                </div>
                <div>
                    <p className="text-slate-400 uppercase text-xs tracking-wider">Team</p>
                    <p className="font-medium">{data.team_name}</p>
                </div>
                <div>
                    <p className="text-slate-400 uppercase text-xs tracking-wider">Leader</p>
                    <p className="font-medium">{data.leader_name}</p>
                </div>
            </div>

            <div className="border-t border-slate-700 pt-4 grid grid-cols-3 gap-2 text-center">
                <div className="bg-slate-900/50 p-2 rounded-lg border border-slate-700/50">
                    <div className="text-2xl font-bold text-red-400">{failures + fixes}</div>
                    <div className="text-xs text-slate-500">Total Failures</div>
                </div>
                <div className="bg-slate-900/50 p-2 rounded-lg border border-slate-700/50">
                    <div className="text-2xl font-bold text-green-400">{fixes}</div>
                    <div className="text-xs text-slate-500">Fixes Applied</div>
                </div>
                <div className={`p-2 rounded-lg border flex items-center justify-center font-bold tracking-wider ${isRunning ? 'bg-blue-500/10 border-blue-500/20 text-blue-400' :
                        isPassed ? 'bg-green-500/10 border-green-500/20 text-green-400' :
                            'bg-red-500/10 border-red-500/20 text-red-400'
                    }`}>
                    {isRunning ? 'RUNNING' : (isPassed ? 'PASSED' : 'FAILED')}
                </div>
            </div>
        </div>
    )
}
