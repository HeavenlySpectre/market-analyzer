import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import DashboardPage from "./pages/DashboardPage";

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-background dark">
        <Routes>
          <Route path="/" element={<DashboardPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
