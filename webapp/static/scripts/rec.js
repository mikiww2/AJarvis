'use strict';

var recorder;
var upload_queue=[]; // use push() and shift()
var uploading=false;

//init
window.onload=function() {
	init_timer(); //from timer.js
	init_recorder();
};

//recorder init
function init_recorder() {
	// Put variables in global scope to make them available to the browser console. //SAFARI NEED IT
	var audio = document.querySelector('audio');

	var constraints=window.constrains={
		audio: {
			sampleRate: 44000 //browsers have different default sampleRate
			//channelCount: 2
		},
		video: false
	};

	// prepare recorder from RecorderJs

	//console.log(adapter.browserDetails.browser);
	//console.log(navigator.mediaDevices.getSupportedConstraints());

	navigator.mediaDevices.getUserMedia(constraints)
	.then(function(stream) {
		var AudioContext= AudioContext || window.AudioContext || window.webkitAudioContext // because adapter.js sucks
		var audioNode=  new AudioContext();
    	var audio=audioNode.createMediaStreamSource(stream); // need to upgrade with a choose_device menu

	  	recorder= new Recorder(audio, { "workerPath":'static/scripts/recorderWorker.js' }); // workerPath='js/recorderjs/recorderWorker.js', bufferLen=4096, type='audio/wav'. // ..... external download ... noot good
	  	//console.log('Recorder initialised');

	  	load_complete();
	})
	.catch(function(error) {
		load_error();
	});
}

function recordingButtonClicked() {
	recorder && recorder.record();

	startTimer();

	start_resume_press();
}

function pauseRecordingButton() {
	recorder.stop();

	pauseTimer();

	stop_press();
}

function restartButtonClicked() {

	recorder.stop();
	recorder.clear();

	refreshTimer();

	recorder && recorder.record();

	startTimer();

	restart_press();
}

function sendButtonClicked() {
	
	send_press(); //wait until convert

	//send audio to backend
	recorder.exportWAV(function(blob) {
		upload_queue.push(blob);

		update_count();

		if(!uploading) {

			start_upload();

			upload();
		}

		regen_recording(); //can rec again
	});
}

function regen_recording() {

	recorder.clear()
	refreshTimer();

	regen_visual();
}

//// HTML METHODS

function load_complete() {
	hide_element('loadingProgressBar');
	hide_message();

	show_element('recorder');
	show_element('tips');

}

function load_error() {
	show_message('Non riesco ad attivare il registratore', 'danger');
}

function start_resume_press() {
	hide_button('recordingButton');
	hide_button('restartButton');
	hide_button('sendButton');
	show_button('pauseRecordingButton');

	//delete_flash();
}

function stop_press() {
	document.getElementById("recordingButton").value='resume';
	document.getElementById("recordingButton").innerHTML='Riprendi';

	hide_button('pauseRecordingButton');
	show_button('recordingButton');
	show_button('restartButton');

	show_button('sendButton');
}

function restart_press() {

	document.getElementById("recordingButton").value='start';
	document.getElementById("recordingButton").innerHTML='Registra';

	hide_button('recordingButton');
	hide_button('restartButton');
	hide_button('sendButton');
	show_button('pauseRecordingButton');
}

function send_press() {
	document.getElementById("sendButton").disabled=true;

	//hide_element('timer');
	hide_button('pauseRecordingButton');
	hide_button('restartButton');
	hide_element('tips');
	show_element('convertingProgressBar', 'inline'); //because recorder.exportWAV take time to process WAV blob
}

function regen_visual() {
	show_message('Conversione riuscita, invio l\'audio');

	document.getElementById("recordingButton").value='start';
	document.getElementById("recordingButton").innerHTML='Registra';

	hide_element('convertingProgressBar')
	hide_button('sendButton');

	//show_element('timer')
	show_button('recordingButton');
	show_element('tips');
	
	document.getElementById("sendButton").disabled=false;
}

function start_upload() {
	show_element('uploadingProgressBar');
}

function end_upload() {
	hide_element('uploadingProgressBar');

	show_message('Caricamento audio terminato');
}

function update_count() {
	document.getElementById('infoUpload').innerHTML=upload_queue.length;
}

function update_progressBar(value=0) {
	var progressBar=document.getElementById("uploadProgressBar");
	//progressBar.style.width=value+'%';
	//$('#uploadProgressBar').css("width", value+'%').attr('aria-valuenow', value+'%'); //not good
	progressBar.style.width=value+'%';
	progressBar.getAttribute("aria-valuenow").value=value;
	progressBar.value=value+'%';

	progressBar.textContent=progressBar.value; // Fallback for unsupported browsers.
}

function upload() {
	uploading=true;

	update_progressBar();

	var blob=upload_queue.shift()
	update_count();

	//retrieve url for post
	var retrieve_url= new XMLHttpRequest();
	
	retrieve_url.onreadystatechange=function() {
		if(this.readyState == 4) {
			if(this.status == 200) {

				update_progressBar();
				//console.log(this.responseText);

				// post audio to s3
				var post_request= new XMLHttpRequest();

				//update ProgressBar
				post_request.upload.onprogress=function(progress) {
					if(progress.lengthComputable) {
						var value=Math.round((progress.loaded/progress.total)*100)
						update_progressBar(value);
						//console.log('%s %s %s', value, progress.loaded, progress.total);
					}
				};

				post_request.onreadystatechange=function() {
					if(this.readyState == 4) {
						if(this.status == 200) {
							console.log("All done");
							
							show_message('Caricamento audio riuscito');

							if(upload_queue.length) {
								upload();
							}
							else {
								uploading=false;

								end_upload();
							}
						}
						else {
							show_message('Caricamento audio non riuscito, riprovo', 'danger');
							upload_queue.unshift(blob);
							update_count();

							upload();
						}
					}
				};
				
				post_request.open('PUT', this.responseText, true);

				post_request.setRequestHeader('Content-type', 'audio/wav');
				//post_request.setRequestHeader('Access-Control-Allow-Origin', '*');

				//console.log("ready");

				post_request.send(blob);

  				//console.log("send");
  			}
			else {
				show_message('Caricamento audio non riuscito, riprovo', 'danger');
				upload_queue.unshift(blob);
				update_count();

				upload();
			}
		}
	};
	retrieve_url.open("GET", "/upload/link", true);
	//retrieve_url.setRequestHeader('Access-Control-Allow-Origin', '*');

	retrieve_url.send();
}