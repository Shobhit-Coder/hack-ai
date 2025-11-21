export async function fetchDashboard() {
  const res = await fetch(
    "https://4db7912fce77.ngrok-free.app/api/dashboard"
  );

  if (!res.ok) throw new Error("Failed to load dashboard");
  return res.json();
}
