#!/usr/bin/env python3

# 029 Puncher
# CDto029b.py (8-23-2025)
# By John Howard and Luca Severini (lucaseverini@mac.com)

import os
import serial
import time
import sys
import logging
import threading
from datetime import datetime

punching_stopped = threading.Event()
    
# Just for testing
# ------------------------------------------------------------------------------
def punch_file_test(file_path, range = None, punch_all = True, log = None):

    punching_stopped.clear()

    file_name = os.path.basename(file_path)
    
    # Emits the log
    def send_log(msg: str):
        print(msg)
        if log:
            try:
                log(msg)

            except Exception:
                pass
        
    start_row, end_row = range
    range_str = f"{start_row} to {end_row}"

    minutestamp = datetime.now().strftime('%H:%M:%S')
    send_log(f"{minutestamp} File to punch: {file_path}")
    send_log(f"{minutestamp} Rows to punch: {range_str} {'(all file)' if punch_all else ''}\n")
   
    rows_to_punch = end_row - start_row + 1
    line_counter = -1
    punch_counter = 0
    punch_aborted = False
    
    try:
        with open(file_path, 'r') as file:
            line_counter += 1
                        
            for line in file:
                if punching_stopped.is_set():
                    end_row = line_counter
                    punch_aborted = True
                    break
                     
                line_counter += 1
                
                if not punch_all:
                    if not (start_row <= line_counter <= end_row):
                        continue
                    
                msg = line
                msg = msg.encode('utf-8')
                # Send the data + line through the serial port
                # ser.write(msg)
                
                print(f"Message sent: {len(line)-1} data chars to punch:")
                print(f"{line}")
                
                minutestamp = datetime.now().strftime('%H:%M:%S')
                send_log(f"{minutestamp} Sent: {msg}")
                
                while True:
                    # Read a line from the 029 serial port check if it is the
                    # msg = ""
                    # msg = ser.readline()

                    # Simulate doing some work...
                    punching_stopped.wait(0.5)
                    
                    punch_counter += 1
                 
                    # Check if any data was received
                    if msg:
                        # Decode the received bytes to string (handle potential errors)
                        try:
                            msg = msg.decode('utf-8')       
                            print(f"Received message from keypunch:") 
                            print(f"{msg}")
                            
                            minutestamp = datetime.now().strftime('%H:%M:%S')
                            send_log(f"{minutestamp} Received msg = {msg}")                  
                            if "ERROR" in msg:
                                minutestamp = datetime.now().strftime('%H:%M:%S')
                                send_log(f"{minutestamp} Sent: msg = {msg}") 
                                print("Fatal error in keypunch. Program terminating")                        
                                sys.exit(0)       
                            break
                      
                        except UnicodeDecodeError:
                            send_log("Error decoding message")
                    else:
                        print("Timeout: No punch response received")
                        minutestamp = datetime.now().strftime('%H:%M:%S')
                        send_log(f"{minutestamp} Timeout no punch response received")
                            
    except FileNotFoundError:
        print("File not found")
    except PermissionError:
        print("Permission error")
    except OSError as e:
        print("OS error:", e)
        
    minutestamp = datetime.now().strftime('%H:%M:%S')
    
    range_str = f"{start_row} to {end_row}"

    report = f""
    
    if punch_aborted:
        send_log(f"{minutestamp} Punch interrupted.")
        report += f"Punch interrupted.\n"
    else:
        send_log(f"{minutestamp} Punch completed.")
        report += f"Punch completed.\n"
        
    if punch_counter != rows_to_punch or punch_all == False:
        send_log(f"{minutestamp} File punched partially.")
        report += f"File punched partially.\n"
 
    if punch_counter == rows_to_punch and punch_all == True:
        send_log(f"{minutestamp} File punched completely.")
        report += f"File punched completely.\n"
       
    send_log(f"{minutestamp} Rows punched: {range_str}\n")
    report += f"Rows punched: {range_str}."
       
    return report, punch_aborted, (start_row, end_row)
 
