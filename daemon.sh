source $HOME/.bashrc
cd /home/user_test/dbf_sync3
while true; do
    server=`ps aux | grep run-process.py | grep -v grep`
    if [ ! "$server" ]; then
           nohup python3 run-process.py >> logs/nohup-process.log &
           echo "start process     `date`"
    fi
    server=`ps aux | grep run-upload.py | grep -v grep`
    if [ ! "$server" ]; then
           nohup python3 run-upload.py >> logs/nohup-upload.log &
           echo "start upload     `date`"
    fi
    sleep 10
done
