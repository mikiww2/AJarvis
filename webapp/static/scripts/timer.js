//// TIMER METHODS

// timer globals
var timer, seconds, minutes, hours;

// timer init
function init_timer() {
	seconds=0;
	minutes=0;
	hours=0;
}

// start timer
function startTimer() {
	timer=setInterval(function() {
		seconds++;

		validateTimer();
		updateHtmlTimer();
	}, 1000);
}

function refreshTimer() {
	clearInterval(timer);
	seconds=0;
	minutes=0;
	hours=0;

	updateHtmlTimer();
}

//stop timer
function pauseTimer() {
	clearInterval(timer);
}

//validate secvonds, minutes, hours
function validateTimer() {
	if(seconds == 60) {
		seconds=0;
		minutes++;
		if(minutes == 60) {
			minutes=0;
			hours++;
		}
	}
}

//update html timer
function updateHtmlTimer() {
	if(seconds < 10)
		document.getElementById("seconds").innerHTML="0" + seconds;
	else
		document.getElementById("seconds").innerHTML=seconds;

	if(minutes < 10)
		document.getElementById("minutes").innerHTML="0" + minutes;
	else
		document.getElementById("minutes").innerHTML=minutes;

	if(hours < 10)
		document.getElementById("hours").innerHTML="0" + hours;
	else
		document.getElementById("hours").innerHTML=hours;
}