#!/usr/bin/env python
#Burak Aksoy
import rospy
import serial
from std_msgs.msg import Int32MultiArray
from geometry_msgs.msg import Twist
#bytesize=8,timeout=2, stopbits=serial.STOPBITS_ONE

def CRC(packet_data, sizeof_packet_data):#crc donusumu yapiyor
    crc16      = 0
    data       = 0
    size       = 0

    while size < sizeof_packet_data:

        data       = packet_data[size]^(crc16 & 0xFF)
        data       = data^(data << 4)
        data       = data&(0xFF)
        crc16      = (((data << 8) | ((crc16 & 0xFF00) >> 8)) ^ (data >> 4) ^ (data << 3))
        size       = size+1
    
    return crc16

def bit_packing_for_2_byte(number):#2 byte lik veriyi paketler yani su anda 255 e kadar desteklemektedir,2 byte tasimasi icin en kisa surede fonksiyon tekrar duzenlenecek
    a=number&255
    b=number>>8
    c=[0,0]
    c[0]=a
    c[1]=b
    return c


def bit_unpacking_for_2byte(array):#seri porttan gelen paketi alir eski haline cevirir
    x=array[0]
    y=array[1]
    return (y<<8)|x

def data_sender(data):
    steer_package   = [0,0]
    print "-----------"
    print "-----------"
    velocity        = int(data.linear.x)
    steer           = int(data.angular.z)
    """velocity        = speed_steer[0]
    steer           = speed_steer[1]"""
    will_send       = [0,0,0,0,0,0]
    print "Paketleme yapilmadan once hiz=",velocity
    print "Paketleme yapilmadan once steer=",steer
    steer_package   = bit_packing_for_2_byte(steer)#paketleme yapildi
    print 'crc olmadan steer_package:',steer_package
    
    crc_input       = [111,steer_package[0],steer_package[1],velocity]#111 isaretci oluyor
    hol             = len(crc_input)
    print 'crc_input:',crc_input
    crc_output      = CRC(crc_input,hol)
    print 'crc_output:',crc_output
    crc_packet      = bit_packing_for_2_byte(crc_output)#crc ciktisini paketliyoruz
    print 'crc_packet:',crc_packet


    will_send[0]    = 111#velocity isaretcisi
    will_send[1]    = steer_package[0]
    will_send[2]    = steer_package[1]
    will_send[3]    = velocity
    will_send[4]    = crc_packet[0]
    will_send[5]    = crc_packet[1]

    print 'gondermeden once basilan data=',will_send
    sender          = serial.Serial(port='/dev/ttyUSB0',baudrate=9600,stopbits=1,bytesize=8)#veriyi bastigimiz seri port
    """receive         = serial.Serial(port='/dev/tnt1',baudrate=9600,stopbits=1,bytesize=8)#veriyi cekecegimiz seri port
    """
    sender.write(will_send)               #burada veriyi seri porta gonderiyoruz
    """sent_data       = receive.read(size=6)#gonderdigim veriyi receive seri portundan okuyorum ve send_data adli dizi olusuyor
    
    sent_crc        = [0,0]
    sent_steer      = [0,0]
    sent_steer[0]   = ord(sent_data[1])                    
    sent_steer[1]   = ord(sent_data[2])                  #gonderdigim veri her ne kadar int olsa da string okunuyor,burada onu int e ceviriyorum
    velocity_result = ord(sent_data[3])                  #||
    sent_crc[0]     = ord(sent_data[4])
    sent_crc[1]     = ord(sent_data[5])


    crc_result      = bit_unpacking_for_2byte(sent_crc)
    steer_result    = bit_unpacking_for_2byte(sent_steer)#receive portundan aldigim paketi aciyorum
    print "-----------"
    print "Alinan datanin paketi aciliyor"
    print "-----------"
    print "Steer:",steer_result#paketten cikani ekrana yazdiriyorum ve test tamamlanmis oluyor.
    print     
    print "-----------"
    print "velocity:",velocity_result
    print  #||
    print "-----------"
    print "CRC:",crc_result
    print "-----------"
    print "Hello world"    #Test sorunsuz calisirsa hello world yazis cikiyor"""
    
def listener():

    rospy.init_node('UART_COMM', anonymous=True)

    rospy.Subscriber("steer_velocity", Twist, data_sender)

    rospy.spin()

if __name__ == '__main__':

	listener()
