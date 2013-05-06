#!/bin/sh -e
stop() {
    kill $PID
    echo ">>> Stopped <<<"
}
trap stop INT ABRT EXIT
./main.py "$@" >>executor.log 2>&1 </dev/null & PID=$!
echo ">>> Started <<<"
tail -f executor.log