function invite() {
	console.log("ee");
}

$(document).ready(function () {
	$('#bodyLogoImg').hide().fadeIn(1500);
	$('.title').hide().fadeIn(1500);

	fadein = $('.fadein');
	fadein.hide();
	description = $(".description")
	descText = description.text();
	description.text(" ".repeat(descText.length));

	setTimeout(function() {

		i = 0;

		function descLoop() {
			setTimeout(function() {
				newText = descText.slice(0, i + 1)
				newText = newText + " ".repeat(descText.length - newText.length);
				description.text(newText);
				i++;
				if (i<descText.length) {
					descLoop();
				} else {
					fadein.fadeIn(1000);
				}
			}, 1);
		}

		descLoop();
	}, 500);
});