# Send the file to the Arduino line by line
# ------------------------------------------------------------------------------   
def punch_file(file_path, range = None, punch_all = True, log = None):
    # USB port D: home  line37   f; CHM
    # Configure the serial port (adjust as needed)
    usb_port = 'COM4'   # at CHM
    # usb_port = 'COM13' # at home
    # usb_port = "/dev/tty.usbserial-A50285BI" # for macOS
    baud_rate = 9600
    timeout = 60 # seconds
    
    punching_stopped.clear()

    msg = ""
    EOJmsg = ""
        
    log_dir = "LOGS"
    os.makedirs(log_dir, exist_ok = True)

    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    log_filename = os.path.join(log_dir, f"app_log_{timestamp}.log")
    logging.basicConfig(filename = log_filename, level = logging.INFO)
 
    # Emits the log
    def send_log(msg: str):
        logging.info(msg)
        if log:
            try:
                log(msg)

            except Exception:
                pass
 
    # d: at home  e: at chm
    if not file_path:
        punch_all = True
        file_path = input("Please enter the name of the file you want to punch: ")
        if not file_path:
            print("No file to punch.")
            sys.exit(0) 
    
    start_row, end_row = range
    range_str = f"{start_row} to {end_row}"

    print(f"Log to file: {os.path.basename(log_filename)}\n")    
    print("File to punch: {file_path}")    
    print("Rows to punch: {range_str} {'(all file)' if punch_all else ''}")
 
    minutestamp = datetime.now().strftime('%H:%M:%S')
    
    send_log(f"{minutestamp} Log to file: {os.path.basename(log_filename)}")
    send_log(f"{minutestamp} File to punch: {file_path}")   
    send_log(f"{minutestamp} Rows to punch: {range_str} {'(all rows)' if punch_all else ''}\n")   
  
    punch_aborted = False
 
    try:
        # Open the serial port to the 029 arudino
        ser = serial.Serial(usb_port, baud_rate)
        print(f"Connected to {usb_port} at {baud_rate} baud")
        
        # send the start command to the 029 arduino and print the response    
        ser.write("start   \n".encode('utf-8'))
        print(f"{timestamp} Sent: Start command")
        minutestamp = datetime.now().strftime('%H:%M:%S') 
        send_log(f"{minutestamp} Sent: Start command")   
        msg=""
        
        while True:
            # Read a line from the serial port  the start  command response
            msg = ser.readline()

            # Check if any data was received
            if msg:
                # Decode the received bytes to string (handle potential errors)
                try:
                    data = msg.decode('utf-8')             
                    print("Started Arduino program:",data)
                    minutestamp = datetime.now().strftime('%H:%M:%S')
                    send_log(f"{minutestamp} Received: {data} ")   
                    break
                except UnicodeDecodeError:
                    print("Error decoding data")
                    
            else:
                print("Timeout: No data received")
                     
        rows_to_punch = end_row - start_row + 1
        line_counter = -1
        punch_counter = 0

        try:
            with open(file_path, 'r') as file:
                
                line_counter += 1
                
                for line in file:
                    if punching_stopped.is_set():
                        end_row = line_counter
                        punch_aborted = True
                        break

                    line_counter += 1
                    
                    if not punch_all:
                        if not (start_row <= line_counter <= end_row):
                            continue

                    msg = "data" + line
                    msg = msg.encode('utf-8')
                    # Send the data + line through the serial port
                    ser.write(msg)
                    
                    print(f"Message sent: {len(line)-1} data chars to punch:")
                    print(f"{line.strip()}")
                    minutestamp = datetime.now().strftime('%H:%M:%S')
                    send_log(f"{minutestamp} Sent: {line.strip()}")
                    
                    while True:
                        # Read a line from the 029 serial port
                        msg = ser.readline()
                     
                        # Check if any data was received
                        if msg:
                            # Decode the received bytes to string (handle potential errors)
                            try:
                                msg = msg.decode('utf-8')       
                                print(f"Received message:") 
                                print(f"{msg}")
                                
                                minutestamp = datetime.now().strftime('%H:%M:%S')
                                send_log(f"{minutestamp} Received: {msg}")                  
                                if "ERROR" in msg:
                                    minutestamp = datetime.now().strftime('%H:%M:%S')
                                    send_log(f"{minutestamp} Sent: {msg}")  
                                    print("fatal error in keypunch program terminating")                        
                                    sys.exit(0)       
                                break
                          
                            except UnicodeDecodeError:
                                print("Error decoding data")
                        else:
                            print("Timeout: No punch responce received")
                            minutestamp = datetime.now().strftime('%H:%M:%S')
                            send_log(f"{minutestamp} Timeout no response from punch received")
                            
        except FileNotFoundError:
            print("File not found")
        except PermissionError:
            print("Permission error")
        except OSError as e:
            print("OS error:", e)
            
        # if file was not empty
        if line_counter > 0:
            if punch_aborted:
                print("File punching interrupted.")
            else:
                print("File punching complete.") 
      
            # end of file send eoj to 029
            ser.write("eoj\n".encode('utf-8'))  
            
            print("Sent EOJ.")
            
            minutestamp = datetime.now().strftime('%H:%M:%S')
            send_log(f"{minutestamp} Sent EOJ.") 
     
            # Check EOJ response
            while True:
                # Read a line from the serial port check if it is the
                eojMsg = ser.readline()

                # Check if any data was received
                if eojMsg:
                    # Decode the received bytes to string (handle potential errors)
                    try:
                        eojStr = eojMsg.decode('utf-8').strip()
                        
                        print(f"Received EOJ response: {eojStr}")
                        
                        minutestamp = datetime.now().strftime('%H:%M:%S')
                        send_log(f"{minutestamp} Received EOJ response: {eojStr}\n")  
                        break
                        
                    except UnicodeDecodeError:
                        print("Error decoding EOJ response")
                        
                        minutestamp = datetime.now().strftime('%H:%M:%S')
                        send_log(f"{minutestamp} Error decoding EOJ response.\n")
                else:
                    print("Timeout: No EOJ response received")   
                        
                    minutestamp = datetime.now().strftime('%H:%M:%S')
                    send_log(f"{minutestamp} Timeout: No EOJ response received.\n")
                    
        elif line_counter == 0:
            print("File is empty")
            
            minutestamp = datetime.now().strftime('%H:%M:%S')
            send_log(f"{minutestamp} File is empty.\n")
     
    except serial.SerialException as e:
        print(f"Error: Could not open serial port: {e}")
    except FileNotFoundError:
        print("Error: Text file not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    finally:
        minutestamp = datetime.now().strftime('%H:%M:%S')
        send_log(f"{minutestamp} Closing ports and exiting.")
        
        # Ensure the serial port is closed
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Serial port closed.")
            
    minutestamp = datetime.now().strftime('%H:%M:%S')

    range_str = f"{start_row} to {end_row}"

    report = f""

    if punch_aborted:
        send_log(f"{minutestamp} Punch interrupted.")
        report += f"Punch interrupted.\n"
    else:
        send_log(f"{minutestamp} Punch completed.")
        report += f"Punch completed.\n"
    
    if punch_counter != rows_to_punch or punch_all == False:
        send_log(f"{minutestamp} File punched partially.")
        report += f"File punched partially.\n"

    if punch_counter == rows_to_punch and punch_all == True:
        send_log(f"{minutestamp} File punched completely.")
        report += f"File punched completely.\n"
   
    send_log(f"{minutestamp} Rows punched: {range_str}\n")
    report += f"Rows punched: {range_str}."
         
    for h in logging.getLogger().handlers[:]:
            if isinstance(h, logging.FileHandler):
                h.close()
                logging.getLogger().removeHandler(h)
    
    return report, punch_aborted, (start_row, end_row)
    
if __name__ == "__main__":
    try:
        file = ""
        
        if len(sys.argv) == 2:
            file = sys.argv[1]

        punch_file(file)
        
        sys.exit(0)
        
    except KeyboardInterrupt:
        print("\nProgram Interrupted.")
        sys.exit(1)
            