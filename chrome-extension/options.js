const ip_input = document.getElementById("server-ip");
const ip_label = document.getElementById("server-ip-label");
const checkmark = document.getElementById("checkmark");
const demo_toggle = document.getElementById("demo-toggle");
const online_tagline = document.getElementById("online-tagline");
const offline_tagline = document.getElementById("offline-tagline");
ip_input.addEventListener("change", handleIpSaved);
ip_input.addEventListener("keydown", handleIpChange);
demo_toggle.addEventListener("change", handleDemoToggle);

chrome.storage.sync.get("server_ip", (data) => {
	ip_input.value = data.server_ip;
	ip_label.innerText = data.server_ip;
	check_connection(data.server_ip);
});

chrome.storage.sync.get("demo", (data) => {
	demo_toggle.checked = data.demo;
});

function handleDemoToggle(event) {
	chrome.storage.sync.set({ demo: event.target.checked });
}

function handleIpChange(event) {
	if (event.key != "Enter") {
		checkmark.classList.add("invisible");
	}
}

function handleIpSaved(event) {
	ip = event.target.value;
	if (ip == "")
		ip = "127.0.0.1";

	chrome.storage.sync.set({ server_ip: ip });
	checkmark.classList.remove("invisible");
	ip_label.innerText = ip;
	check_connection(ip);
}

function check_connection(server_ip) {
	fetch("https://"+server_ip+"/ping").then(res => res.text()).then(res => {
		if (res == "Pong") {
			// connection OK
			online_tagline.classList.remove("gone");
			offline_tagline.classList.add("gone");
		}
		else {
			// error
			online_tagline.classList.add("gone");
			offline_tagline.classList.remove("gone");
		}
	}).catch(() => {
		// error
		online_tagline.classList.add("gone");
		offline_tagline.classList.remove("gone");
	});
}