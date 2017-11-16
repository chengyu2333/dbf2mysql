echo "restart sync"
pkill python3
nohup python3 main.py >> logs/nohup.log &
