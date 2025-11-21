// src/public/PublicJobs.tsx
import { useEffect, useState } from "react";
import { adminApi } from "@/lib/fakeApi";
import { Link } from "react-router-dom";

export default function PublicJobs() {
  const [jobs, setJobs] = useState<any[]>([]);
  useEffect(() => { adminApi.listJobs().then(setJobs); }, []);
  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold">Open Positions</h1>
      <ul className="grid sm:grid-cols-2 gap-4">
        {jobs?.results?.map(j => (
          <li key={j.id} className="border rounded-2xl bg-white p-4 space-y-2">
            <div className="font-medium">{j.title}</div>
            <p className="text-sm text-gray-600 line-clamp-2">{j.descriptionText || "—"}</p>
            <Link className="text-sm underline" to={`/careers/${j.id}`}>View details</Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
