function handleUpdate(request){
    if(request.readyState != 4)
        return;
    if(request.status == 204) {
        console.log("No data yet");
        return;
    }
    var parsed;
    try {
        parsed = JSON.parse(request.responseText);
    } catch(SyntaxError) {
        console.log("Invalid JSON: "+request.responseText);
        return;
    }
    console.log(parsed);
    if(parsed.messages != undefined){
        console.log("Messages!");
    }
    if(parsed.scores != undefined){
        var sortedScores = parsed.scores;
        sortedScores.sort(function(left,right){
            return left.score > right.score;
        });
        var trs = sortedScores.map(function(element){
            var group = document.createElement('td');
            group.innerText = element.group;
            var score = document.createElement('td');
            score.innerText = element.score;
            var newTr = document.createElement('tr');
            newTr.appendChild(group);
            newTr.appendChild(score);
            return newTr;
        });
        [].forEach.call(document.querySelectorAll('#scores tbody tr'), function(child){
            child.parentNode.removeChild(child);
        });
        trs.forEach(function(tr){
            document.querySelector('#scores tbody').appendChild(tr);
        });
    }
}

function loadScores(){
    var req = new XMLHttpRequest();
    req.open('GET', 'https://borrel.collegechaos.nl:2003', true);
    req.onreadystatechange = function(){
        handleUpdate(req);
    }
    req.send();
    //window.setTimeout(loadScores, 1000);
}

document.addEventListener("DOMContentLoaded", function() {
    window.scrollTo(0,0);
    window.setTimeout(loadScores);
});
