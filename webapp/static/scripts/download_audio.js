function download_audio_clicked(button) {
	var retrieve_url= new XMLHttpRequest();

	retrieve_url.onreadystatechange=function() {
		if(this.readyState == 4) {
			if(this.status == 200) {
				console.log('retrieved url: '+this.responseText);

				window.open(this.responseText);
			}
		}
	};
	retrieve_url.open("GET", "/download/link/"+button.value, true);
	
	retrieve_url.send();
}