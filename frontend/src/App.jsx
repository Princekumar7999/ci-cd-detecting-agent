import { useState, useEffect } from 'react'
import Dashboard from './components/Dashboard'

function App() {
  const [repoUrl, setRepoUrl] = useState('')
  const [teamName, setTeamName] = useState('')
  const [leaderName, setLeaderName] = useState('')
  const [runId, setRunId] = useState(null)
  const [data, setData] = useState(null)
  const [isLoading, setIsLoading] = useState(false)

  // Polling logic
  useEffect(() => {
    let interval;
    if (runId && (isLoading || (data && data.status === 'running'))) {
      interval = setInterval(async () => {
        try {
          const res = await fetch(`http://localhost:8000/results/${runId}`)
          if (!res.ok) return;
          const json = await res.json()
          setData(json)
          if (json.status === 'completed' || json.status === 'failed') {
            setIsLoading(false)
          }
        } catch (e) {
          console.error(e)
        }
      }, 2000)
    }
    return () => clearInterval(interval)
  }, [runId, isLoading, data?.status])

  const handleRun = async () => {
    if (!repoUrl || !teamName || !leaderName) return;

    setIsLoading(true)
    setData(null)
    try {
      const res = await fetch('http://localhost:8000/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ repo_url: repoUrl, team_name: teamName, leader_name: leaderName })
      })
      const json = await res.json()
      setRunId(json.run_id)
      // Poll immediately once
      const res2 = await fetch(`http://localhost:8000/results/${json.run_id}`)
      if (res2.ok) setData(await res2.json())
    } catch (e) {
      setIsLoading(false)
      alert("Failed to start agent: " + e.message)
    }
  }

  return (
    <div className="min-h-screen bg-slate-900 text-white p-4 md:p-8">
      {/* Header */}
      <div className="max-w-7xl mx-auto mb-8 text-center">
        <h1 className="text-4xl md:text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500 mb-2">
          Autonomous DevOps Agent
        </h1>
        <p className="text-slate-400">Self-healing CI/CD Pipeline & Code Fixer</p>
      </div>

      {/* Input Section */}
      {!runId && (
        <div className="max-w-xl mx-auto card space-y-6">
          <div className="space-y-2">
            <label className="text-slate-300 text-sm font-medium">GitHub Repository URL</label>
            <input
              className="input-field"
              placeholder="https://github.com/user/repo"
              value={repoUrl}
              onChange={e => setRepoUrl(e.target.value)}
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-slate-300 text-sm font-medium">Team Name</label>
              <input
                className="input-field"
                placeholder="e.g. RIFT ORGANISERS"
                value={teamName}
                onChange={e => setTeamName(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <label className="text-slate-300 text-sm font-medium">Team Leader Name</label>
              <input
                className="input-field"
                placeholder="e.g. Saiyam Kumar"
                value={leaderName}
                onChange={e => setLeaderName(e.target.value)}
              />
            </div>
          </div>

          <button
            onClick={handleRun}
            disabled={!repoUrl || !teamName || !leaderName || isLoading}
            className="btn-primary w-full flex justify-center items-center"
          >
            {isLoading ? (
              <>
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Initializing Agent...
              </>
            ) : "Run Agent"}
          </button>
        </div>
      )}

      {/* Dashboard */}
      {data && (
        <Dashboard data={data} isLoading={isLoading} />
      )}
    </div>
  )
}

export default App
