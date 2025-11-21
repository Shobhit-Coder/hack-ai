import { useEffect, useState } from "react";
import { useAppStore } from "@/store/useAppStore";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Plus } from "lucide-react";
import { toast } from "sonner";
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "@/components/ui/select";
import { JOB_CATEGORIES } from "@/constants";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import TableSkeleton from "@/components/ui/table-skeleton";

export default function Jobs() {
  const { jobs, addJob, getJob, loading } = useAppStore();
  const [open, setOpen] = useState(false);
  const [title, setTitle] = useState("");
  const [desc, setDesc] = useState("");
  const [category, setCategory] = useState("");
  const [companyName, setCompanyName] = useState("");
  const [location, setLocation] = useState("");
  const [isRemote, setIsRemote] = useState(false);
  const [applicationDeadline, setApplicationDeadline] = useState(""); // yyyy-mm-dd or ISO
  const [jobStatus, setJobStatus] = useState("open");

  const [page, setPage] = useState(1);
  const pageSize = 10;

  useEffect(() => {
    getJob(page, pageSize);
  }, [page]);

  function validateForm() {
    if (!title.trim()) {
      toast.error("Title is required");
      return false;
    }
    if (!companyName.trim()) {
      toast.error("Company name is required");
      return false;
    }
    // optional: check date validity if provided
    // if (applicationDeadline) {
    //   // simple YYYY-MM-DD check
    //   const valid = /^\d{4}-\d{2}-\d{2}$/.test(applicationDeadline);
    //   if (!valid) {
    //     toast.error("Application deadline should be YYYY-MM-DD");
    //     return false;
    //   }
    // }
    return true;
  }

  async function onSave() {
    if (!validateForm()) return;
    const payload = {
      title: title.trim(),
      descriptionText: desc.trim(),
      category: category.trim(),
      company_name: companyName.trim(),
      location: location.trim(),
      is_remote: isRemote,
      // send ISO date-time if you want hours: use new Date(...).toISOString()
      application_deadline: applicationDeadline ? new Date(applicationDeadline).toISOString() : null,
      // job_status: jobStatus,
    };

    try {

      await addJob(payload);
      toast.success("Job created");
      setOpen(false);
      setTitle("");
      setDesc("");
      setCategory("");
      setCompanyName("");
      setLocation("");
      setIsRemote(false);
      setApplicationDeadline("");
      setJobStatus("open");
      // reload first page so new job is visible
      setPage(1);
      getJob(1, pageSize);
    } catch (err: any) {
      console.error("create job failed", err);
      const msg = err?.response?.data?.detail || err?.message || "Failed to create job";
      toast.error(msg);
    }
  }

  const total = jobs?.count ?? 0;
  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Jobs</h2>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button className="gap-2"><Plus className="h-4 w-4"/> New Job</Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-xl">
            <DialogHeader><DialogTitle>Create Job Posting</DialogTitle></DialogHeader>

            <div className="grid gap-4">
              <div className="grid gap-2">
                <Input
                  placeholder="e.g., Backend Engineer"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                />
              </div>

              <div className="grid gap-2">
                <Input
                  placeholder="Company name"
                  value={companyName}
                  onChange={(e) => setCompanyName(e.target.value)}
                />
              </div>

              <div className="grid gap-2">
                <Select value={category} onValueChange={setCategory} >
                  <SelectTrigger className="w-full"><SelectValue placeholder="Select Category"/></SelectTrigger>
                  <SelectContent>
                    {JOB_CATEGORIES.map(j=> <SelectItem key={j} value={j}>{j}</SelectItem>)}
                  </SelectContent>
                </Select>
                {/* <Select
                  placeholder="Category"
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                /> */}
              </div>

              <div className="grid gap-2">
                <Input
                  placeholder="Location"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                />
              </div>

              <div className="grid gap-2">
                <Textarea
                  rows={10}
                  placeholder="Paste JD here…"
                  value={desc}
                  onChange={(e) => setDesc(e.target.value)}
                />
              </div>
              <div className="grid gap-2">
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={isRemote}
                    onChange={(e) => setIsRemote(e.target.checked)}
                    className="form-checkbox"
                  />
                  <span>Is remote</span>
                </label>
              </div>
              <div>
                <label className="flex flex-col text-sm">
                  <span className="text-xs text-gray-500">Application deadline</span>
                  <DatePicker
                    selected={applicationDeadline}
                    onChange={(d) => setApplicationDeadline(d)}
                    placeholderText="dd/mm/yyyy"
                    className="border border-muted/40 rounded px-2 py-1 w-full h-9 rounded-md"
                  />
                </label>
              </div>

              <div className="flex items-center gap-4">
                {/* <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={isRemote}
                    onChange={(e) => setIsRemote(e.target.checked)}
                    className="form-checkbox"
                  />
                  <span>Is remote</span>
                </label>

                <label className="flex flex-col text-sm">
                  <span className="text-xs text-gray-500">Application deadline</span>
                  <input
                    type="date"
                    value={applicationDeadline}
                    onChange={(e) => setApplicationDeadline(e.target.value)}
                    className="border rounded px-2 py-1"
                  />
                </label> */}

                {/* <label className="flex flex-col text-sm">
                  <span className="text-xs text-gray-500">Job status</span>
                  <select
                    value={jobStatus}
                    onChange={(e) => setJobStatus(e.target.value)}
                    className="border rounded px-2 py-1"
                  >
                    <option>Open</option>
                    <option>Paused</option>
                    <option>Closed</option>
                  </select>
                </label> */}
              </div>
            </div>

            <DialogFooter>
              <Button onClick={onSave}>Save</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      <Card className="rounded-2xl">
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-gray-500">
                  <th className="py-2 pl-4">Title</th>
                  <th className="py-2 pl-4">Company Name</th>
                  <th className="py-2 pl-4">Location</th>
                  <th className="py-2 pl-4">Category</th>
                  <th className="py-2 pl-4">Remote</th>
                  <th>Created</th>
                </tr>
              </thead>
              <tbody>
                {loading && <TableSkeleton rows={10} columns={6} />}
                {!loading && jobs?.results?.map((j: any) => (
                  <tr key={j.id} className="border-t">
                    <td className="py-3 pl-4">{j.title}</td>
                    <td className="py-3 pl-4">{j.company_name}</td>
                    <td className="py-3 pl-4">{j.location}</td>
                    <td className="py-3 pl-4">{j.category}</td>
                    <td className="py-3 pl-4">{j.is_remote ? "Yes" : "No"}</td>
                    <td>{new Date(j.created_at ?? j.createdAt).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination controls */}
          {!loading && <div className="flex items-center justify-between p-4">
            <div className="text-sm text-gray-600">
              Showing {(jobs?.results?.length ?? 0)} of {total} jobs
            </div>

            <div className="flex items-center gap-2">
              <button
                className="px-3 py-1 cursor-pointer rounded-lg border"
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page <= 1}
              >
                Prev
              </button>

              <div className="flex items-center gap-1">
                {Array.from({ length: totalPages }).map((_, i) => {
                  const pNum = i + 1;
                  if (totalPages > 7) {
                    if (pNum !== 1 && pNum !== totalPages && Math.abs(pNum - page) > 2) {
                      return null;
                    }
                  }
                  return (
                    <button
                      key={pNum}
                      onClick={() => setPage(pNum)}
                      className={`px-2 py-1 cursor-pointer rounded ${pNum === page ? "font-semibold" : "text-sm"}`}
                    >
                      {pNum}
                    </button>
                  );
                })}
                {totalPages > 7 && page < totalPages - 3 && <span className="px-2">…</span>}
              </div>

              <button
                className="px-3 py-1 cursor-pointer rounded-lg border"
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page >= totalPages}
              >
                Next
              </button>
            </div>
          </div> }
        </CardContent>
      </Card>
    </div>
  );
}
