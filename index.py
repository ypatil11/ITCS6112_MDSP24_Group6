import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time
import pymysql 
import smtplib
import ssl
import logging
from datetime import datetime
from email.message import EmailMessage
from cachetools import TTLCache

conn = None

# Ten minute Cache
cache = TTLCache(maxsize=1000, ttl=600)

logging.basicConfig(level=logging.NOTSET)



def get_db_cursor():
    global conn
    conn = pymysql.connect( 
        host='localhost', 
        user='root',  
        password = "password", 
        db='moviemate',
        cursorclass=pymysql.cursors.DictCursor
    ) 
    cur = conn.cursor()
    return cur
    
def close_db_connecion():
    global conn
    if conn:
        conn.commit()
        conn.close() 
    
  
def get_all_preferences(): 
    # To connect MySQL database       
    cur = get_db_cursor() 
    cur.execute("SELECT * FROM base_moviepreferences WHERE is_processed=0")
    all_preferences = cur.fetchall()
    for preference in all_preferences:
        cur.execute(f"SELECT * FROM base_seatpreferences WHERE preference_id = {preference["id"]}")
        preference["seat_preferences"] = cur.fetchall()
      
    # To close the connection 
    close_db_connecion() 
    return all_preferences

def mark_preference_done(preference): 
    # To connect MySQL database       
    cur = get_db_cursor()
    cur.execute(f"UPDATE base_moviepreferences SET is_processed=1 WHERE id={preference['id']}")
      
    # To close the connection 
    close_db_connecion() 

def send_mail(preference, payment_url):     
    cur = get_db_cursor() 
    cur.execute(f"SELECT * FROM auth_user WHERE id = {preference['user_id']}")
    userdata = cur.fetchall()[0]
       
    port = 465  # For SSL
    context = ssl.create_default_context()
    
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login("moviematebot@gmail.com", "khsn rssi rurx jwof")
        
        
        msg = EmailMessage()
        msg['Subject'] = "Reserved Tickets - MovieMate"
        msg['From'] = "moviematebot@gmail.com"
        msg['To'] = userdata["email"]
        msg.set_content(f"""\
            Subject: Hi there

            Payment URL for movie - {preference["movie_name"]} is : {payment_url}""")
        
        server.send_message(msg)
        server.close()
        
    close_db_connecion()


def reserve_tickets(preferences):
    #### RESERVE TICKETS
    for preference in preferences:
        logging.info(datetime.now().strftime("%Y/%m/%d %H:%M:%S") + ":: Processing Preference: " + str(preference) + " --------------------------")
        try:
            cinema_list_url = f"https://in.bookmyshow.com/{preference["city"]}/cinemas"
            driver = uc.Chrome()
            driver.get(cinema_list_url)

            # GO THROUGH CINEMAS URL INSTEAD OF BUILDING COMPLETE URL (https://in.bookmyshow.com/hyderabad/cinemas)
            driver.find_element(By.XPATH, f"//li//child::div//child::span[contains(text(),'{preference["city"]}')]").click()
            time.sleep(1)
            
            driver.find_element(By.XPATH, f"//div//div//div//div//div//div//div//div//div//div[contains(text(),'{preference["cinema_name"]}')]").click()
            # driver.find_element(By.XPATH, "//div//div//div//div//div//div//div//div//div//div[contains(text(),'AMB')]").click()
            driver.get(driver.current_url[:-8] + preference["date"].strftime("%Y%m%d"))

            shows = driver.find_elements(By.XPATH, f"//li[contains(., '{preference["movie_name"]}')]//descendant::a[@class='showtime-pill data-enabled']//div[@class='__text']")
            time.sleep(8)
            driver.find_element(By.XPATH, "//button[@id='wzrk-cancel']").click()
            
            time.sleep(3)
            for show in shows: 
                show_time_text = show.text
                show_time = int(show_time_text[0:2]) * 100 + int(show_time_text[3:5])
                if (show_time_text[6:] == "PM"):
                    show_time += 1200
                
                if show_time >= preference["time_from"] and show_time <= preference["time_to"]:
                    time.sleep(6)
                    show.click()
                    break

            # # clicks accept on popup
            # time.sleep(3)
            # driver.find_element(By.XPATH, "//div[@id='btnPopupAccept']").click()


            time.sleep(3)
            driver.find_element(By.XPATH, f"//li[contains(@id,'pop_{preference["number_of_seats"]}')]").click()
            time.sleep(3)
            driver.find_element(By.XPATH, "//div[@id='proceed-Qty']").click()

            time.sleep(1)

            available_seats = driver.find_elements(By.XPATH, "//div[a[contains(@class , '_available')]]")
            available_seats[6].click()
            
            start_row = 0
            start_column = 0
            end_row = 99
            end_column = 99

            for seat_preference in preference["seat_preferences"]:
                if seat_preference["is_included"]:
                    end_row = seat_preference["number_of_rows_top"] if seat_preference["number_of_rows_top"] else 99
                    end_column = seat_preference["number_of_rows_left"] if seat_preference["number_of_rows_left"] else 99
                else:
                    start_row = seat_preference["number_of_rows_top"] if seat_preference["number_of_rows_top"] else 0
                    start_column = seat_preference["number_of_rows_left"] if seat_preference["number_of_rows_left"] else 0

            for seat in available_seats:
                seat_id = seat.get_attribute('id').split("_")
                if int(seat_id[1]) > start_row and int(seat_id[1]) < end_row \
                    and int(seat_id[2][2:]) > start_column and int(seat_id[2][2:]) < end_column:
                    seat.click()
                    if (len(driver.find_elements(By.XPATH, "//div[a[contains(@class , '_selected')]]"))) == preference["number_of_seats"]:
                        break
                    else:
                        continue
            
            time.sleep(4)
            driver.execute_script('fnBookTickets();')
            
            # clicks accept on popup
            time.sleep(4)
            driver.find_element(By.XPATH, "//div[@id='btnPopupAccept']").click()
        
            time.sleep(4)
            driver.execute_script('fnPrePay();')
            
            time.sleep(4)
            payment_url = driver.current_url
            try:
                send_mail(preference, payment_url)
                logging.info(datetime.now().strftime("%Y/%m/%d %H:%M:%S") + ":: Mail Sent :")
            except Exception as e:
                logging.error( datetime.now().strftime("%Y/%m/%d %H:%M:%S") + ":: Error in sending mail : " + str(e))
                raise e
        except Exception as e:
            logging.error( datetime.now().strftime("%Y/%m/%d %H:%M:%S") + ":: Exception : " + str(e))
        else:
            mark_preference_done(preference)
            logging.info(datetime.now().strftime("%Y/%m/%d %H:%M:%S") + ":: Marking preference as processed :")
        
        ## Remove the following line for complete execution    
        time.sleep(1000)
        driver.close()


# Runs Every 5 Minutes
while(True):
    logging.info("============================ Script Execution Started: " + datetime.now().strftime("%Y/%m/%d %H:%M:%S") + " ============================")
    preferences = get_all_preferences()
    logging.info( datetime.now().strftime("%Y/%m/%d %H:%M:%S") + ":: All Preferences : " + str(preferences))
    reserve_tickets(preferences)
    time.sleep(300)