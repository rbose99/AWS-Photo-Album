var search_bar = document.getElementById("searchBar");
var li = document.getElementsByTagName("li");
search_bar.onkeyup = function(){
   var search_value = search_bar.value.toLowerCase();
   for(var l = 0;l<li.length;l++){
       if(li[l].innerHTML.toLocaleLowerCase().search(search_value) == -1){
           li[l].style.display = 'none';
       }else{
        li[l].style.display = 'block';
       }
   }
}

function search()
{
	var query = document.getElementsByClassName('searchBar')[0];
	console.log(query.value);

	if (!query.value)
	{
		alert('Please enter something to search');
	}
	else
	{
		getResults(query.value.trim().toLowerCase());
	}
}

function getResults(q)
{
	document.getElementsByClassName('searchBar')[0].value = '';

 	var sdk = apigClientFactory.newClient();

    sdk.searchGet({ q: q})
    	.then(function(result) {
    	
    		var results = result['data']['results'];
            console.log("Res")
            console.log(results[0])
            console.log (result)
            if (results.length == 0)
            {
                alert("No images found.");
            }

    		var section = document.getElementById('searchResults');
    		section.innerHTML = "";
            console.log(results)
    		for (var i=0; i<results.length; i++)
    		{
    			section.innerHTML += "<figure><img src=" + results[i] + " style='width:40%'></figure>"
    		}
    	}).catch(function(result){
    		console.log(result);
    	});
}

function upload()
{
	var filePath = (document.getElementById('uploadedFile').value).split("\\");
    var fileName = filePath[filePath.length - 1];
    var fileExt = fileName.split(".").pop();
    if (!document.getElementById('customLabels').value != "") {
        var customLabels = document.getElementById('customLabels').value;
    }
    else {
        var customLabels = ""
    }
    console.log(fileName);

    var file = document.getElementById("uploadedFile").files[0];
    file.constructor = () => file;

    console.log(file.type);

    var sdk = apigClientFactory.newClient({ apiKey: KEY_NAME });

    var params = {
        'x-amz-meta-customLabels': customLabels,
        "filename": fileName,
        "bucket": "ccbd-photos",
        "x-api-key": KEY_NAME
    };

    var additionalParams = {
        headers: {
            //'x-amz-meta-customLabels': custom_labels.value,
            'Content-Type': file.type,
            //'policy': ["starts-with", "$x-amz-meta-customLabels", ""]
        }
    };

    var reader = new FileReader();
    reader.onload = function (event) {
        body = btoa(event.target.result);
        return sdk.uploadPut(params, file, additionalParams)
        .then(function(result) {
            console.log(result);
            alert('Image uploaded successfully')
        })
        .catch(function(error) {
            console.log(error);
        })
    }
    reader.readAsBinaryString(file);

    document.getElementById('uploadedFile').value = "";
    document.getElementById('customLabels').value = "";

    // var url = "https://wajuqrne5c.execute-api.us-east-1.amazonaws.com/v1/upload/photos-st3523/duck.jpeg"
    // axios.put(url, file, params).then(response => {
    //     alert("Image uploaded: " + file.name);
    // })
    // .catch(function(error) {
    //     console.log(error);
    // });   
}
window.SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition

function record()
{
    var search= document.getElementsByClassName('searchBar')[0];
    const recognition = new window.SpeechRecognition();

    mic = document.getElementById("mic");  
    
    if (mic.innerHTML == "micOn") {
        recognition.start();
    } else if (mic.innerHTML == "micOff"){
        recognition.stop();
    }

    recognition.addEventListener("start", function() {
        mic.innerHTML = "micOff";
    });

    recognition.addEventListener("end", function() {
        mic.innerHTML = "micOn";
    });

    recognition.addEventListener("result", speech);
    function speech(event) {
        search.value =  event.results[current][0].transcript;
    }
}
