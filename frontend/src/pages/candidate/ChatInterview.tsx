import { useCandidateStore } from "../../store/useCandidateStore";
import ChatBubble from "../../components/chat/ChatBubble";
import { useEffect, useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";


function useCountdown(endsAt?: string) {
  const [left, setLeft] = useState<number>(() =>
    endsAt
      ? Math.max(
          0,
          Math.floor((new Date(endsAt).getTime() - Date.now()) / 1000)
        )
      : 0
  );
  useEffect(() => {
    if (!endsAt) return;
    const id = setInterval(() => {
      setLeft(
        Math.max(
          0,
          Math.floor((new Date(endsAt).getTime() - Date.now()) / 1000)
        )
      );
    }, 1000);
    return () => clearInterval(id);
  }, [endsAt]);
  const mm = String(Math.floor(left / 60)).padStart(2, "0");
  const ss = String(left % 60).padStart(2, "0");
  return { left, label: `${mm}:${ss}` };
}


export default function ChatInterview() {
  const { invite, send, refreshTranscript } = useCandidateStore();
  const [text, setText] = useState("");
  const scroller = useRef<HTMLDivElement>(null);
  const { left, label } = useCountdown(invite?.endsAt);
  useEffect(() => {
    const id = setInterval(() => {
      if (invite) refreshTranscript(invite.token);
    }, 5000);
    return () => clearInterval(id);
  }, [invite?.token]);
  useEffect(() => {
    scroller.current?.scrollTo({
      top: scroller.current.scrollHeight,
      behavior: "smooth",
    });
  }, [invite?.transcript]);
  if (!invite) return null;
  const disabled = left === 0;
  return (
    <div className="min-h-screen flex flex-col">
      <header className="h-14 border-b flex items-center justify-between px-4 bg-white">
        <div className="font-semibold">Interview</div>
        <div
          className={`text-sm font-medium ${
            left < 60 ? "text-red-600" : "text-gray-700"
          }`}
        >
          Time left: {label}
        </div>
      </header>
      <main className="flex-1 max-w-3xl w-full mx-auto p-4 gap-4 flex flex-col">
        <div
          ref={scroller}
          className="flex-1 overflow-auto space-y-2 p-2 bg-white rounded-2xl border"
        >
          {invite.transcript.map((m, i) => (
            <ChatBubble key={i} role={m.role as any} text={m.text} />
          ))}
          {left === 0 && (
            <div className="text-center text-sm text-red-600">
              Time is up. Your last answer has been saved.
            </div>
          )}
        </div>
        <form
          className="flex gap-2"
          onSubmit={(e) => {
            e.preventDefault();
            if (!text.trim()) return;
            send(invite.token, text.trim());
            setText("");
          }}
        >
          <Input
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Type your answer..."
            disabled={disabled}
          />
          <Button type="submit" disabled={disabled}>
            Send
          </Button>
        </form>
      </main>
    </div>
  );
}
