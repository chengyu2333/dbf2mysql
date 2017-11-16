source $HOME/.bashrc 
cd /home/user_test/dbf_sync
server=`ps aux | grep main.py | grep -v grep`
if [ ! "$server" ]; then
       nohup python3 main.py >> logs/nohup.log &
       echo "start sync     `date`"
fi
