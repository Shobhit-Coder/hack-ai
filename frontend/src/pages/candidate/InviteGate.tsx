import { useCandidateStore } from "../../store/useCandidateStore";
import { Button } from "@/components/ui/button";
export default function InviteGate(){
  const { invite, start } = useCandidateStore();
  if(!invite) return null; const minutes = Math.floor(invite.timeLimitSec/60);
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 to-white">
      <div className="w-full max-w-lg p-6 rounded-2xl border bg-white shadow-sm space-y-4">
        <h1 className="text-2xl font-semibold">Interview</h1>
        <p className="text-sm text-gray-600">Time limit: <b>{minutes} minutes</b>. You’ll see a question at a time.</p>
        <Button className="w-full" onClick={()=> start(invite.token)}>Start Interview</Button>
        <p className="text-xs text-gray-500">By continuing you consent to your responses being recorded.</p>
      </div>
    </div>
  );
}
