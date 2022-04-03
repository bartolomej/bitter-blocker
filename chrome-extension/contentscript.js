let server_ip;
let demo = false;

chrome.storage.sync.get("power", (powe) => {
	chrome.storage.sync.get("server_ip", (ip) => {
		chrome.storage.sync.get("demo", (deemo) => {
			demo = deemo.demo;
			const power = powe.power;
			server_ip = ip.server_ip;
			if (power) {
				setInterval(() => {
					filter_fnct(filter_cached(get_tweet_data()), data => data.forEach(data => {
						hide_element(data.element);
					}));
				}, 1000);
			}
		});
	});
});

get_tweet_id = el => {
    let id_ = "";
    const a_elems = [...el.getElementsByTagName("a")].map(e => e.href);
    for(let i = 0; i < a_elems.length; i++){
        const regsult = a_elems[i].match(/.*\/status\/(\d+)?.*/);
        if(regsult && regsult.length > 1){
            id_ = regsult[1];
            break;
        }
    }
    return id_;
}

get_tweet_data = () => [...document.querySelectorAll('article')].map(e => e.getElementsByClassName("css-901oao r-37j5jr r-a023e6 r-16dba41 r-rjixqe r-bcqeeo r-bnwqim r-qvutc0")).filter(e => e.length > 0).map(e => {
    const article_element = e[0].closest("article");
    return ({
        text: [...e].map(j => j.innerText).join(),
        element: article_element,
        id: get_tweet_id(article_element)
    })
});

hide_element = (el) => {
	el.setAttribute("data-bitter", true);
    if (demo) {
		el.style.boxShadow = "inset 0px 0px 32px 7px rgb(255 0 0 / 84%)";
	}
	else {
		el.style.display = "none";
	}
}

filter_cached = (arr) => arr.filter(e => !e.element.getAttribute("data-cached"))

filter_fnct = (tweet_data, callback) => {
	//console.log(tweet_data)
	if(tweet_data.length > 0) fetch("https://"+server_ip+"/prediction", {
		method: 'POST',
		headers: {
		'Content-Type': 'application/json'
		},
		body: JSON.stringify(tweet_data.map(e => ({id:e.id, text:e.text})))
	}).then(res => res.json()).then(json => {
		tweet_data.forEach(el => el.element.setAttribute("data-cached", true));
		out_json = tweet_data.map(el => Object.assign(el,{neg:json[el.id].is_negative})).filter(el => el.neg)

		console.log(out_json);
		if(callback) callback(out_json);
		}
	).catch((err) => {console.error(err); return tweet_data});
}
