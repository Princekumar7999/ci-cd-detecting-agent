import SummaryCard from './SummaryCard'
import ScoreBreakdown from './ScoreBreakdown'
import FixesTable from './FixesTable'
import Timeline from './Timeline'

export default function Dashboard({ data }) {
    return (
        <div className="space-y-6 animate-fade-in">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <SummaryCard data={data} />
                <ScoreBreakdown data={data} />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2">
                    <FixesTable data={data} />
                </div>
                <div>
                    <Timeline data={data} />
                </div>
            </div>
        </div>
    )
}
