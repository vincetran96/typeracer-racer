import time
from itertools import islice
from random import randint, uniform
import argparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By


def random_chunk(st: str, min_chunk=1, max_chunk=8):
    '''Creates random chunks of a string
    
    :params:
        @st: string
        @min_chunk: minimum length of a chunk
        @max_chunk: maximum length of a chunk
    '''
    
    it = iter(st)
    while True:
        nxt = "".join(list(islice(it,randint(min_chunk, max_chunk))))
        if nxt:
            yield nxt
        else:
            break


# Create the arg parser
arg_parser = argparse.ArgumentParser(
    prog="python start.py",
    description="Start TypeRacer Racer"
)

# Add the arguments
arg_parser.add_argument(
    'wpm',
    metavar='wpm',
    type=int,
    help="Desired words per minute"
)

arg_parser.add_argument(
    'chromedriver',
    metavar='chromedriver',
    type=str,
    help="Location of the chromedriver (e.g., ./drivers/chromedriver)"
)

# Execute the parse_args() method
args = arg_parser.parse_args()
WPM = args.wpm
CHROMEDRIVER_PATH = args.chromedriver

TYPERACER = "https://play.typeracer.com/"
MAX_CHUNK_WAITTIME = 0.25
SPW = 60 / WPM # Seconds per word
DEFAULT_CHAR_INPUT_TIME = 0.03 # Time it takes to input a char in seconds

# Chrome things
chrome_service = Service(executable_path=CHROMEDRIVER_PATH)
chrome_options = Options()
chrome_options.add_argument("--remote-debugging-port=9222")
driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
driver.get(TYPERACER)

while True:
    time.sleep(0.01)
    try:
        race_btn_xpath = '//*[@id="gwt-uid-1"]/a'
        # race_btn_xpath = "(//div[@class='mainMenu']/table/descendant::tr)[2]/descendant::*[@class='gwt-Anchor']"
        driver.find_element(by=By.XPATH, value=race_btn_xpath).click()
        break
    except:
        print("CAN'T FIND RACE BUTTON\n")

while True:
    time.sleep(0.01)
    try:
        input_panel_xpath = "//div[@class='mainViewport']/descendant::table[@class='inputPanel']"
        spans_xpath = "/descendant::span"
        spans = driver.find_elements(by=By.XPATH, value=input_panel_xpath + spans_xpath)
        s0, s1 = spans[0].text, spans[1].text
        print("===" + s0 + "===")
        print("===" + s1 + "===")
        if len(spans) == 2:
            text = s0.strip() + " " + s1.rstrip()
        if len(spans) == 3:
           text = s0.strip() + s1.rstrip() + " " + spans[2].text.strip()
        print(f"Text:\n{text}\n")
        
        # Need a dynamic way to calculate wait time between words
        # Because TypeRacer calculates WPM based on the # of words typed divided by the elapsed time
        num_words = len(text.split(" "))
        num_chars = len(text)
        total_time = SPW * (num_words) # In seconds

        # Inputing a char can even take some time, so now we have to subtract that time from the total_time to calculate the wait time between chars
        char_wait_time = \
            (total_time - num_chars * DEFAULT_CHAR_INPUT_TIME) / (num_chars - 1) # In seconds
        print(f"Number of words in text: {num_words}")
        print(f"Target words per minute: {WPM}")
        print(f"Estimated complete time in seconds: {total_time}")
        print(f"Number of chars in text: {num_chars}")
        print(f"Estimated char wait time: {char_wait_time}")
        break
    except Exception as exc:
        print(f"CAN'T FIND INPUT PANEL WITH EXCEPTION:\n{exc}\n")

time.sleep(11) # Wait for countdown
c_total_time = 0 # Total time spent on inputing characters (in seconds)
total_time_remaining = total_time # Total time remaining from this point (in seconds)
while True:
    time.sleep(0.01)
    try:
        txtInput_xpath = "/descendant::input[contains(@class, 'txtInput')]"
        txtInput=driver.find_element_by_xpath(input_panel_xpath+txtInput_xpath)
        
        # Randomize the whole text into a # of fragmented strings
        # for s in random_chunk(text, max_chunk=3):
        #     print(s)
        #     txtInput.send_keys(s)
        #     time.sleep(uniform(0, MAX_CHUNK_WAITTIME))

        # Type according to desired WPM
        start = time.time()
        for idx, c in enumerate(text):
            c_start = time.time()
            txtInput.send_keys(c)
            c_end = time.time()
            c_time = c_end - c_start
            c_total_time += c_time # add time to total char time
            print(f"{c} took {c_time} seconds")
            total_time_remaining -= c_time
            
            # Calculate the total time remaining
            # and number of chars remaining so we can re-calculate the char wait time
            if idx < num_chars - 2:
                num_chars_remaining = len(text[idx+1:])
                a = max(total_time_remaining - num_chars_remaining * c_time, 0)
                b = (num_chars_remaining - 1)
                char_wait_time = a / b
                
                print(f"Total time remaining: {total_time_remaining}")
                print(f"Num chars remaining: {num_chars_remaining}")
                print(f"New char wait time: {char_wait_time}")
            
            time.sleep(char_wait_time)
            total_time_remaining -= char_wait_time
        break
    except Exception as exc:
        print(f"CAN'T TYPE WITH EXCEPTION:")
        # raise (exc)
end = time.time() # Typing end timestamp

print(f"\nActual elapsed time in seconds: {end - start}")
print(f"Total time spent on inputing chars in seconds: {c_total_time}")
print(f"Original estimated complete time in seconds: {total_time}")
