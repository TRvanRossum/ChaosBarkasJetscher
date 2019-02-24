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
            return right.score - left.score;
        });
        var trs = sortedScores.map(function(element){
            var group = document.createElement('td');
            group.setAttribute('class', 'group');
            group.innerText = element.group;
            var score = document.createElement('td');
            score.setAttribute('class', 'score');
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

        // Start uber-hacky
        // We will replace this. This is too hacky
        sortedScores = parsed.scores;
        sortedScores.sort(function(left, right){
            return right.multiplier - left.multiplier;
        });
        console.log(sortedScores);
        var shell = 1;
        var electron = 1;
        sortedScores.forEach(function(score){
            document.querySelector('#electron'+shell+electron+' .electron').setAttribute('style', 'background-image: url("img/'+score.group+'.png");');

            electron += 1;
            if((shell == 1 && electron > 2) || electron > 8){
                shell += 1;
                electron = 1;
            }
        });
        // end uber-hacky
    }
    if(parsed.electrons != undefined){
        var shellsizes = parsed.electrons.shellsizes;
        if(document.querySelector('.electron-loc2') != shellsizes[1]){
            // Remove excess
            // Add new
            // Trim animation offset
        }
        if(document.querySelector('.electron-loc3') != shellsizes[2]){
            // Remove excess
            // Add new
            // Trim animation offset
        }
    }
}

function loadScores(){
    var req = new XMLHttpRequest();
    req.open('GET', 'https://borrel.collegechaos.nl:2003', true);
    req.onreadystatechange = function(){
        handleUpdate(req);
    }
    req.send();
    window.scrollTo(0,0);
    window.setTimeout(loadScores, 1000);
}

document.addEventListener("DOMContentLoaded", function() {
    window.scrollTo(0,0);
    window.setTimeout(loadScores);
});
