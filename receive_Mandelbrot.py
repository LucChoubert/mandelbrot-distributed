## REquires to install on the machine
# imagemagick
# mandelbrot (From Luc Choubert)

import pika, sys, os, time
from random import randrange
import paramiko

class TimerError(Exception):
    """A custom exception used to report errors in use of Timer class"""


class Timer:
    def __init__(self):
        self._start_time = None
        self._stop_time = None


    def start(self):
        """Start a new timer"""
        if self._start_time is not None:
            raise TimerError(f"Timer is running. Use .stop() to stop it")
        self._stop_time = None
        self._start_time = time.perf_counter()


    def stop(self):
        """Stop the timer, and report the elapsed time"""
        if self._start_time is None:
            raise TimerError(f"Timer is not running. Use .start() to start it")
        self._stop_time = time.perf_counter()

    def __str__(self):
        elapsed_time = self._stop_time - self._start_time
        self._start_time = None
        self._stop_time = None
        return "Elapsed time: {elapsed_time:0.4f} seconds"

    def getElapsed_time(self):
        elapsed_time = self._stop_time - self._start_time
        self._start_time = None
        self._stop_time = None
        return elapsed_time

def main():
    ## Connect to the Job Queue RabbitMq instance to 
    credentials = pika.PlainCredentials('mandelbrot', 'benoit')
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='garage.local',virtual_host='MandelbrotGenerator',credentials=credentials))
    channel = connection.channel()

    channel.queue_declare(queue='task')

    def callback(ch, method, properties, body):
        ## Decode the task received
        taskMandelbrot, targetDirectory = body.decode().split('|')
        print("[x] Received {}".format(body.decode()))

        ## Run the task received, a Mandelbrot generation
        t = Timer()
        t.start()
        # Adding the hardcoded path as a workaround. TOBEREMOVED
        aReturnCodeMandelbrot = os.waitstatus_to_exitcode(os.system("nice -10 /home/luc/.local/bin/"+taskMandelbrot))
        #aReturnCodeMandelbrot = os.WEXITSTATUS(os.system(taskMandelbrot))
        t.stop()
        processing_time = t.getElapsed_time()
        
        ## Convert the .bmp file into .jog file if mogrify exists
        ## Another way could be via python itself and PIL module
        imageFile = taskMandelbrot.split(' ')[7].split('.')[0]
        taskConvertion = "nice -10 convert {0}.bmp {0}.jpg && rm -f {0}.bmp".format(imageFile)
        aReturnCodeConvertion = os.waitstatus_to_exitcode(os.system(taskConvertion))
        
        ## Send the resulting image file to the storage server and remove it locally
        host = "garage.local"
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname = host)
        sftp = ssh.open_sftp()
        aLocalPath = "./{0}.jpg".format(imageFile)
        aRemotePath = "{0}/{1}.jpg".format(targetDirectory, imageFile)
        sftp.put(localpath=aLocalPath, remotepath=aRemotePath)
        ssh.close()
        os.remove(aLocalPath)

        ## Successfully dequeue the task from the job Queue 
        if aReturnCodeMandelbrot == 0 and aReturnCodeConvertion == 0:
            ch.basic_ack(delivery_tag = method.delivery_tag)

        ## Report status
        print("-->Processed in {0:.1f} seconds with RC_Mandelbrot={1} and RC_Convertion={2}".format(processing_time, aReturnCodeMandelbrot, aReturnCodeConvertion))

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='task', on_message_callback=callback)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
