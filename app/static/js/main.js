/**
 * Nutrition Management System - Professional JS
 * No animations, static behavior only
 */

document.addEventListener("DOMContentLoaded", function () {
  console.log("Nutrition Management System - Loaded");

  // Form validation
  initFormValidation();

  // Alert auto-dismiss (optional)
  initAlertDismiss();

  // Date input max date
  initDateInputs();

  // Print functionality
  initPrintButtons();
});

/**
 * Form validation on submit
 */
function initFormValidation() {
  const forms = document.querySelectorAll("form");

  forms.forEach(function (form) {
    form.addEventListener(
      "submit",
      function (event) {
        if (!form.checkValidity()) {
          event.preventDefault();
          event.stopPropagation();
        }
        form.classList.add("was-validated");
      },
      false
    );
  });
}

/**
 * Auto-dismiss alerts after 8 seconds
 */
function initAlertDismiss() {
  const alerts = document.querySelectorAll(".alert");

  alerts.forEach(function (alert) {
    setTimeout(function () {
      alert.style.display = "none";
    }, 8000);
  });
}

/**
 * Set max date for date inputs (today)
 */
function initDateInputs() {
  const dateInputs = document.querySelectorAll('input[type="date"]');
  const today = new Date().toISOString().split("T")[0];

  dateInputs.forEach(function (input) {
    if (input.name === "dob") {
      input.max = today;
    }
  });
}

/**
 * Print functionality for reports
 */
function initPrintButtons() {
  const printButtons = document.querySelectorAll(".btn-print");

  printButtons.forEach(function (button) {
    button.addEventListener("click", function () {
      window.print();
    });
  });
}

/**
 * Confirm delete action
 */
function confirmDelete(itemName) {
  return confirm("Are you sure you want to delete " + itemName + "?");
}

/**
 * BMI Preview Calculator (optional)
 */
function initBMIPreview() {
  const heightInput = document.getElementById("height");
  const weightInput = document.getElementById("weight");

  if (heightInput && weightInput) {
    const previewDiv = document.getElementById("bmi-preview");

    function updatePreview() {
      const height = parseFloat(heightInput.value);
      const weight = parseFloat(weightInput.value);

      if (height > 0 && weight > 0) {
        const heightM = height / 100;
        const bmi = (weight / (heightM * heightM)).toFixed(2);

        if (previewDiv) {
          previewDiv.textContent = "Preview BMI: " + bmi;
        }
      }
    }

    heightInput.addEventListener("input", updatePreview);
    weightInput.addEventListener("input", updatePreview);
  }
}
