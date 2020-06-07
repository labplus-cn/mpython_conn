from mpython_conn import controller
import matplotlib.pyplot as plt
import time

m = controller()

def a_down():
    print("Start collection...")
    result = []
    for count in range(100):
        result.append(m.get_light())
        time.sleep(0.1)
        print( '\rData : [{}/100]'.format(count + 1), end='')
    plt.plot( result, label="light" )
    plt.legend()
    plt.show()

m.on_a_pressed = a_down
print("Press A button to start.")
