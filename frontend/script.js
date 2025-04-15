
const apiUrl = "https://usdt-pof.onrender.com"; // Update to your actual Render backend URL
const debugMode = true; // Set to `true` to enable debug mode, `false` to disable it

// Debug function
function debugLog(message) {
  if (debugMode) {
    console.log(message);
  }
}

// DOM ready
document.addEventListener("DOMContentLoaded", () => {
  debugLog("DOM fully loaded.");

  // Wallet connect
  const connectBtn = document.getElementById("connectWalletBtn");
  if (connectBtn) {
    connectBtn.addEventListener("click", async () => {
      if (window.ethereum) {
        try {
          const accounts = await ethereum.request({ method: "eth_requestAccounts" });
          const walletAddress = accounts[0];
          sessionStorage.setItem("wallet", walletAddress);
          alert("Wallet connected: " + walletAddress);
          document.getElementById("walletStatus").textContent = "Wallet: " + walletAddress;
          debugLog("Wallet connected: " + walletAddress);
        } catch (error) {
          console.error("Wallet connection error:", error);
          debugLog("Wallet connection error: " + error.message);
        }
      } else {
        alert("MetaMask not detected. Please install MetaMask.");
        debugLog("MetaMask not detected.");
      }
    });
  } else {
    debugLog("Connect wallet button not found");
  }

  // Signup
  const signupForm = document.getElementById("signupForm");
  if (signupForm) {
    signupForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const email = signupForm.email.value;
      const password = signupForm.password.value;

      debugLog("Signup attempt with email: " + email);

      try {
        const res = await fetch(`${apiUrl}/signup`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password }),
        });

        if (res.ok) {
          alert("Signup submitted!");
          window.location.href = "dashboard.html";
          debugLog("Signup successful for: " + email);
        } else {
          const data = await res.json();
          alert("Error signing up: " + data.detail);
          debugLog("Signup failed: " + data.detail);
        }
      } catch (err) {
        console.error("Signup error:", err);
        alert("Error signing up");
        debugLog("Signup error: " + err.message);
      }
    });
  } else {
    debugLog("Signup form not found");
  }

  // Login
  const loginForm = document.getElementById("loginForm");
  if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const email = loginForm.email.value;
      const password = loginForm.password.value;

      debugLog("Login attempt with email: " + email);

      try {
        const res = await fetch(`${apiUrl}/login`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password }),
        });

        if (res.ok) {
          const data = await res.json();
          sessionStorage.setItem("token", data.token);
          sessionStorage.setItem("email", email);
          alert("Login submitted!");
          window.location.href = "dashboard.html";
          debugLog("Login successful for: " + email);
        } else {
          const data = await res.json();
          alert("Error logging in: " + data.detail);
          debugLog("Login failed: " + data.detail);
        }
      } catch (err) {
        console.error("Login error:", err);
        alert("Error logging in");
        debugLog("Login error: " + err.message);
      }
    });
  } else {
    debugLog("Login form not found");
  }

  // Dashboard
  if (window.location.pathname.includes("dashboard.html")) {
    const token = sessionStorage.getItem("token");
    if (!token) {
      window.location.href = "login.html";
      return;
    }

    const email = sessionStorage.getItem("email");
    const wallet = sessionStorage.getItem("wallet");

    document.getElementById("userEmail").textContent = email || "Not available";
    document.getElementById("walletStatus").textContent = wallet || "Wallet not connected";

    // Token balance (for now, just showing a fixed placeholder)
    document.getElementById("tokenBalance").textContent = "1000 POF";

    // Logout
    const logoutBtn = document.getElementById("logoutBtn");
    logoutBtn.addEventListener("click", () => {
      sessionStorage.clear();
      window.location.href = "login.html";
      debugLog("User logged out");
    });

    // Service Option A/B Buttons
    const optionA = document.getElementById("optionA");
    const optionB = document.getElementById("optionB");

    optionA.addEventListener("click", () => {
      alert("Option A Selected: 24h temporary transfer service");
      debugLog("Option A selected");
    });

    optionB.addEventListener("click", () => {
      alert("Option B Selected: Lifetime full token transfer");
      debugLog("Option B selected");
    });
  }
});
