export default function Timeline({ data }) {
    const iteration = data.iteration || 0;
    const maxIterations = data.max_iterations || 5;
    const status = data.status;
    const isPassed = data.status === 'completed' && (data.lint_errors?.length || 0) + (data.test_failures?.length || 0) === 0;

    return (
        <div className="card h-full flex flex-col">
            <h3 className="text-lg font-bold text-slate-200 mb-6">CI/CD Pipeline</h3>

            <div className="flex-grow space-y-0 relative pl-4">
                {/* Vertical Line */}
                <div className="absolute top-0 bottom-0 left-[19px] w-0.5 bg-slate-700"></div>

                {/* Start */}
                <div className="relative flex items-start gap-4 pb-8 group">
                    <div className="z-10 flex items-center justify-center w-10 h-10 rounded-full border-2 border-slate-700 bg-slate-900 shadow shrink-0 text-blue-500 group-hover:border-blue-500 transition-colors">
                        <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" viewBox="0 0 20 20" fill="currentColor">
                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-11a1 1 0 10-2 0v2H7a1 1 0 100 2h2v2a1 1 0 102 0v-2h2a1 1 0 100-2h-2V7z" clipRule="evenodd" />
                        </svg>
                    </div>
                    <div className="flex-1 pt-1">
                        <div className="flex justify-between items-start">
                            <div className="text-slate-200 font-bold">Analysis Started</div>
                            <time className="font-mono text-xs text-slate-500">{new Date(data.start_time).toLocaleTimeString()}</time>
                        </div>
                        <div className="text-xs text-slate-400 mt-1">Repository cloned & Initial Scan</div>
                    </div>
                </div>

                {/* Iterations */}
                {Array.from({ length: iteration }).map((_, i) => (
                    <div key={i} className="relative flex items-start gap-4 pb-8 group animate-fade-in-up" style={{ animationDelay: `${i * 200}ms` }}>
                        <div className="z-10 flex items-center justify-center w-10 h-10 rounded-full border-2 border-slate-700 bg-slate-900 shadow shrink-0 text-blue-400 group-hover:border-blue-400 transition-colors">
                            <span className="font-bold text-sm">{i + 1}</span>
                        </div>
                        <div className="flex-1 pt-1">
                            <div className="text-slate-200 font-bold">Iteration {i + 1}</div>
                            <div className="text-xs text-slate-400 mt-1">Automated Fix applied & Tests re-run</div>
                        </div>
                    </div>
                ))}

                {/* Current / End */}
                {(status === 'completed' || status === 'failed') && (
                    <div className="relative flex items-start gap-4 pb-0 group animate-fade-in">
                        <div className={`z-10 flex items-center justify-center w-10 h-10 rounded-full border-2 border-slate-700 bg-slate-900 shadow shrink-0 ${isPassed ? 'text-green-500 border-green-500' : 'text-red-500 border-red-500'} transition-colors`}>
                            {isPassed ? (
                                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
                            ) : (
                                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
                            )}
                        </div>
                        <div className="flex-1 pt-1">
                            <div className="flex justify-between items-start">
                                <div className={`font-bold ${isPassed ? 'text-green-400' : 'text-red-400'}`}>
                                    {isPassed ? 'Pipeline Passed' : 'Pipeline Failed'}
                                </div>
                                <time className="font-mono text-xs text-slate-500">{data.end_time ? new Date(data.end_time).toLocaleTimeString() : ''}</time>
                            </div>
                            <div className="text-xs text-slate-400 mt-1">Process finished</div>
                        </div>
                    </div>
                )}
            </div>

            <div className="mt-6 pt-4 border-t border-slate-700 text-center">
                <div className="inline-block px-3 py-1 bg-slate-800 rounded text-xs font-mono text-slate-400">
                    Pipeline Retries: {iteration} / {maxIterations}
                </div>
            </div>
        </div>
    )
}
