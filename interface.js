function search(ele) {
    if(event.key === 'Enter') {
        var xhr = new XMLHttpRequest();
        xhr.open('POST', "http://ec2-3-22-117-212.us-east-2.compute.amazonaws.com/", true);
        xhr.onreadystatechange = function() {
            if (xhr.readyState>3 && xhr.status==200) { display(xhr.responseText); }
        };
        xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
        xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        xhr.send('text=' + ele.value);
    }
}
function display(text)
{
    document.getElementById("results").innerHTML = text;
}