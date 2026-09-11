// nbox extension popup controller

document.addEventListener("DOMContentLoaded", () => {
  const toggleEnabled = document.getElementById("toggle-enabled");
  const toggleWatermark = document.getElementById("toggle-watermark");
  const slider = document.getElementById("sharpness-slider");
  const sliderVal = document.getElementById("sharpness-val");

  // Load saved settings
  chrome.storage.local.get(
    {
      nboxEnabled: true,
      nboxShowWatermark: true,
      nboxSharpness: 35,
    },
    (items) => {
      toggleEnabled.checked = items.nboxEnabled;
      toggleWatermark.checked = items.nboxShowWatermark;
      slider.value = items.nboxSharpness;
      sliderVal.textContent = items.nboxSharpness + "%";
    }
  );

  toggleEnabled.addEventListener("change", () => {
    chrome.storage.local.set({ nboxEnabled: toggleEnabled.checked });
  });

  toggleWatermark.addEventListener("change", () => {
    chrome.storage.local.set({ nboxShowWatermark: toggleWatermark.checked });
  });

  slider.addEventListener("input", () => {
    sliderVal.textContent = slider.value + "%";
    chrome.storage.local.set({ nboxSharpness: parseInt(slider.value, 10) });
  });
});
