var wrapper = document.getElementById('alertwrapper');
var example = document.getElementById('examplealert');

function updateMessages(first = false)
{
	var xhr = new XMLHttpRequest();
	var url = location.protocol + "//" + location.host + "/messages";
	xhr.open("GET", url, true);


	xhr.onreadystatechange = function (){
		if (this.readyState == 4 && this.status == 200)
		{
			if (first)
				removeLoader()
			
			var list = JSON.parse(this.responseText);

			list.forEach(msg => {
				createMessage(msg);
			});
		}
	};

	xhr.send();
}

function createMessage(msgobj)
{
	let alert = example.cloneNode(true);
	alert.removeAttribute('id');

	alert.querySelector(".date").innerHTML = msgobj.time.split(" ")[0];
	alert.querySelector(".time").innerHTML = msgobj.time.split(" ")[1];
	alert.querySelector(".message").innerHTML = msgobj.message;
	alert.querySelector(".capcodes").innerHTML = msgobj.capcodes.join(" ");

	wrapper.prepend(alert);
}

function removeLoader()
{
	document.getElementById("loader").remove();
}

updateMessages(true);

// window.setInterval(updateMessages, 1500);
