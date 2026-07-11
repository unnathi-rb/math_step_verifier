const textTab = document.getElementById("textTab");
const imageTab = document.getElementById("imageTab");
const textSection = document.getElementById("textSection");
const imageSection = document.getElementById("imageSection");

const statusPill = document.getElementById("statusPill");
const verified = document.getElementById("verified");
const extracted = document.getElementById("extracted");
const toolResult = document.getElementById("toolResult");
const finalAnswer = document.getElementById("finalAnswer");
const explanation = document.getElementById("explanation");

const imageInput = document.getElementById("imageInput");
const fileName = document.getElementById("fileName");
const toggleStepsBtn = document.getElementById("toggleStepsBtn");
const stepsBox = document.getElementById("stepsBox");
const stepsList = document.getElementById("stepsList");

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

imageInput.addEventListener("change", () => {
  const file = imageInput.files[0];
  fileName.textContent = file ? file.name : "No file selected";
});

toggleStepsBtn.addEventListener("click", () => {
  stepsBox.classList.toggle("hidden");
  toggleStepsBtn.textContent = stepsBox.classList.contains("hidden")
    ? "Show detailed steps"
    : "Hide detailed steps";
});

function setStatus(text, state) {
  statusPill.textContent = text;
  statusPill.className = `status-pill ${state}`;
}

function resetSteps() {
  stepsList.innerHTML = "";
  stepsBox.classList.add("hidden");
  toggleStepsBtn.classList.add("hidden");
  toggleStepsBtn.textContent = "Show detailed steps";
}

function showLoading(message) {
  setStatus(message, "loading");
  verified.textContent = "-";
  extracted.textContent = "-";
  toolResult.textContent = "-";
  finalAnswer.textContent = "Working...";
  explanation.textContent = "Please wait while NextStep verifies the expression.";
  resetSteps();
}

function showResult(data) {
  setStatus(data.verified ? "Solved" : "Needs review", data.verified ? "success" : "error");

  verified.textContent = String(data.verified);
  extracted.textContent = data.extracted_remaining_expression || "-";
  toolResult.textContent = data.tool_result || "-";

  finalAnswer.textContent = data.final_answer || "-";

  if (data.verified) {
    explanation.textContent =
      "NextStep found the unfinished part of your work and continued from that expression using SymPy, so the final result is computed rather than guessed.";
  } else {
    explanation.textContent = data.explanation || "NextStep could not verify this input.";
  }

  resetSteps();

  if (data.steps && data.steps.length > 0) {
    data.steps.forEach((step) => {
      const li = document.createElement("li");
      li.textContent = step;
      stepsList.appendChild(li);
    });
    toggleStepsBtn.classList.remove("hidden");
  }
}

function showError(error) {
  setStatus("Error", "error");
  verified.textContent = "false";
  extracted.textContent = "-";
  toolResult.textContent = "-";
  finalAnswer.textContent = "-";
  resetSteps();

  if (typeof error === "string") {
    explanation.textContent = error;
  } else if (error && error.detail) {
    explanation.textContent =
      typeof error.detail === "string"
        ? error.detail
        : JSON.stringify(error.detail, null, 2);
  } else if (error && error.message) {
    explanation.textContent = error.message;
  } else {
    explanation.textContent = JSON.stringify(error, null, 2);
  }
}

document.getElementById("verifyTextBtn").addEventListener("click", async () => {
  showLoading("Checking");

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
    showError(error);
  }
});

document.getElementById("verifyImageBtn").addEventListener("click", async () => {
  const file = imageInput.files[0];

  if (!file) {
    showError("Please choose an image first.");
    return;
  }

  showLoading("Reading image");

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
      throw data;
    }

    showResult(data);
  } catch (error) {
    showError(error);
  }
});