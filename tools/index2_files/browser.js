$(window).load(new function() {
	var lang = navigator.browserLanguage ? navigator.browserLanguage : navigator.language;

	if (lang.indexOf('en') > -1) {
		// 英文版本
		var addr = toString(window.top.location);
		if (addr.indexOf('www.math.pku.edu.cn:8000/en') == -1) {
			// window.top.location = "http://www.math.pku.edu.cn:8000/en/newpage";
		}
	}

	if (lang.indexOf('zh') > -1) {
		//中文版本
		var addr = toString(window.top.location);
		if (addr.indexOf('www.math.pku.edu.cn:8000/en') > -1) {
			// window.top.location = "http://www.math.pku.edu.cn/htdocs";
		}
	}
});
