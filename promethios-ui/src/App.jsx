import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Splash from "./Splash";
import ControlRoom from "./ControlRoom";

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Splash />} />
        <Route path="/dashboard" element={<ControlRoom />} />
      </Routes>
    </Router>
  );
}
