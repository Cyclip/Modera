function getDuration(id) {
	children = $(id).children();
	data = {};
	for (let cindex in children) {
		if (cindex in map) {
			val = parseInt($($(children[cindex]).children()[0]).val());
			data[map[cindex]] = val;
		}
	}
	return data;
}

function resetDuration(id) {
	$(id).map(function() {
		children = $(this).children();
    	for (let cindex in children) {
    		if (cindex in map) {
    			val = $($(children[cindex]).children()[0]).val(0);
    		}
    	}
	}).get();

}

map = {0: "days", 1: "hours", 2: "minutes"};
