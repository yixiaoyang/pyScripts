$(document).ready(function(){
	$("#container").height(Math.max($("#main").height() + 200, $("#leftmenu").height() + 200));
});

$(window).load(function() {
	resizePage();
});

function resizePage() {
	$("#container").height(Math.max($("#main").height() + 200, $("#leftmenu").height() + 200));
}

	function redirect(e){
		top.location = e;
	}