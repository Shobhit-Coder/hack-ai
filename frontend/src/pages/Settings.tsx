import { useEffect, useState } from "react";
import { useAppStore } from "@/store/useAppStore";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "@/components/ui/select";
import { CheckCircle2, Pause } from "lucide-react";
import { toast } from "sonner";

export default function Settings(){
  const { settings, saveSettings, bootstrap } = useAppStore();
  const [form, setForm] = useState(settings);
  useEffect(()=>{ bootstrap(); }, []);
  useEffect(()=>{ setForm(settings); }, [settings]);

  if(!form) return null;

  return (
    <div className="space-y-6">
      <Card className="rounded-2xl">
        <CardHeader><CardTitle>Reminders</CardTitle></CardHeader>
        <CardContent className="grid md:grid-cols-3 gap-4">
          <div className="grid gap-2">
            <Label>Interval (minutes)</Label>
            <Select value={String(form.reminderIntervalMin)} onValueChange={(v)=> setForm({...form, reminderIntervalMin: Number(v)})}>
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                {[10,30,60].map(v => <SelectItem key={v} value={String(v)}>{v}</SelectItem>)}
              </SelectContent>
            </Select>
          </div>
          <div className="grid gap-2">
            <Label>Max reminders</Label>
            <Input value={form.maxReminders} onChange={(e)=> setForm({...form, maxReminders: Number(e.target.value)})} />
          </div>
          <div className="grid gap-2">
            <Label>Close after inactivity (min)</Label>
            <Input value={form.maxInactivityMinutes} onChange={(e)=> setForm({...form, maxInactivityMinutes: Number(e.target.value)})} />
          </div>
        </CardContent>
      </Card>

      <Card className="rounded-2xl">
        <CardHeader><CardTitle>Scoring Weights</CardTitle></CardHeader>
        <CardContent className="grid md:grid-cols-4 gap-4">
          <div className="grid gap-2"><Label>Skills</Label><Input value={form.scoringWeights.skills} onChange={(e)=> setForm({...form, scoringWeights:{...form.scoringWeights, skills: Number(e.target.value)}})} /></div>
          <div className="grid gap-2"><Label>Relevance</Label><Input value={form.scoringWeights.relevance} onChange={(e)=> setForm({...form, scoringWeights:{...form.scoringWeights, relevance: Number(e.target.value)}})} /></div>
          <div className="grid gap-2"><Label>Communication</Label><Input value={form.scoringWeights.communication} onChange={(e)=> setForm({...form, scoringWeights:{...form.scoringWeights, communication: Number(e.target.value)}})} /></div>
          <div className="grid gap-2"><Label>Completeness</Label><Input value={form.scoringWeights.completeness} onChange={(e)=> setForm({...form, scoringWeights:{...form.scoringWeights, completeness: Number(e.target.value)}})} /></div>
        </CardContent>
      </Card>

      <div className="flex gap-2">
        <Button onClick={async()=>{ await saveSettings(form); toast.success("Settings saved"); }} className="gap-2"><CheckCircle2 className="h-4 w-4"/> Save Settings</Button>
        <Button variant="outline" onClick={()=> setForm(settings!)} className="gap-2"><Pause className="h-4 w-4"/> Reset</Button>
      </div>
    </div>
  );
}
