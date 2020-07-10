import threading, time


gecko = 'A'


def my_thread():
    global gecko
    time.sleep(10)
    gecko = 'B'
    print(gecko)


def run_thread():
    global gecko
    my_process = threading.Thread(target=my_thread)
    my_process.start()
    while gecko == 'A':
        print(gecko)
        time.sleep(1)
    my_process.join()


run_thread()

print('stopped')
