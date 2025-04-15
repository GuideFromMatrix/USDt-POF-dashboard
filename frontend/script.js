
document.addEventListener("DOMContentLoaded", () => {
  const statusMessage = document.getElementById("status-message");

  async function checkStatus() {
    try {
      const response = await fetch("https://usdt-pof.onrender.com/test-status");
      if (!response.ok) throw new Error("Network response was not ok.");
      const data = await response.json();
      statusMessage.textContent = data.status;
      statusMessage.classList.add("success");
    } catch (error) {
      statusMessage.textContent = "Failed to connect to backend.";
      statusMessage.classList.add("error");
    }
  }

  checkStatus();
});
