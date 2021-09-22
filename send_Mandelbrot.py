import os
import datetime
import time
import re
import pika
import paramiko

IMAGE_PRECISION = 1000

def generateImageSequence():
    return generateImageSequence_SpecificPoint2()

def generateImageSequence_Classic():
    ## Compute the images to build at various zoom level
    # This is where to input all the logic of going through a beautifull patch in Mandelbrot Set
    xmin = -2
    xmax = 1
    ymin = -1.5
    ymax = 1.5

    #pas = 0.000001 <- on ne voit pas le mouvement
    #pas = 0.0001 <- on ne voit pas le mouvement
    pas = 0.001
    aSequence = []
    for i in range (120):
        aSequence.append([xmin+i*pas, xmax-i*pas, ymin+i*pas, ymax-i*pas])
    return aSequence

def generateImageSequence_SpecificPoint1():
    ## Compute the images to build at various zoom level
    # This is where to input all the logic of going through a beautifull patch in Mandelbrot Set
    ## Alternative (from XaoS) is to get center and height / width
    x0 = -1.158315616523
    y0 = -0.299125353268
    xrange = 0.000960151758
    yrange = 0.000960151758
    xmin = x0 - xrange/2
    xmax = x0 + xrange/2
    ymin = y0 - yrange/2
    ymax = y0 + yrange/2

    #pas = 0.000001 <- on ne voit pas le mouvement
    #pas = 0.0001 <- on ne voit pas le mouvement
    pas = -0.0001
    aSequence = []
    for i in range (120):
        aSequence.append([xmin+i*pas, xmax-i*pas, ymin+i*pas, ymax-i*pas])
    return aSequence

def generateImageSequence_SpecificPoint2():
    ## Compute the images to build at various zoom level
    # This is where to input all the logic of going through a beautifull patch in Mandelbrot Set
    ## Alternative (from XaoS) is to get center and height / width
    x0 = -1.158315616523
    y0 = -0.299125353268
    xrange = 0.000960151758
    yrange = 0.000960151758
    xmin = x0 - xrange/2
    xmax = x0 + xrange/2
    ymin = y0 - yrange/2
    ymax = y0 + yrange/2

    #Zooming Out at each iteration
    ratio = 1.1
    aSequence = []
    i = 0
    while (ratio**i)*xrange < 3:
        aSequence.append([x0 - (ratio**i)*xrange/2, x0 + (ratio**i)*xrange/2, y0 - (ratio**i)*yrange/2, y0 + (ratio**i)*yrange/2])
        i += 1
    return aSequence








###################################
## MAIN PROGRAM ###################
###################################




## Create Taskid
uid = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
targetDirectory = "/media/BIGDATA/MandelbrotImages/{0}".format(uid)
print("Uniq id created:{0}".format(uid))


## Prepare Directory on File server side to receive images
host = "garage.local"
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname = host)
sftp = ssh.open_sftp()
sftp.mkdir(path=targetDirectory)
#lines = sftp.listdir(path="/media/BIGDATA/MandelbrotImages")
#print(lines)
ssh.close()

## call the function that generate the sequence of images to build
aSequence = []
aSequence = generateImageSequence()

## Queue the job to the RabbitMq instance to distribute the load
credentials = pika.PlainCredentials('mandelbrot', 'benoit')
connection = pika.BlockingConnection(pika.ConnectionParameters(host='garage.local',virtual_host='MandelbrotGenerator',credentials=credentials))

channel = connection.channel()

#Emergency commend for queue cleanup
channel.queue_purge(queue='task')

q = channel.queue_declare(queue='task')
i = 0
for l in aSequence:
    body='Message '+str(i)
    body="Mandelbrot {xmin} {xmax} {ymin} {ymax} {nbPixel} {nbPixel} {sequence:06}-mset.bmp|{targetDir}".format(xmin = l[0], xmax = l[1], ymin = l[2], ymax = l[3], nbPixel = IMAGE_PRECISION, sequence = i, targetDir = targetDirectory)
    channel.basic_publish(exchange='',
                        routing_key='task',
                        body=body)
    #print(" [x] Sent job {0}".format(i))
    i+=1
print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S : ")+"{0} jobs queued".format(i))

## Poll the job queue to detect completion 
q = channel.queue_declare(queue='task', passive=True)
q_len = q.method.message_count
while q_len>0:
    q = channel.queue_declare(queue='task', passive=True)
    q_len = q.method.message_count
    time.sleep(1)
    #print("Queue Size is {0}".format(q_len))
connection.close()
#Workaround to make sure we have all images generated and pushed before generating the video
print (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S : ")+"Queue has been worked out")
time.sleep(30)

## Submit the video construction job or Build it directly, check completion, a bit of cleanup if required
command = "cd {0} && ffmpeg -framerate 25 -i %06d-mset.jpg -c:v libx264 -profile:v high -crf 20 -pix_fmt yuv420p output.mp4".format(targetDirectory)
#command = "ls {0}/*mp4".format(targetDirectory)
ssh2 = paramiko.SSHClient()
ssh2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh2.connect(hostname = host)
stdin, stdout, stderr = ssh2.exec_command(command)
print(command)
print(stdout.readlines())
print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S : ")+"Movie generated")

## Server side check and possible cleanup of the directory if no file
command = "ls {0}".format(targetDirectory)
stdin, stdout, stderr = ssh2.exec_command(command)
lines = stdout.readlines()
image = 0
for f in lines:
    aFile = f.strip()
    #print(aFile)
    if re.match(".*\.bmp", aFile):
        image+=1
    if re.match(".*\.jpg", aFile):
        image+=1
    if re.match(".*\.mp4", aFile):
        print("1 video file generated: {0} from {1} image(s)".format(aFile, image))
        ## Retrieve the video
        aLocalPath = "./output.mp4"
        aRemotePath = "{0}/output.mp4".format(targetDirectory)
        try:
            os.remove(aLocalPath)
        except:
            print("File not found")
        host = "garage.local"
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname = host)
        sftp = ssh.open_sftp()
        sftp.get(remotepath=aRemotePath, localpath=aLocalPath)
        ssh.close()
        os.system("vlc ./output.mp4")
if not lines:
    command = "rmdir {0}".format(targetDirectory)
    ssh2.exec_command(command)
    print("No image file generated, cleaning up directory")


#Workaround to avoid unexpected exception when closing the ssh connection
time.sleep(5)

try:
    ssh2.close()
except:
    print("Unexpected error:", sys.exc_info()[0])


