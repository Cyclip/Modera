function capitalize(s) {
	return s.charAt(0).toUpperCase() + s.slice(1);
}

function addAttrib(name, attrib) {
	name = capitalize(name);
	code = `<div class="filter-item">
		<h2>${(name.replace("_", " "))}</h2>
		`

	setChecked = [];
	for (let setting in attrib) {
		val = attrib[setting]
		setting = capitalize(setting);

		if (typeof(val) == "boolean") {
			code += `<label class="checkboxContainer">${capitalize(setting)}
				<input type="checkbox" class="attribCheckbox" id="${name}-${setting}" />
				<span class="checkmark"></span>
		</label>`

			if (val) {
				setChecked.push(`#${name}-${setting}`);
			}
		} else if (typeof(val) == "number") {
			code += `
		<div class="sliderContainer">
			<h3 class="sliderText">${setting}:</h3>
			<input type="range" min="1" max="100" value="${val}" class="slider" oninput="this.nextElementSibling.value = this.value; " id="${name}-${setting}">
			<output>${val}</output>
		</div>`
		}
	}

	code += `
</div>
`;
	$("#filter-grid").append(code);

	for (i in setChecked) {
		$(setChecked[i]).prop("checked", true);
	}
}

function addServerSetting(setting, val) {
	if (typeof(val) == "boolean") {
		if (getKeys(describeSettings).includes(setting)) {
			description = `<span class="tooltiptext">${describeSettings[setting]}</span>`;
		} else {
			description = "";
		}

		$("#serverSettings").append(`<div class="serverSetting tooltip">
			${description}
			<label class="checkboxContainer">${capitalize(setting)}
				<input type="checkbox" class="attribCheckbox" id="${setting}">
				<span class="checkmark"></span>
			</label>
		</div><br>`)

		if (val) {
			$(`#${setting}`).prop("checked", true);
		}
	} else if (typeof(val) == "object") {
		// assuming its iterable
		// only allowed iterable is prefixes
		// because im lazy
		for (let prefixIndex in val) {
			if (setting == "prefixes") {
				addPrefix(val[prefixIndex], true);
			}
		}
	}
}

function addPunishmentSelect(name) {
	$("#punishmentSelect").append(`<option value="${name}">${capitalize(name.replace("Filtering", "").replace("_", " "))}</option>`);
}

function loadPunishment_list(name, text) {
	$("#punishmentList").append(`<div class="generalItem" id="punishment-${name}">
		<div class="generalName">
			${text}
			<button onclick="removePunishment('punishment-${name}');">Remove</button>
		</div>
	</div>`)
}

function uuidv4() {
	return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
		var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
		return v.toString(16);
	});
}

function formatReason(reason) {
	reason = reason.split("\n").join(" ");
	if (reason.length > 60) {
		reason = reason.substring(0, 27) + "...";
	}
	return reason
}

function handleSettings(settings) {
	originalSettings = $.extend({}, currentSettings);

	for (let setting in settings) {
		if (!blockedSettings.includes(setting)) {
			val = settings[setting]
			if (setting.endsWith("Filtering")) {
				addAttrib(setting.replace("Filtering", ""), val);
			} else if (setting == "punishment") {
				// punishment
				console.log("Tis punishment - " + val);
				for (let ps in val) {
					console.log(ps);
					addPunishmentSelect(ps);
				}

				loadPunishment();
			} else {
				// server setting
				addServerSetting(setting, val);
			}
		}
	}

	$(".attribCheckbox").change(function() {
		checkChanges();
	});

	$(".slider").change(function() {
		checkChanges();
	});
}

function addPrefix(prefix, force) {
	if (prefix.length == 0) {
		alertify.error("Please enter a prefix");
	} else if (prefix.length > 6) {
		alertify.error("Prefixes can only be 6 characters max");
	} else if (!currentSettings["prefixes"].includes(prefix) || force) {
		uuid = uuidv4();
		code = `<div class="generalItem" id="prefix-${uuid}">
			<div class="generalName">
				${prefix}
				<button onclick="removePrefix('prefix-${uuid}');">Remove</button>
			</div>
		</div>`

		$("#prefixList").append(code);
		$("#prefixInput").val("");

		if (!force) {
			currentSettings["prefixes"].push(prefix);
			checkChanges();
		}
	}
}

function removePrefix(prefix) {
	$(`#${prefix}`).remove();
	currentSettings["prefixes"].splice(
		currentSettings["prefixes"].indexOf(prefix),
		1
	);
	checkChanges();
}

function removePunishment(punishment) {
	element = $(`#${punishment}`)
	filtering = $("#punishmentSelect").val();
	currentSettings["punishment"][filtering].splice(
		element.index(),
		1
	);
	element.remove();
	console.log("3")
	checkChanges();
}

function showTab(tab) {
	$(".section").map(function() {
	    $(this).hide();
	}).get();

	$(`#${tab}`).show();
}

function getKeys(dict) {
	tmp = [];
	for (let i in dict) { tmp.push(i) }
	return tmp;
}

function createPunishment(type) {
	console.log(type);
	$(".popup").children().hide();
	$(`#dialog-${type}`).show();

	$('.ptitle').text(function(_, oldText){
    	return `Add punishment to ${$("#punishmentSelect").val().replace("Filtering", "")}`
	});

	$(".popup").hide().css("visibility", "visible").fadeIn(300);
}

function closeDialog() {
	$(".popup").fadeOut(300);
	setTimeout(function() {
		$(".popup").css("visibility", "hidden");
	}, 300);
}

