import time
from itertools import islice
from random import randint, uniform
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


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


MAX_CHUNK_WAITTIME = 0.25
WPM = 150 # Desired words per minute
SPW = 60 / WPM # Seconds per word
CHAR_INPUT_TIME = 0.03 # Time it takes to input a char in seconds
CHRPM = WPM * 5 # Assuming each word on average has 5 chars, this is chars per minute

chromedriver_location = "./chromedrivers/chromedriver_mac64"
chrome_options = Options()
# chrome_options.add_argument("--headless")
chrome_options.add_argument("--remote-debugging-port=9222")
driver = webdriver.Chrome(executable_path=chromedriver_location, options=chrome_options)
TYPERACER = "https://play.typeracer.com/"
driver.get(TYPERACER)

while True:
    try:
        race_btn_xpath = '//*[@id="gwt-uid-1"]/a'
        # race_btn_xpath = "(//div[@class='mainMenu']/table/descendant::tr)[2]/descendant::*[@class='gwt-Anchor']"
        driver.find_element_by_xpath(race_btn_xpath).click()
        break
    except:
        print("CAN'T FIND RACE BUTTON\n")

while True:
    time.sleep(0.01)
    try:
        input_panel_xpath = "//div[@class='mainViewport']/descendant::table[@class='inputPanel']"
        spans_xpath = "/descendant::span"
        spans = driver.find_elements_by_xpath(input_panel_xpath + spans_xpath)
        text = spans[0].text.strip() + spans[1].text.strip() + " " + spans[2].text.strip()
        print(f"Text:\n{text}\n")
        
        # Need a dynamic way to calculate wait time between words
        # Because TypeRacer calculates WPM based on the # of words typed divided by the elapsed time
        num_words = len(text.split(" "))
        num_chars = len(text)
        total_time = SPW * (num_words) # In seconds

        # Inputing a char can even take some time, so now we have to subtract that time from the total_time to calculate the wait time between chars
        char_wait_time = \
            (total_time - num_chars * CHAR_INPUT_TIME) / (num_chars - 1) # In seconds
        print(f"Number of words in text: {num_words}")
        print(f"Target words per minute: {WPM}")
        print(f"Estimated complete time in seconds: {total_time}")
        print(f"Number of chars in text: {num_chars}")
        print(f"Char wait time: {char_wait_time}")
        break
    except Exception as exc:
        print(f"CAN'T FIND INPUT PANEL WITH EXCEPTION:\n{exc}\n")

# start = 0 # Typing start timestamp
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
            
            # Calculate the total time remaining
            # and number of chars remaining so we can re-calculate the char wait time
            if idx < num_chars - 1:
                total_time_remaining -= c_time
                num_chars_remaining = len(text[idx+1:])
                char_wait_time = \
                    (total_time_remaining - num_chars_remaining * c_time) / \
                        (num_chars_remaining - 1)
            
            print(f"New char wait time: {char_wait_time}")
            time.sleep(char_wait_time)
            
            total_time_remaining -= char_wait_time
        break
    except Exception as exc:
        # print(exc)
        pass
end = time.time() # Typing end timestamp

print(f"Actual elapsed time in seconds: {end - start}")
print(f"Total time spent on inputing chars in seconds: {c_total_time}")
print(f"Original estimated complete time in seconds: {total_time}")
