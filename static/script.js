const textTab = document.getElementById("textTab");
const imageTab = document.getElementById("imageTab");
const textSection = document.getElementById("textSection");
const imageSection = document.getElementById("imageSection");

const statusBox = document.getElementById("status");
const verified = document.getElementById("verified");
const extracted = document.getElementById("extracted");
const toolResult = document.getElementById("toolResult");
const finalAnswer = document.getElementById("finalAnswer");
const explanation = document.getElementById("explanation");

textTab.addEventListener("click", () => {
  textTab.classList.add("active");
  imageTab.classList.remove("active");
  textSection.classList.remove("hidden");
  imageSection.classList.add("hidden");
});

imageTab.addEventListener("click", () => {
  imageTab.classList.add("active");
  textTab.classList.remove("active");
  imageSection.classList.remove("hidden");
  textSection.classList.add("hidden");
});

function showLoading(message) {
  statusBox.textContent = message;
  verified.textContent = "-";
  extracted.textContent = "-";
  toolResult.textContent = "-";
  finalAnswer.textContent = "Working...";
  explanation.textContent = "Please wait.";
}

function showResult(data) {
  statusBox.textContent = data.verified ? "Verification completed." : "Could not verify.";
  verified.textContent = String(data.verified);
  extracted.textContent = data.extracted_remaining_expression || "-";
  toolResult.textContent = data.tool_result || "-";
  finalAnswer.textContent = data.final_answer || "-";
  explanation.textContent = data.explanation || "-";
}

function showError(error) {
  statusBox.textContent = "Error";
  verified.textContent = "false";
  extracted.textContent = "-";
  toolResult.textContent = "-";
  finalAnswer.textContent = "-";

  if (typeof error === "string") {
    explanation.textContent = error;
  } else if (error && error.detail) {
    explanation.textContent =
      typeof error.detail === "string"
        ? error.detail
        : JSON.stringify(error.detail, null, 2);
  } else {
    explanation.textContent = JSON.stringify(error, null, 2);
  }
}

document.getElementById("verifyTextBtn").addEventListener("click", async () => {
  showLoading("Verifying typed work...");

  const payload = {
    problem_type: document.getElementById("problemType").value,
    original_expression: document.getElementById("originalExpression").value,
    partial_work: document.getElementById("partialWork").value,
    remaining_expression: document.getElementById("remainingExpression").value,
    variable: "x"
  };

  try {
    const response = await fetch("/verify-step", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });

    const data = await response.json();

    if (!response.ok) {
      throw data;
    }

    showResult(data);
  } catch (error) {
    showError(error.message);
  }
});

document.getElementById("verifyImageBtn").addEventListener("click", async () => {
  const file = document.getElementById("imageInput").files[0];

  if (!file) {
    showError("Please choose an image first.");
    return;
  }

  showLoading("Reading image and verifying work...");

  const formData = new FormData();
  formData.append("file", file);
  formData.append("problem_type", document.getElementById("imageProblemType").value);

  try {
    const response = await fetch("/verify-image", {
      method: "POST",
      body: formData
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Image request failed.");
    }

    showResult(data);
  } catch (error) {
    showError(error.message);
  }
});