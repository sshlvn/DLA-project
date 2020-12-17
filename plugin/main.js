(function (){
    var regex = /[?&]([^=#]+)=([^&#]*)/g,
        url = window.location.href,
        params = {},
        match;
    while(match = regex.exec(url)) {
        params[match[1]] = match[2];
    }

    let videoId = params['v'];

    var subtitles = null;
    
    fetch('https://youtubetts.herokuapp.com/json/' + videoId)
        .catch(t => console.log(t))
        .then(r => r.text())
        .then(result => {
            subtitles = JSON.parse(result);
        });

    function fetch_next(start_idx) {
        console.log("Fetching from " + start_idx);
        fetch('https://youtubetts.herokuapp.com/10wavs/' + videoId + '&&' + start_idx)
            .catch(t => console.log(t));
        return start_idx + 9;
    }


    console.log(videoId);
    var current_time = null;
    var current_index = 0;
    var cur_seconds = 0;
    var last_generated = fetch_next(0);
    var audio_ended = true;
    let last_index = 0;
    setInterval(function () {
        var timeTracker = document.getElementsByClassName('ytp-time-current')[0];
        if (current_time !== timeTracker.innerHTML) {
            current_time = timeTracker.innerHTML;
            cur_seconds = Number(current_time.split(":")[0]) * 60 + Number(current_time.split(":")[1]);
        }
        if (subtitles != null && audio_ended) {
            var new_index = 0;
            while (new_index < subtitles.length
            && subtitles[new_index].start + subtitles[new_index].duration < cur_seconds)
            {
                new_index++;
            }
            console.log("Current fragment: " + new_index);

            if (new_index < current_index || new_index > current_index + 10) {
                current_index = new_index;
                last_generated = fetch_next(current_index)
            } else  if (new_index > current_index) {
                current_index++;
                if (current_index + 1 > last_generated) {
                    last_generated = fetch_next(current_index)
                }
            }


            if (current_index !== last_index) {
                console.log("Fragment " + current_index);
                console.log(subtitles[current_index]);
                console.log("Playing " + "https://youtubetts.herokuapp.com/wavs/" + videoId + "&&" + current_index);
                var myAudio = new Audio(
                    "https://youtubetts.herokuapp.com/wavs/" + videoId + "&&" + current_index
                );
                audio_ended = false;
                myAudio.addEventListener("ended", function(){
                    audio_ended = true;
                });
                myAudio.play();
                last_index = current_index;
            }
        }
    }, 100);
})();
