function changeFilter(filter) {
	$("#content").children().hide();
	$(`.bar>button.active`).removeClass("active");

	$(`#content-${filter}`).show();
	$(`#filter-${filter}`).addClass("active");
}

$(document).ready(function() {
	$("#mc-toxicity").click(function() {
		window.open("https://docs.google.com/spreadsheets/d/13edevE6WQLhEQ7r3nY4Z1leJZ-M5BbO_4UUQwc33Hr4/edit#gid=666710886");
	});
	$("#mc-overview").click(function() {
		window.open("https://developers.perspectiveapi.com/s/about-the-api-model-cards");
	});
	$("#mc-performance").click(function() {
		window.open("https://developers.perspectiveapi.com/s/about-the-api-model-cards?tabset-20254=3");
	});
	$("#mc-datasets").click(function() {
		window.open("https://www.perspectiveapi.com/research/#public-datasets");
	});
	$("#mc-osc").click(function() {
		window.open("https://www.perspectiveapi.com/research/#open-source-code");
	});
	$("#mc-research-contributions").click(function() {
		window.open("https://www.perspectiveapi.com/research/#research-contributions");
	});
});
