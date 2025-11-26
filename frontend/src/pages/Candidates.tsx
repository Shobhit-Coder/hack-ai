import { useEffect, useState } from "react";
import { useAppStore } from "@/store/useAppStore";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Phone } from "lucide-react";
import { toast } from "sonner";
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "@/components/ui/select";
import TableSkeleton from "@/components/ui/table-skeleton";

export default function Candidates(){
  const { candidates, addCandidate, getCandidates, jobs, getJob, loading } = useAppStore();
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [page, setPage] = useState(1);
  const [email, setEmail] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [jobId, setJobId] = useState<string>("");
  const pageSize = 10;
  const total = candidates?.count ?? 0;
  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  useEffect(() => {
      console.log("current page", page)
      getCandidates(page, pageSize);
      getJob(1, 100);
  }, [page]);

  const emailIsValid = (v: string) => /^\S+@\S+\.\S+$/.test(v);
  const phoneIsValid = (v: string) => /^\+?\d{7,15}$/.test(v); 
  async function onSave() {
    if(!jobId.trim()) return toast.error("Select job");
    // if (!name.trim()) return toast.error("Enter name");
    // if (!phone.trim()) return toast.error("Enter phone");
    // if (!phoneIsValid(phone.trim())) return toast.error("Phone looks invalid. Use digits with optional +");
    // if (email.trim() && !emailIsValid(email.trim())) return toast.error("Email looks invalid");
    if (!file) return toast.error("Upload resume file (PDF / DOCX)");

    try {
      await addCandidate(jobId.trim(), file);
      setName(""); setPhone(""); setEmail(""); setFile(null);
      setJobId("");
      toast.success("Candidate saved");
      setPage(1);
      getCandidates(1, pageSize);
    } catch (err: any) {
      console.error("save candidate failed", err);
      // server-side field errors often in err.response.data
      const data = err?.response?.data;
      if (data) {
        // if backend returns e.g. { email: ["Invalid"] } or { detail: "..." }
        if (typeof data === "string") toast.error(data);
        else if (data.detail) toast.error(data.detail);
        else {
          // join field errors
          const messages = Object.entries(data)
            .flatMap(([k, v]: any) => (Array.isArray(v) ? v : [v]))
            .join(" ");
          toast.error(messages || "Failed to save candidate");
        }
      } else {
        toast.error(err?.message || "Failed to save candidate");
      }
    }
  }

  return (
    <div className="space-y-6">
      <Card className="rounded-2xl">
        <CardHeader><CardTitle>Add Candidate</CardTitle></CardHeader>
        <CardContent className="grid md:grid-cols-2 gap-4">
          <div className="grid gap-2">
            <label>Job</label>
            <Select value={jobId} onValueChange={setJobId}>
              <SelectTrigger className="w-full"><SelectValue placeholder="Select job"/></SelectTrigger>
              <SelectContent>
                {console.log("jobs in candidate page", jobs)}
                {jobs?.results?.map(j=> <SelectItem key={j.id} value={j.id}>{`${j.title} - ${j.company_name}`}</SelectItem>)}
              </SelectContent>
            </Select>
          </div>
          <div className="grid gap-2">
            <label>Upload Resume</label>
            <input
              type="file"
              accept=".pdf,.doc,.docx"
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
              className="block w-full"
            />
          </div>
          
          <div className="md:col-span-2 mt-4">
            <Button onClick={onSave}>Apply For Job</Button>
          </div>
        </CardContent>
      </Card>

      <Card className="rounded-2xl">
        <CardHeader><CardTitle>All Candidates</CardTitle></CardHeader>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-gray-500">
                  <th className="py-2 pl-4">Name</th>
                  <th>Phone</th>
                  <th>Email</th>
                </tr>
              </thead>
              <tbody>
                {loading && <TableSkeleton rows={10} columns={3} />}
                {!loading && candidates && candidates?.results?.map((c)=> (
                  <tr key={c.id} className="border-t">
                    <td className="py-3 pl-4">{c.first_name + ' ' + c.last_name}</td>
                    <td>{c.phone_number}</td>
                    <td>{c.email}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {/* Pagination controls */}
          {!loading && <div className="flex items-center justify-between p-4">
            <div className="text-sm text-gray-600">
              Showing {(candidates?.results?.length ?? 0)} of {total} candidates
            </div>

            <div className="flex items-center gap-2">
              <button
                className="px-3 py-1 cursor-pointer rounded-lg border"
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page <= 1}
              >
                Prev
              </button>

              {/* simple page numbers: show up to 5 pages centered around current */}
              <div className="flex items-center gap-1">
                {Array.from({ length: totalPages }).map((_, i) => {
                  const p = i + 1;
                  // optionally limit large lists to a window:
                  if (totalPages > 7) {
                    if (
                      p !== 1 &&
                      p !== totalPages &&
                      Math.abs(p - page) > 2
                    ) {
                      // show ellipses only once; simple approach: skip rendering
                      // we will render first, last and a sliding window around current
                      return null;
                    }
                  }
                  return (
                    <button
                      key={p}
                      onClick={() => setPage(p)}
                      className={`px-2 py-1 cursor-pointer rounded ${p === page ? "font-semibold" : "text-sm"}`}
                    >
                      {p}
                    </button>
                  );
                })}
                {totalPages > 7 && page < totalPages - 3 && (
                  <span className="px-2">…</span>
                )}
              </div>

              <button
                className="px-3 py-1 cursor-pointer rounded-lg border"
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page >= totalPages}
              >
                Next
              </button>
            </div>
          </div>}
        </CardContent>
      </Card>
    </div>
  );
}
