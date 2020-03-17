function Record(id,time)
{
    this.UserID = id;
    this.Time = time;
}

var records = [];

function initRecords()
{
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function()
    {
        if(xhttp.readyState == 4 && xhttp.status == 200)
        {
            var data = xhttp.responseText;
            var recordStrings = data.split(";");
            console.log(recordStrings)
            for(var i=0;i<5&&i<recordStrings.length-1;i++)
            {
                var textinput;
                switch(i){
                    case 0:
                        textinput = document.getElementById('1st');
                        break;
                    case 1:
                        textinput = document.getElementById('2nd');
                        break;
                    case 2:
                        textinput = document.getElementById('3rd');
                        break;
                    case 3:
                        textinput = document.getElementById('4th');
                        break;
                    case 4:
                        textinput = document.getElementById('5th');
                        break;
                }
                var recordString = recordStrings[i];
                var attributeStrings = recordString.split(",");
                textinput.value = attributeStrings[0]+"  "+attributeStrings[1]+"s"
            }
        }
    }
    xhttp.open("GET", "/loadRecords/",true);
    xhttp.send();
    return;
}
