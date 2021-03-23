var slider_dance = new Slider('#dance', {
	formatter: function(value) {
		return 'Current value: ' + value;
	}
});
var slider_energy = new Slider('#energy', {
	formatter: function(value) {
		return 'Current value: ' + value;
	}
});
var slider_instrumental = new Slider('#instrumental', {
	formatter: function(value) {
		return 'Current value: ' + value;
	}
});
var slider_valence = new Slider('#valence', {
	formatter: function(value) {
		return 'Current value: ' + value;
	}
});

const getRecommendations = () =>{
    var dance = document.querySelector("#dance").value
    var energy = document.querySelector("#energy").value
    var instrumental = document.querySelector("#instrumental").value
    var valence = document.querySelector("#valence").value
    window.location.href = "/recommendedsongs?dance="+dance+"&energy="+energy+"&instrumental="+instrumental+"&valence="+valence
}
