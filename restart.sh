source $HOME/.bashrc
cd /home/user_test/dbf_sync
echo "restart sync"
pkill python3
nohup python3 run-process.py >> logs/nohup-process.log &
nohup python3 run-upload.py >> logs/nohup-upload.log &