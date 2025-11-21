import { useEffect, useState } from "react";
import { useAppStore } from "@/store/useAppStore";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Select,
  SelectTrigger,
  SelectValue,
  SelectContent,
  SelectItem,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Play, Link as LinkIcon, Copy, Eye, Loader2Icon } from "lucide-react";
import { toast } from "sonner";
import { useNavigate } from "react-router-dom";
import TableSkeleton from "@/components/ui/table-skeleton";

const INTERVIEWsTATUS = {
  scheduled: "Scheduled",
  in_progress: "In Progress",
  completed: "Completed",
  canceled: "Canceled",
};
const statusColor: Record<string, string> = {
  scheduled: "bg-slate-100 text-slate-700",
  in_progress: "bg-blue-100 text-blue-700",
  completed: "bg-emerald-100 text-emerald-700",
  canceled: "bg-amber-100 text-amber-700",
};

export default function Interviews() {
  const {
    interviews,
    jobs,
    candidates,
    getInterview,
    startInterview,
    getJob,
    getCandidates,
    loading,
    issueInvite,
  } = useAppStore();
  const [open, setOpen] = useState(false);
  const [jobId, setJobId] = useState<string>("");
  const [candidateId, setCandidateId] = useState<string>("");
  const [page, setPage] = useState(1);
  const pageSize = 10;
  const total = interviews?.count ?? 0;
  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  const [inviteOpen, setInviteOpen] = useState(false);
  const [inviteFor, setInviteFor] = useState<string | null>(null);
  const [minutes, setMinutes] = useState<number>(15);
  const [inviteUrl, setInviteUrl] = useState<string>("");
  const navigate = useNavigate();

  useEffect(() => {
    getInterview(page, pageSize);
    getJob();
    getCandidates();
  }, [page]);

  async function onStart() {
    if (!jobId || !candidateId) return;
    await startInterview(jobId, candidateId);
    setOpen(false);
  }

  async function onIssueInvite(interviewId: string) {
    try {
      issueInvite(interviewId);
    } catch (e: any) {
      toast.error(e.message ?? "Failed to issue invite");
    }
  }

  return (
    <>
      {/* <PageSpinner show={loading} /> */}

      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">Interviews</h2>
          <Dialog open={open} onOpenChange={setOpen}>
            {/* <DialogTrigger asChild>
            <Button className="gap-2"><Play className="h-4 w-4"/> Start Interview</Button>
          </DialogTrigger> */}
            <DialogContent className="sm:max-w-xl">
              <DialogHeader>
                <DialogTitle>Start Interview</DialogTitle>
              </DialogHeader>
              <div className="grid gap-4">
                <div className="grid gap-2">
                  <label>Job</label>
                  <Select value={jobId} onValueChange={setJobId}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select job" />
                    </SelectTrigger>
                    <SelectContent>
                      {jobs?.results?.map((j) => (
                        <SelectItem key={j.id} value={j.id}>
                          {j.title}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="grid gap-2">
                  <label>Candidate</label>
                  <Select value={candidateId} onValueChange={setCandidateId}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select candidate" />
                    </SelectTrigger>
                    <SelectContent>
                      {candidates?.results?.map((c) => (
                        <SelectItem key={c.id} value={c.id}>
                          {c.fullName}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <Button onClick={onStart}>Start</Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>

        <Card className="rounded-2xl">
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-gray-500">
                    {/* <th className="py-2 pl-4">Interview ID</th> */}
                    <th className="py-2 pl-4">Candidate</th>
                    <th>Job</th>
                    <th>Status</th>
                    <th>Scheduled At</th>
                    <th className="pr-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {loading && <TableSkeleton rows={10} columns={5} />}
                  {!loading &&
                    interviews &&
                    interviews?.results?.map((row) => (
                      <tr key={row.id} className="border-t">
                        {/* <td className="py-3 pl-4">{row.id.slice(0,8)}…</td> */}
                        <td className="py-3 pl-4">{row?.candidate_name}</td>
                        <td>{row?.job_category}</td>
                        <td>
                          <span
                            className={`px-2 py-1 rounded-full text-xs ${
                              statusColor[row.status]
                            }`}
                          >
                            {INTERVIEWsTATUS[row.status]}
                          </span>
                        </td>
                        <td>{new Date(row.scheduled_at).toLocaleString()}</td>
                        <td className="pr-4 text-right">
                          <Button
                            variant="outline"
                            size="sm"
                            className="gap-2"
                            onClick={() => onIssueInvite(row.id)}
                            disabled={["completed", "complete"].includes(
                              row.status
                            )}
                            aria-disabled={["completed", "complete"].includes(
                              row.status
                            )}
                          >
                            <LinkIcon className="h-4 w-4" /> Invite
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            className="ml-2 gap-2 cursor-pointer"
                            onClick={() => navigate(`/interviews/${row.id}`)}
                            disabled={
                              !["completed", "complete"].includes(row.status)
                            }
                            aria-disabled={
                              !["completed", "complete"].includes(row.status)
                            }
                            title={
                              !["completed", "complete"].includes(row.status)
                                ? "Details available after interview completes"
                                : "View details"
                            }
                          >
                            <Eye className="h-4 w-4" />
                          </Button>
                        </td>
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>
            {/* Pagination controls */}
            {!loading && (
              <div className="flex items-center justify-between p-4">
                <div className="text-sm text-gray-600">
                  Showing {interviews?.results?.length ?? 0} of {total}{" "}
                  Interviews
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
                      const p = i + 1;
                      if (totalPages > 7) {
                        if (
                          p !== 1 &&
                          p !== totalPages &&
                          Math.abs(p - page) > 2
                        ) {
                          return null;
                        }
                      }
                      return (
                        <button
                          key={p}
                          onClick={() => setPage(p)}
                          className={`px-2 py-1 cursor-pointer rounded ${
                            p === page ? "font-semibold" : "text-sm"
                          }`}
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
              </div>
            )}
          </CardContent>
        </Card>

        {/* Invite dialog */}
        <Dialog open={inviteOpen} onOpenChange={setInviteOpen}>
          <DialogContent className="sm:max-w-lg">
            <DialogHeader>
              <DialogTitle>Share Interview Link</DialogTitle>
            </DialogHeader>
            <div className="grid gap-3">
              <label className="text-sm">Time limit (minutes)</label>
              <Input
                type="number"
                value={minutes}
                onChange={(e) => setMinutes(Number(e.target.value || 15))}
              />
              <label className="text-sm">Link</label>
              <div className="flex gap-2">
                <Input readOnly value={inviteUrl} />
                <Button
                  type="button"
                  variant="outline"
                  className="gap-2"
                  onClick={() => {
                    navigator.clipboard.writeText(inviteUrl);
                    toast.success("Link copied");
                  }}
                >
                  <Copy className="h-4 w-4" /> Copy
                </Button>
              </div>
              <p className="text-xs text-gray-500">
                Send this link via SMS or email. The candidate must open it to
                start their timer.
              </p>
            </div>
            <DialogFooter>
              <Button onClick={() => setInviteOpen(false)}>Done</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </>
  );
}
