$(document).ready(function() {
	$(".hidden").fadeIn(1000).removeClass("hidden");
});

$(window).bind("beforeunload", function() {
	$("body").fadeOut(500).addClass("hidden");
});
