// File: src/Splash.jsx
import "./Splash.css";
import logo from "../public/logo.png";

function Splash() {
  return (
    <div className="splash-container">
      <div className="left-panel">
        <img src={logo} alt="Promethios Logo" className="logo" />
        <h1 className="title">Promethios Operator Dashboard</h1>
        <p className="slogan">The fire has been lit. Operator input required.</p>

        <form className="login-form">
          <input type="text" placeholder="Username" />
          <input type="password" placeholder="Password" />
          <input type="text" placeholder="Override (e.g. I AM PROMETHEOS)" />
          <button type="submit">Access</button>
        </form>

        <p className="footer">🔥 The fire is lit</p>
      </div>

      <div className="right-panel">
        {/* Right panel is intentionally blank for now, enhancements later */}
      </div>
    </div>
  );
}

export default Splash;
