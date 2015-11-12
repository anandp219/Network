killall python

# for (( i = 2; i < 6; i++ )); do
# 	echo "Spawning 127.0.0.$i"
# 	stdbuf -oL python m_recieve.py 127.0.0.$i > output/$i &
# 	sleep 1

# done

# i=2
# echo "Spawning 127.0.0.$i"
# stdbuf -oL python m_recieve.py 127.0.0.$i > output/$i &
# sleep 1
# i=5
# echo "Spawning 127.0.0.$i"
# stdbuf -oL python m_recieve.py 127.0.0.$i > output/$i &
# sleep 1
# i=4
# echo "Spawning 127.0.0.$i"
# stdbuf -oL python m_recieve.py 127.0.0.$i > output/$i &
# sleep 1
# i=3
# echo "Spawning 127.0.0.$i"
# stdbuf -oL python m_recieve.py 127.0.0.$i > output/$i &
# sleep 2
# i=6
# echo "Spawning 127.0.0.$i"
# stdbuf -oL python m_recieve.py 127.0.0.$i > output/$i &
# sleep 2




# i=4
# echo "Spawning 127.0.0.$i"
# stdbuf -oL python m_recieve.py 127.0.0.$i > output/$i &
# sleep 1
i=4
echo "Spawning 127.0.0.$i"
stdbuf -oL python m_recieve.py 127.0.0.$i > output/$i &
sleep 1
i=3
echo "Spawning 127.0.0.$i"
stdbuf -oL python m_recieve.py 127.0.0.$i > output/$i &
sleep 1
i=5
echo "Spawning 127.0.0.$i"
stdbuf -oL python m_recieve.py 127.0.0.$i > output/$i &
sleep 1
i=2
echo "Spawning 127.0.0.$i"
stdbuf -oL python m_recieve.py 127.0.0.$i > output/$i &
sleep 1
i=6
echo "Spawning 127.0.0.$i"
stdbuf -oL python m_recieve.py 127.0.0.$i > output/$i &
sleep 1
i=1
echo "Spawning 127.0.0.$i"
stdbuf -oL python m_recieve.py 127.0.0.$i > output/$i &
sleep 1
# i=9
# echo "Spawning 127.0.0.$i"
# stdbuf -oL python m_recieve.py 127.0.0.$i > output/$i &
# sleep 1
# i=8
# echo "Spawning 127.0.0.$i"
# stdbuf -oL python m_recieve.py 127.0.0.$i > output/$i &
# sleep 1
# i=11
# echo "Spawning 127.0.0.$i"
# stdbuf -oL python m_recieve.py 127.0.0.$i > output/$i &
# sleep 1
# i=10
# echo "Spawning 127.0.0.$i"
# stdbuf -oL python m_recieve.py 127.0.0.$i > output/$i &
# sleep 1
# i=12
# echo "Spawning 127.0.0.$i"
# stdbuf -oL python m_recieve.py 127.0.0.$i > output/$i &
# sleep 1
# i=7
# echo "Spawning 127.0.0.$i"
# stdbuf -oL python m_recieve.py 127.0.0.$i > output/$i &
# sleep 1
# for (( i = 20; i < 50; i++ )); do
# 	#statements
# 	echo "Spawning 127.0.0.$i"
# 	stdbuf -oL python m_recieve.py 127.0.0.$i > output/$i &
# 	sleep 1
# done
echo "Complete!"
