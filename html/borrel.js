function makeElectron(shell, spot, delay_steps){
    var e_loc = document.createElement('div');
    e_loc.setAttribute('class', 'electron-location electron-loc'+shell);
    e_loc.setAttribute('id', 'electron'+shell+spot);
    var electron = document.createElement('div');
    electron.setAttribute('class', 'electron');
    e_loc.appendChild(electron);
    // Trim animation offset
    // 1-spot (1,2,3) → (0, -1, -2)
    e_loc.setAttribute('style', 'animation-delay: '+((1-spot)*delay_steps)+'s;');

    return e_loc;
}

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
    //console.log(parsed);
    if(parsed.messages != undefined){
        parsed.messages.forEach(function(message){
            var cur_time = Math.floor(Date.now() / 1000);
            var appear_ts = message.from;
            var leave_ts = message.to;

            var message_id = ""+appear_ts+"-"+leave_ts;
            if(document.getElementById(message_id) != null || leave_ts < cur_time){
                return;
            }
            var message_pane = document.getElementById('right-bar');
            var msg_el = document.createElement('p');
            msg_el.setAttribute('id', message_id);
            msg_el.innerHTML = message.message;
            msg_el.hidden = true;
            message_pane.appendChild(msg_el);
            window.setTimeout(function(){
                var msg_el = document.getElementById(message_id);
                msg_el.hidden = false;

                var cur_time = Math.floor(Date.now() / 1000);
                window.setTimeout(function(){
                    var msg_el = document.getElementById(message_id);
                    msg_el.parentNode.removeChild(msg_el);
                }, Math.max(0, (leave_ts - cur_time)*1000));
            }, Math.max(0, (appear_ts - cur_time)*1000));
        });
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
    }
    if(parsed.electrons != undefined){
        var electrons = parsed.electrons;
        var inner = document.getElementById('inner-orbit');
        var middle = document.getElementById('middle-orbit');
        var outer = document.getElementById('outer-orbit');
        if(document.querySelectorAll('.electron-loc2').length != electrons[1].length){
            // Remove all
            [].forEach.call(document.querySelectorAll('.electron-loc2'), function(e2){
                middle.removeChild(e2);
            });
            // Add new
            for(var i = 0; i < electrons[1].length; i++){
                middle.appendChild(makeElectron(2, i+1, 8/electrons[1].length));
            }
        }
        if(document.querySelectorAll('.electron-loc3').length != electrons[2].length){
            // Remove all
            [].forEach.call(document.querySelectorAll('.electron-loc3'), function(e3){
                outer.removeChild(e3);
            });
            // Add new
            for(var i = 0; i < electrons[2].length; i++){
                outer.appendChild(makeElectron(3, i+1, 16/electrons[1].length));
            }
        }
        // Actually replace electrons
        for(var shell = 0; shell < 3; shell++){
            for(var spot = 0; spot < electrons[shell].length; spot++){
                var elec = document.querySelector('#electron'+(shell+1)+(spot+1)+' .electron');
                if(electrons[shell][spot] == null){
                    elec.setAttribute('style', '');
                } else {
                    elec.setAttribute('style', 'background-color: transparent; background-image: url("img/'+electrons[shell][spot]+'.png"); border-radius: 0;');
                }
            }
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
