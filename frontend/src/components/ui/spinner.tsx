import { Loader2 } from "lucide-react";

interface PageSpinnerProps {
  show: boolean;
  text?: string;
}

export default function PageSpinner({ show, text = "Loading..." }: PageSpinnerProps) {
  if (!show) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30">
      <div className="rounded-lg bg-white/90 px-6 py-4 shadow-lg flex items-center gap-3">
        <Loader2 className="h-6 w-6 animate-spin" />
        <span className="text-sm font-medium">{text}</span>
      </div>
    </div>
  );
}
