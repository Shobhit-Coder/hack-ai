import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
export default function StatCard({ title, value, icon }:{ title:string; value:string; icon?:React.ReactNode }){
  return (
    <Card className="rounded-2xl">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium text-gray-500">{title}</CardTitle>
        {icon}
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-semibold">{value}</div>
      </CardContent>
    </Card>
  );
}
