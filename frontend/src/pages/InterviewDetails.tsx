import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "@/lib/apiClient";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Loader2Icon,
} from "lucide-react"
import { useAppStore } from "@/store/useAppStore";

type InterviewResponse = {
  interview: {
    id: string;
    candidate_name: string;
    job_category: string;
    created_at: string;
    modified_at: string;
    scheduled_at?: string | null;
    started_at?: string | null;
    ended_at?: string | null;
    job_fit_score?: number | null;
    status?: string | null;
    candidate?: string | null;
    job?: string | null;
  };
  messages: Array<{
    message_id: string;
    created_at: string;
    direction: "inbound" | "outbound" | string;
    message_text: string;
    status?: string;
    related_question?: string | null;
  }>;
};

export default function InterviewDetailPage() {
  const { interviewId } = useParams<{ id: string }>(); // route must be /interviews/:id
//   const interviewId = id;
  const [data, setData] = useState<InterviewResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const {getInterviewDetails, interviewDetails} = useAppStore();
  useEffect(() => {
    if (!interviewId) return;
    // fetchInterview(interviewId);
    getInterviewDetails(interviewId);
  }, [interviewId]);

  // async function fetchInterview(interviewId: string) {
  //   setLoading(true);
  //   setError(null);
  //   try {
  //     const res = await api.get(`/interviews/${interviewId}`);
  //     setData(res.data as InterviewResponse);
  //   } catch (err: any) {
  //     console.error("Failed to fetch interview", err);
  //     setError(err?.response?.data?.detail || err.message || "Failed to load");
  //   } finally {
  //     setLoading(false);
  //   }
  // }
  useEffect(() => {
    console.log("interview details", interviewDetails)
    setData(interviewDetails);
  }, [interviewDetails])

  function fmt(dt?: string | null) {
    if (!dt) return "—";
    try {
      return new Date(dt).toLocaleString();
    } catch {
      return dt;
    }
  }

  // Example screenshot path you provided (system will transform path into a URL)
  const SCREENSHOT = "/mnt/data/Screenshot from 2025-11-19 16-53-21.png";

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Interview Details</h1>
          <p className="text-sm text-gray-500">Metadata and message transcript (read-only)</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* LEFT: Interview card (takes 5/12 on large screens) */}
        <div className="lg:col-span-5">
          <Card className="h-full">
            <CardHeader>
              <CardTitle>Interview</CardTitle>
            </CardHeader>
            <CardContent>
              {/* {loading && <div className="p-6 text-center">Loading…</div>} */}
              {loading && <Loader2Icon className="size-4 animate-spin" />}
              {error && <div className="p-4 text-red-600">{error}</div>}

              {!loading && !error && data && (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="text-sm text-gray-500">Candidate</div>
                      <div className="text-lg font-medium">{data.interview.candidate_name}</div>
                    </div>
                    <Badge className="uppercase">{data.interview.status ?? "unknown"}</Badge>
                  </div>

                  <div className="grid grid-cols-2 gap-3 text-sm">
                    <div className="space-y-1">
                      <div className="text-gray-500">Job</div>
                      <div>{data.interview.job_category}</div>
                    </div>
                    <div className="space-y-1">
                      <div className="text-gray-500">Job fit</div>
                      <div>{data.interview.job_fit_score ?? "—"}</div>
                    </div>

                    <div className="space-y-1">
                      <div className="text-gray-500">Scheduled</div>
                      <div>{fmt(data.interview.scheduled_at)}</div>
                    </div>
                    <div className="space-y-1">
                      <div className="text-gray-500">Started</div>
                      <div>{fmt(data.interview.started_at)}</div>
                    </div>

                    <div className="space-y-1">
                      <div className="text-gray-500">Ended</div>
                      <div>{fmt(data.interview.ended_at)}</div>
                    </div>
                    <div className="space-y-1">
                      <div className="text-gray-500">Created</div>
                      <div>{fmt(data.interview.created_at)}</div>
                    </div>

                    <div className="col-span-2 pt-2">
                      <div className="text-gray-500 text-sm">Modified</div>
                      <div>{fmt(data.interview.modified_at)}</div>
                    </div>
                  </div>

                  {/* optional: small actions area */}
                  <div className="mt-4 flex gap-2">
                    {/* <button
                      className="px-3 py-2 rounded-md border text-sm bg-white hover:bg-gray-50"
                      onClick={() => window.print()}
                    >
                      Print
                    </button>
                    <a
                      href={SCREENSHOT}
                      target="_blank"
                      rel="noreferrer"
                      className="px-3 py-2 rounded-md border text-sm bg-white hover:bg-gray-50"
                    >
                      View Screenshot
                    </a> */}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* RIGHT: Messages card (takes 7/12 on large screens) */}
        <div className="lg:col-span-7">
          <Card className="h-full">
            <CardHeader>
              <CardTitle>Messages</CardTitle>
            </CardHeader>
            <CardContent className="flex flex-col p-0">
              {loading && <div className="p-6 text-center">Loading messages…</div>}
              {!loading && !error && data && (
                <div className="flex-1 p-4">
                  <div className="h-[520px] overflow-y-auto space-y-4 pr-2">
                    {data.messages.length === 0 && (
                      <div className="text-sm text-gray-500">No messages</div>
                    )}

                    {data.messages.map((m) => {
                      const inbound = m.direction === "inbound";
                      return (
                        <div key={m.message_id} className={`flex ${inbound ? "justify-start" : "justify-end"}`}>
                          <div
                            className={`max-w-[80%] p-3 rounded-lg shadow-sm ${inbound ? "bg-gray-100 text-gray-900" : "bg-primary text-white"}`}
                          >
                            <div className="text-sm whitespace-pre-wrap">{m.message_text}</div>
                            <div className="mt-2 text-[11px] text-gray-400">{new Date(m.created_at).toLocaleString()}</div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* fallback when no data */}
              {!data && !loading && !error && (
                <div className="p-6 text-gray-500">No interview selected.</div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
