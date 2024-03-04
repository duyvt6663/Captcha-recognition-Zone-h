import requests
import os
import sys
import asyncio
import aiohttp
from config import FILE_COUNTER
import random

class CaptchaGenerator:
    def __init__(
        self, 
        captcha_url="https://www.zone-h.org/captcha.py", 
        captcha_path="test_set/imgs/", 
        template="captcha_{}.png"
    ):
        """
        This is the constructor method for the CaptchaGenerator class.
        It initializes the captcha path, captcha url, and file template.
        --------------------------------------------------------------
        :param captcha_url: The URL of the captcha image.
        :param captcha_path: The path where the captcha image will be saved.
        :param template: The template for the filename of the captcha image.
        :output: None
        """

        self.captcha_path = captcha_path
        self.captcha_url = captcha_url
        self.file_template = template 
        # self._lock = asyncio.Lock()  
        self._file_counter = FILE_COUNTER

    def generate_file_name(self):
        """
        This method generates a unique filename for the captcha image.
        --------------------------------------------------------------
        :param: None
        :output: filename
        """

        self._file_counter += 1
        print(f"File counter: {self._file_counter}")
        # Construct the filename with the current index
        filename = self.file_template.format(self._file_counter)
        return filename

    async def _agenerate_captcha(
        self,
        max_retries=5, 
        initial_interval=0.5, 
        max_interval=10
    ):
        """
        This method generates a captcha image from the given URL.
        --------------------------------------------------------------
        :param: None
        :output: None
        """
        for attempt in range(max_retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(self.captcha_url) as response:
                        # Use .status to get the status code
                        if response.status == 200:
                            filename = self.generate_file_name()
                            filepath = os.path.join(self.captcha_path, filename)
                            # You need to use 'await' to read the content
                            content = await response.read()
                            with open(filepath, "wb") as f:
                                f.write(content)
                            return None # Break and return the loop if the request was successful
                        elif response.status == 503:
                            # Service Unavailable, prepare to retry
                            print(f"Attempt {attempt+1}: Got 503 Service Unavailable.")
                        else:
                            # Other HTTP errors, could log or handle accordingly
                            print(f"Attempt {attempt+1}: Received HTTP {response.status}.")
                            break  # or handle other statuses as needed
            except aiohttp.ClientError as e:
                print(f"Attempt {attempt+1}: ClientError {e}")
            except Exception as e:
                print(f"Attempt {attempt+1}: An unexpected error occurred: {e}")
                break  # Break on non-retriable errors
        
            # Calculate wait time for exponential backoff
            wait_interval = min(initial_interval * (2 ** attempt), max_interval)
            # Add jitter to the wait interval
            jitter = random.uniform(0, 0.1) * wait_interval
            wait_time = wait_interval + jitter

            print(f"Retrying in {wait_time:.2f}s...")
            await asyncio.sleep(wait_time)
        
        print(f"All {max_retries} retries failed.")
        return None
    
    async def abatch_generate_captcha(self, n=50):
        """
        This method generates a batch of captcha images from the given URL.
        --------------------------------------------------------------
        :param n: The number of captcha images to generate.
        :output: None
        """
        
        tasks = [self._agenerate_captcha() for _ in range(n)]
        await asyncio.gather(*tasks)

        # write config back to file
        with open("data/config.py", "w") as f:
            f.write(f"FILE_COUNTER = {self._file_counter}")

if __name__ == "__main__":
    # Create an instance of the CaptchaGenerator class
    cg = CaptchaGenerator()
    # Create the test_set directory if it does not exist
    if not os.path.exists(cg.captcha_path):
        os.makedirs(cg.captcha_path)
        
    # Create an event loop
    loop = asyncio.get_event_loop()
    # Run the coroutine
    loop.run_until_complete(cg.abatch_generate_captcha(20))
    # Close the event loop
    loop.close()