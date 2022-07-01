var last = 0; // Timestamp of last message we saw
var size = 0; // Size of page

// Request data from api
function updateMessages(first = false)
{
	let xhr = new XMLHttpRequest();
	let url = "/messages";
	xhr.open("GET", url, true);

	// When request completes and is OK, process data
	xhr.onreadystatechange = function (){
		if (this.readyState == 4 && this.status == 200)
		{
			// Remove loading animation
			if (first)
				removeLoader()
			
			let list = JSON.parse(this.responseText);

			// Take over length as length for page as well
			size = list.length;

			// Loop over messages and only append if they are AFTER the last timestamp we saw
			list.forEach(msg => {
				if (msg.timestamp > last)
				{
					createMessage(msg);
					last = msg.timestamp;
				}
			});
		}
	};

	xhr.send();
}

// Keep the alerts rotating
function limitElements()
{
	let children = document.getElementById('alertwrapper').children;

	if (children.length > size)
	{
		let e = children[size];
		e.remove();
	}
}

// Create a message on the page from a template
function createMessage(msgobj)
{
	// Clone and remove id to prevent conflichts
	let alert = document.getElementById('examplealert').cloneNode(true);
	alert.removeAttribute('id');

	// Fill in data
	alert.querySelector(".date").innerHTML = msgobj.time.split(" ")[0];
	alert.querySelector(".time").innerHTML = msgobj.time.split(" ")[1];
	alert.querySelector(".message").innerHTML = msgobj.message;
	alert.querySelector(".capcodes").innerHTML = msgobj.capcodes.join(" ");

	// Push to page
	document.getElementById('alertwrapper').prepend(alert);

	// Make sure we don't go over the threshold, prevents long-term issues
	limitElements();
}

// Remove the loading animation
function removeLoader()
{
	document.getElementById("loader").remove();
}

// Startup and set interval
updateMessages(true);
window.setInterval(updateMessages, 1500);
