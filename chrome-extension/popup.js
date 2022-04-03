const power_button = document.getElementById("power-button");

// power button clicked
power_button.addEventListener('change', function() {
	chrome.storage.sync.set({ power: this.checked });

	// refresh page
	chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
		chrome.tabs.reload(tabs[0].id);
	});
});

chrome.storage.sync.get("power", (data) => {
	power_button.checked = data.power;
});
