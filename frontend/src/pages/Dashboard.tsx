import StatCard from "@/components/StatCard";
import { MessageSquare, BarChart2, CheckCircle2, Clock } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as ChartTooltip,
  Tooltip,
  BarChart,
  Bar,
} from "recharts";
import { useEffect } from "react";
import { useAppStore } from "@/store/useAppStore";

// const trendData = [
//   { ts: "Nov 1", score: 68 },
//   { ts: "Nov 2", score: 72 },
//   { ts: "Nov 3", score: 76 },
//   { ts: "Nov 4", score: 74 },
//   { ts: "Nov 5", score: 79 },
// ];
// const scoreData = [
//   { name: "Skills", value: 32 },
//   { name: "Relevance", value: 26 },
//   { name: "Communication", value: 10 },
//   { name: "Completeness", value: 10 },
// ];

export default function Dashboard() {
  const { bootstrap, metrics, category, job_status } = useAppStore();
  console.log("matrics", metrics, category, job_status);
  // const {getAllInvites} = useAppStore();
  useEffect(() => {
    bootstrap();
  }, []);

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatCard
          title="Active Interviews"
          value={String(metrics?.active_interviews || 0)}
          icon={<MessageSquare className="h-4 w-4" />}
        />
        <StatCard
          title="Avg. Score (7d)"
          value={String(metrics?.average_score_7d || 0)}
          icon={<BarChart2 className="h-4 w-4" />}
        />
        <StatCard
          title="Completion Rate"
          value={`${String(metrics?.completion_rate || 0)}%`}
          icon={<CheckCircle2 className="h-4 w-4" />}
        />
        <StatCard
          title="Median Time"
          value={`${String(metrics?.median_time_minutes || 0)}m`}
          icon={<Clock className="h-4 w-4" />}
        />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">
        <Card className="rounded-2xl xl:col-span-4">
          <CardHeader>
            <CardTitle>Interview Score</CardTitle>
          </CardHeader>
          <CardContent className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={job_status}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="ts" />
                <YAxis domain={[0, 100]} />
                <ChartTooltip />
                <Line type="monotone" dataKey="score" />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card className="rounded-2xl xl:col-span-4">
          <CardHeader>
            <CardTitle>Job Openings Breakdown</CardTitle>
          </CardHeader>
          <CardContent className="overflow-y-auto">
            <ResponsiveContainer width="100%" height={category && category.length * 35}>
              <BarChart
                data={Array.isArray(category) ? category : []}
                layout="vertical"
                margin={{ left: 80 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis dataKey="name" type="category" width={150} />
                <Tooltip />
                <Bar dataKey="value" fill="#8884d8" barSize={20} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
