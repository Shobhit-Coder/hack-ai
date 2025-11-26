import React from "react";
import ReactDOM from "react-dom/client";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import AppShell from "./shell/AppShell";
import Dashboard from "./pages/Dashboard";
import Jobs from "./pages/Jobs";
import Candidates from "./pages/Candidates";
import Interviews from "./pages/Interviews";
import Settings from "./pages/Settings";
import CandidateRouter from "./pages/candidate/CandidateRouter";
import PublicJobs from "./pages/public/Careers";
import PublicJobDetail from "./pages/public/JobDetail";
import "./index.css";
// import './styles/global.scss';
// import "./App.css"
import PublicLayout from "./pages/public/PublicLayout";
import InterviewDetail from "./pages/InterviewDetails";


const router = createBrowserRouter([
  {
    path: "/",
    element: <AppShell />,
    children: [
      { index: true, element: <Dashboard /> },
      { path: "jobs", element: <Jobs /> },
      { path: "candidates", element: <Candidates /> },
      { path: "interviews", element: <Interviews /> },
      { path: "interviews/:interviewId", element:<InterviewDetail />},
      // { path: "settings", element: <Settings /> },
    ],
  },
  {
    path: "/careers",
    element: <PublicLayout />,
    children: [
      { index: true, element: <PublicJobs /> },
      { path: ":jobId", element: <PublicJobDetail /> },
    ],
  },

  { path: "/candidate/:token", element: <CandidateRouter /> },
]);

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>
);
