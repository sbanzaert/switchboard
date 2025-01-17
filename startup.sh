#!/bin/bash
set -euf -o pipefail
set -x
PATH=/home/pi/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/local/games:/usr/games

LOGDIR="/home/pi/Python"
REPO_ROOT="/home/pi/Python/switchboard"

function kill_daemons {
    killall jackd && echo "killed jackd" || echo "jackd was not running"
    killall jack_wait && echo "killed jack_wait" || echo "jack_wait was not running"
    killall puredata && echo "killed puredata" || echo "puredata was not running"
    killall fluidsynth && echo "killed fluidsynth" || echo "fluidsynth was not running"
}

function clean_up {
    echo "Cleaning up!"
    kill_daemons
    python "$REPO_ROOT/statusLED.py" blue
    exit
}

# Kill everything if the script is terminated via real signal or exits on EXIT.
trap clean_up SIGHUP SIGINT SIGTERM EXIT
# Make sure we're starting fresh if something else weird happened.
kill_daemons

python "$REPO_ROOT/statusLED.py" cyan
export JACK_NO_AUDIO_RESERVATION=1
jackd -d alsa -d hw:Device 2>&1 | tee -a "$LOGDIR/jack.log" &
jack_wait -w

python "$REPO_ROOT/statusLED.py" orange
puredata -nogui -jack -jackname sw -nojackconnect -outchannels 1 "$REPO_ROOT/headphones/myfirstpd.pd" 2>&1 | tee -a "$LOGDIR/pd.log" &

python "$REPO_ROOT/statusLED.py" red
fluidsynth -i -s -g 0.6 -a jack -c 2 -z 64 -o synth.cpu-cores=4 -o synth.polyphony=128 /home/pi/Projects/MIDIsynth/Orpheus_18.06.2020.sf2 2>&1 | tee -a "$LOGDIR/fluidsynth.log" &

# https://askubuntu.com/questions/1153655/making-connections-in-jack-on-the-command-line
python "$REPO_ROOT/statusLED.py" violet
waited=0
found=false
while true; do
    echo "Waiting for 'sw' and 'fluidsynth'..."
    if jack_lsp | grep -q "sw" && jack_lsp | grep -q "fluidsynth"; then
        echo "puredata + fluidsynth running!";
        found=true
        break
    elif [[ "$waited" -gt 24 ]]; then # 2 minutes
        echo "Waited 2 minutes, no puredata + fluidsynth... :-("
        break
    fi
    waited=$((waited + 1))
    sleep 5
done
if [[ $found != true ]]; then
    clean_up
fi
jack_connect sw:output_1 system:playback_2
jack_connect fluidsynth:left system:playback_1

python "$REPO_ROOT/statusLED.py" green
python "$REPO_ROOT/tableTest.py"
