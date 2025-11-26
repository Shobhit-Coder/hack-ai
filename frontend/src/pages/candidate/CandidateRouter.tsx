import { useParams } from "react-router-dom";
import InviteGate from "./InviteGate";
import ChatInterview from "./ChatInterview";
import { useCandidateStore } from "../../store/useCandidateStore";
import { useEffect } from "react";
export default function CandidateRouter() {
  const { token } = useParams<{ token: string }>();
  const { invite, fetchInvite } = useCandidateStore();
  useEffect(() => {
    if (token) fetchInvite(token);
  }, [token]);
  if (!invite) return <div className="p-6">Loading…</div>;
  if (!invite.acceptedAt) return <InviteGate />;
  return <ChatInterview />;
}
