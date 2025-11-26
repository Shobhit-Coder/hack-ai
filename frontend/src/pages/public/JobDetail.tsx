// src/public/PublicJobDetail.tsx
import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { publicApi } from "@/lib/Api";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";

export default function PublicJobDetail() {
  const { jobId } = useParams<{ jobId: string }>();
  const [job, setJob] = useState<any>();
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [file, setFile] = useState<File | null>(null);

  useEffect(() => { if (jobId) publicApi.getJob(jobId).then(setJob); }, [jobId]);

  async function onApply(e: React.FormEvent) {
    e.preventDefault();
    if (!jobId || !name || !phone || !file) { toast.error("Fill all fields & attach resume"); return; }
    await publicApi.applyForJob(jobId, { fullName: name, phoneE164: phone }, file);
    toast.success("Application received! We’ll contact you soon.");
    setName(""); setPhone(""); setFile(null);
  }

  if (!job) return <div>Loading…</div>;

  return (
    <div className="space-y-6">
      <div>
        <Link to="/jobs" className="text-sm underline">← Back to jobs</Link>
      </div>

      <div className="border rounded-2xl bg-white p-6 space-y-2">
        <h1 className="text-xl font-semibold">{job.title}</h1>
        <p className="text-gray-700 whitespace-pre-wrap">{job.descriptionText || "—"}</p>
      </div>

      <form onSubmit={onApply} className="border rounded-2xl bg-white p-6 grid gap-4">
        <h2 className="font-semibold">Apply for this job</h2>
        <Input placeholder="Full name" value={name} onChange={e=>setName(e.target.value)} />
        <Input placeholder="Phone (+E.164)" value={phone} onChange={e=>setPhone(e.target.value)} />
        <Input type="file" accept=".pdf,.doc,.docx" onChange={e=>setFile(e.target.files?.[0] ?? null)} />
        <div><Button type="submit">Submit Application</Button></div>
      </form>
    </div>
  );
}
