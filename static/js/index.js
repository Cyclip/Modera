function copyToClipboard(element) {
    var $temp = $("<input>");
    $("body").append($temp);
    $temp.val($(element).text()).select();
    document.execCommand("copy");
    $temp.remove();
}

function inviteScroll() {
	$([document.documentElement, document.body]).animate({
		scrollTop: $("#invite").offset().top
	}, 1000);
}

function invite() {
	var win = window.open("https://discord.com/api/oauth2/authorize?client_id=840601414685556746&permissions=8&scope=bot", '_blank');
	if (win) {
	    //Browser has allowed it to be opened
	    win.focus();
	} else {
	    //Browser has blocked it
	    alertify.alert('Please allow popups for this website');
	}
}

function configure() {
    window.open("/dashboard", "_self");
}

function copyInvite() {
	copyToClipboard("#inviteCode");
	alertify.success("Copied to clipboard!");
}

$(document).ready(function () {
	$('#bodyLogoImg').hide().fadeIn(1500);
	$('.title').hide().fadeIn(1500);

	fadein = $('.fadein');
	fadein.hide();
	fadein.addClass("show");
	description = $(".description")
	descText = description.text();
	description.text(" ".repeat(descText.length));
	description.addClass("show");

	featuresTitle = $("#fs_title");
	fs_title = featuresTitle.text();
	featuresTitle.text("");
	$(".fsttext").hide();
	$(".fstimgcont").hide();


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
			}, 20);
		}

		descLoop();
	}, 500);
});

$(window).scroll(function() {
	currentScroll = $(window).scrollTop();

	if (!($("#featureSection").hasClass("shown"))) {
		targetScrollFeatures = $("#featureSection").offset().top - 250;
		if (currentScroll > targetScrollFeatures) {
			$("#featureSection").addClass("shown");
			i = 0;

			function fs_loop() {
				setTimeout(function() {
					newTextFs = fs_title.slice(0, i + 1);
					$("#fs_title").text(newTextFs);
					i++;
					if (i < fs_title.length) {
						fs_loop();
					} else {
						$(".fsttext").fadeIn(1000);
						setTimeout(function() {
							$(".fstimgcont").fadeIn(1000);
						}, 500);
					}
				}, 20);
			}

			fs_loop();
		}
	}
})