function addDialog(type) {
	addTo = $("#punishmentSelect").val();
	if (type == "ban") {
		reason = $("#dialog-ban-reason").val();
		currentSettings["punishment"][addTo].push({"type": type, "reason": reason});
	} else if (type == "kick") {
		reason = $("#dialog-kick-reason").val();
		currentSettings["punishment"][addTo].push({"type": type, "reason": reason});
	} else if (type == "mute") {
		reason = $("#dialog-mute-reason").val();
		duration = getDuration("#dialog-mute-duration");
		currentSettings["punishment"][addTo].push({
			"type": type,
			"reason": reason,
			"duration": toSeconds(duration)
		});
	} else if (type == "addRole") {
		rolename = $("#dialog-addRole-rolename").val();
		if (rolename.length == 0) {
			return alertify.error("You need to enter a rolename.");
		}
		currentSettings["punishment"][addTo].push({"type": type, "rolename": rolename});
	} else if (type == "removeRole") {
		rolename = $("#dialog-removeRole-rolename").val();
		if (rolename.length == 0) {
			return alertify.error("You need to enter a rolename.");
		}
		currentSettings["punishment"][addTo].push({"type": type, "rolename": rolename});
	} else if (type == "warn") {
		currentSettings["punishment"][addTo].push({"type": type});
	} else if (type == "dm") {
		userid = $("#dialog-dm-user").val();
		if (userid == "{USER}") {
			userid = 0;
		} else {
			userid = parseInt(userid);
			if ((isNaN(userid) || userid.toString().length != 18)) {
				return alertify.error("Invalid User ID");
			}
		}

		msg = $("#dialog-dm-message").val();
		if (msg.length == 0) {
			return alertify.error("You need to enter a message.");
		}
		currentSettings["punishment"][addTo].push({
			"type": type,
			"user": userid,
			"msg": msg
		});
	}

	loadPunishment();
	closeDialog();
	resetDialog();
	console.log("4")
	checkChanges();
	alertify.success(`Added ${type} punishment to ${capitalize(addTo.replace("Filtering", ""))}`);
}

function loadPunishment() {
	selected = $("#punishmentSelect").val();
	$("#punishmentList").empty();
	for (let i in currentSettings["punishment"][selected]) {
		data = currentSettings["punishment"][selected][i];
		uuid = uuidv4();
		if (data["type"] == "ban") {
			loadPunishment_list(uuid, `Banning with reason "${formatReason(data['reason'])}"`);
		} else if (data["type"] == "kick") {
			loadPunishment_list(uuid, `Kicking with reason "${formatReason(data['reason'])}"`);
		} else if (data["type"] == "mute") {
			loadPunishment_list(uuid, `Muting for ${data['duration']}s with reason "${formatReason(data['reason'])}"`);
		} else if (data["type"] == "addRole") {
			loadPunishment_list(uuid, `Adding role "${data['rolename']}"`);
		} else if (data["type"] == "removeRole") {
			loadPunishment_list(uuid, `Removing role "${data['rolename']}"`);
		} else if (data["type"] == "warn") {
			loadPunishment_list(uuid, `Warn user`);
		} else if (data["type"] == "dm") {
			loadPunishment_list(uuid, `DMing ${data['user']} with msg "${formatReason(data['msg'])}"`);
		}
	}
}

function toSeconds(dur) {
	return (dur["days"] * 86400) + (dur["hours"] * 3600) + (dur["minutes"] * 60);
}

function resetDialog() {
	$("#dialog-ban-reason").val("Reason: {REASON}");
	resetDuration(".duration");
}

function closeSaveDialog() {
	$(".saveDialog").fadeOut(300);
	setTimeout(function() {
		$(".saveDialog").css("visibility", "hidden");
	}, 300);
}

function openSaveDialog() {
	$(".saveDialog").hide().css("visibility", "visible").fadeIn(300);
}

function checkChanges() {
	console.log(currentSettings != originalSettings);
	if (currentSettings != originalSettings && $(".saveDialog").css("visibility") == "hidden") {
		openSaveDialog();
	}
}

function saveChanges() {
	updateAttributeSettings();
	closeSaveDialog();
	$("#saveChanges").prop("disabled", true);
	$.ajax({
        type: "POST",
        url: "/dashboard/save",
        data: JSON.stringify(currentSettings),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (data) {
			alertify.success("Saved settings!");
			originalSettings = $.extend({}, currentSettings);
        },
		error: function(data) {
			alertify.error("Error while saving");
			console.log(data);
			$("#saveChanges").prop("disabled", false);
			openSaveDialog();
		}
    });
	$("#saveChanges").prop("disabled", false);
}

function updateAttributeSettings() {
	attributes = $("#filter-grid").children();
	url = window.location.href.split("?")[0].split("/");
	currentSettings["id"] = parseInt(url[url.length - 1]);

	for (i in attributes) {
		attribute = attributes[i];
		div = $(attribute).children();
		attributeName = $($(attribute).children()[0]).text().toLowerCase().replace(" ", "_") + "Filtering";
		settings = div.splice(1);

		for (si in settings) {
			setting = settings[si];
			className = setting.className;
			if (className == "checkboxContainer") {
				checkbox = $($(settings[si]).children()[0]);
				isChecked = checkbox.prop("checked");
				id = checkbox.attr("id").split("-")[1].toLowerCase();
				currentSettings[attributeName][id] = isChecked;
			} else if (className == "sliderContainer") {
				slider = $($(settings[si]).children()[1]);
				value = parseInt(slider.val());
				id = slider.attr("id").split("-")[1].toLowerCase();
				currentSettings[attributeName][id] = value;
			}
		}
	}

	currentSettings["deleteComments"] = $("#deleteComments").prop("checked");
}

blockedSettings = ["id", "logTo"];
