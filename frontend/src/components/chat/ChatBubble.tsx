export default function ChatBubble({
  role,
  text,
}: {
  role: "bot" | "candidate" | "system";
  text: string;
}) {
  const isMe = role === "candidate";
  const bg =
    role === "system" ? "bg-amber-50" : isMe ? "bg-blue-50" : "bg-gray-100";
  const align = isMe ? "justify-end" : "justify-start";
  return (
    <div className={`flex ${align}`}>
      <div className={`max-w-[80%] ${bg} rounded-2xl px-4 py-2 text-sm`}>
        {text}
      </div>
    </div>
  );
}
