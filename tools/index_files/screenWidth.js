window["MzBrowser"]={};(function()
{
if(MzBrowser.platform) return;
var ua = window.navigator.userAgent;
MzBrowser.platform = window.navigator.platform;

MzBrowser.firefox = ua.indexOf("Firefox")>0;
MzBrowser.opera = typeof(window.opera)=="object";
MzBrowser.ie = !MzBrowser.opera && ua.indexOf("MSIE")>0;
MzBrowser.mozilla = window.navigator.product == "Gecko";
MzBrowser.netscape= window.navigator.vendor=="Netscape";
MzBrowser.safari= ua.indexOf("Safari")>-1;

if(MzBrowser.firefox) var re = /Firefox(\s|\/)(\d+(\.\d+)?)/;
else if(MzBrowser.ie) var re = /MSIE( )(\d+(\.\d+)?)/;
else if(MzBrowser.opera) var re = /Opera(\s|\/)(\d+(\.\d+)?)/;
else if(MzBrowser.netscape) var re = /Netscape(\s|\/)(\d+(\.\d+)?)/;
else if(MzBrowser.safari) var re = /Version(\/)(\d+(\.\d+)?)/;
else if(MzBrowser.mozilla) var re = /rv(\:)(\d+(\.\d+)?)/;

if("undefined"!=typeof(re)&&re.test(ua))
MzBrowser.version = parseFloat(RegExp.$2);
})(); 
function aa()
{
	if(MzBrowser.ie)
	{
	return('ie'+MzBrowser.version);
	}
	if(MzBrowser.firefox)
	{
	return('firefox'+MzBrowser.version);
	}
}
	
function checkWidth(){
	if(screen.width>1024){
		//document.getElementById("wrapper").style.width="100%";
	}else{
		document.getElementById("footerSL").style.left="-20px";
		document.getElementById("footerSR").style.right="-20px";
		//document.getElementById("footer_pucaFollow").style.left="730px";
		if(aa()=='ie6'){
			//document.getElementById("wrapper").style.width="964px";
		}else if(aa()=='ie7'){
			//document.getElementById("wrapper").style.width="963px";
		}else{
			//document.getElementById("wrapper").style.width="968px";
		}
	}
}