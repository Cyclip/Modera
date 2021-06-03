function openServer(url, name, icon) {
	window.open("dashboard/" + url + "?name=" + name + "&icon=" + icon, "_self");
}

function addServer(icon, id, name) {
	code = `
<div class="grid-item">
	<img src="` + icon + `" class="serverIcon" />
	<h2 class="serverName">` + name + `</h2>
	<button onclick="openServer('` + id + `', '` + name + `', '`+ icon + `')">EDIT</button>
</div>
`;
	$("#container").append(code);
}
