while true; do
        server=`ps aux | grep main.py | grep -v grep`
        if [ ! "$server" ]; then
            nohup python3 main.py >> logs/nohup.log &
            echo "start sync"
            sleep 10
        fi
        sleep 5
done
