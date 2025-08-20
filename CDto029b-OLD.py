
  # verson b July 14 add logging
import serial
import time
import sys
import logging
from datetime import datetime
# USB port D: home  line37   f; CHM
# Configure the serial port (adjust as needed)
usb_port = 'COM4'  # at CHM  9600 baud
#usb_port = 'COM13'   # at home
baud_rate = 9600
timeout =60        #seconds
msg=""
EOJmsg=""
timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
log_filename = f'app_log_{timestamp}.log'
logging.basicConfig(filename=log_filename, level=logging.INFO)
logging.info("Log with a timestamped filename,each entry prefied with %M:%S minute stamp")
print(f"{timestamp} log file setup {log_filename}") 
try:
    # Open the serial port to the 029 arudino
    ser = serial.Serial(usb_port, baud_rate)
    print(f"Connected to {usb_port} at {baud_rate} baud")
    
# send the start command to the 029 arduino and print the response    
    ser.write("start   \n".encode('utf-8'))
    print(f"{timestamp} Sent: start command")
    minutestamp = datetime.now().strftime('%M:%S') 
    logging.info(f"{minutestamp} Sent: start command")   
    msg=""
    while True:
        # Read a line from the serial port  the start  command response
        msg = ser.readline()

        # Check if any data was received
        if msg:
        # Decode the received bytes to string (handle potential errors)
            try:
              data = msg.decode('utf-8')             
              print("Started program version ",data)
              minutestamp = datetime.now().strftime('%M:%S')
              logging.info(f"{minutestamp} Received msg= {data} ")   
              break
            except UnicodeDecodeError:
              print("Error decoding data")
        else:
          print("Timeout: No data received")
 
# d: at home  e: at chm
    file_name = input("Please enter the name of the file you want to punch: ")
    minutestamp = datetime.now().strftime('%M:%S')
    logging.info(f"{minutestamp} punching file {file_name} ")
    print(file_name)
    try:
        with open(file_name, 'r') as file:
            for line in file:
                msg = "data"+line
                msg= msg.encode('utf-8')
                # Send the data + line through the serial port
                ser.write(msg)
                print(f"message sent:{len(line)-1} data chars to punch = {line}")
                minutestamp = datetime.now().strftime('%M:%S')
                logging.info(f"{minutestamp} Sent: {msg}")   
                while True:
                # Read a line from the 029 serial port check if it is the
                  msg =""
                  msg = ser.readline()
                 
                # Check if any data was received
                  if msg:
                # Decode the received bytes to string (handle potential errors)
                    try:
                      msg = msg.decode('utf-8')       
                      print(f"Received message from keypunch: {msg}") 
                      minutestamp = datetime.now().strftime('%M:%S')
                      logging.info(f"{minutestamp} Received  msg= {msg}")                  
                      if "ERROR" in msg:
                        minutestamp = datetime.now().strftime('%M:%S')
                        logging.info(f"{minutestamp} Sent:  msg= {msg}")  
                        print("fatal error in keypunch program terminating")                        
                        sys.exit(0)       
                      break
                      
                    except UnicodeDecodeError:
                      print("Error decoding data")
                  else:
                    print("Timeout: No punch responce received")
                    minutestamp = datetime.now().strftime('%M:%S')
                    logging.info(f"{minutestamp} Timeout no response from punch received") 
    except FileNotFoundError:
        print("File not found: ", file_name)
    except PermissionError:
        print("Permission denied for file: ", file_name)
    except OSError as e:
        print("OS error:", e)
        
# end of file send eoj to 029
    ser.write("eoj\n".encode('utf-8') )        
    print("File transfer complete. Sent eoj")
    minutestamp = datetime.now().strftime('%M:%S')
    logging.info(f"{minutestamp} File transfer complete. Sent eoj") 
                
    while True:
      # Read a line from the serial port check if it is the
      EOJmsg=""
      EOJmsg  = ser.readline()

    # Check if any data was received
      if EOJmsg:
          # Decode the received bytes to string (handle potential errors)
          try:
            EOJmsg = EOJmsg.decode('utf-8').strip()            
            print(f"Received eoj response:  {EOJmsg}")
            minutestamp = datetime.now().strftime('%M:%S')
            logging.info(f"{minutestamp} Received eoj response: msg= {EOJmsg}")  
            break
          except UnicodeDecodeError:
           print("Error decoding data")
      else:
        print("Timeout: No data received")   
            
            

   


except serial.SerialException as e:
    print(f"Error: Could not open serial port: {e}")
except FileNotFoundError:
    print("Error: Text file not found.")
except Exception as e:
     print(f"An unexpected error occurred: {e}")
finally:
    # Ensure the serial port is closed
    # print('Finally is executed!')
    minutestamp = datetime.now().strftime('%M:%S')
    logging.info(f"{minutestamp} Python Function finally: is  closing ports and exiting")  
    if 'ser' in locals() and ser.is_open:
        ser.close()
        print("Serial port closed.")
