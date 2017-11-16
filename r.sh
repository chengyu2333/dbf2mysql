        server=`ps aux | grep main.py | grep -v grep`
        if [ ! "$server" ]; then
            nohup /home/user_test/python3/bin/python3 /home/user_test/dbf_sync/main.py >> /home/user_test/dbf_sync/logs/nohup.log &
            echo "start sync `date`"
        fi
