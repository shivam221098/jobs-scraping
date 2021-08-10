from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
import os
import pandas as pd


class Automation:
    def __init__(self):
        self.details = []
        self.configs = {}
        self.driver = None
        self.username = "mschrier@uw.edu"
        self.password = "Mountrainier1!"
        self.cont_t = 0
        self.cont_j = 0
        self.cont_d = 0
        self.cont_l = 0
        self.num_of_pages = 0
        self.page_counter = 1
        self.job_counter = 0

    def get_into_account(self):
        self.driver = webdriver.Chrome(executable_path=ChromeDriverManager().install())
        self.driver.get("https://uw.joinhandshake.com/login?ref=open-in-new-tab")
        self.driver.find_element_by_id("sso-name").click()
        time.sleep(4)

        self.driver.find_element_by_id("weblogin_netid").send_keys(self.username)
        self.driver.find_element_by_id("weblogin_password").send_keys(self.password)
        self.driver.find_element_by_id("submit_button").click()
        time.sleep(30)
        if self.configs.get("on_page") == 1:
            self.driver.find_element_by_xpath("//span[contains(text(),'Jobs')]").click()
        else:
            self.driver.get("")
        time.sleep(10)

    def get_num_pages(self):
        self.num_of_pages = pages(self.driver.find_element_by_class_name("style__page___1UaFT"))

    def apply_job(self):
        apply = self.driver.find_element_by_xpath("//div[@class='style__button-content___1aPle']")
        print(apply.text)
        if apply.text.lower() == "apply":
            self.driver.find_element_by_xpath("//div[@class='style__button-content___1aPle']").click()
            time.sleep(2)
            self.driver.find_element_by_class_name("style__pill___3uHDM.style__small___1oG3P.style__blue___mBOsr"
                                                   ".style__inverse___2z_Ei.style__clickable___3a6Y8").click()
            self.driver.find_element_by_xpath("//span[contains(text(),'Submit Application')]").click()
            self.driver.find_element_by_class_name("style__dismiss___Zotdc").click()
            time.sleep(3)
            return True

        elif apply.text.lower() == "quick apply":
            self.driver.find_element_by_xpath("//div[@class='style__button-content___1aPle']").click()
            time.sleep(2)
            self.driver.find_element_by_xpath("//span[contains(text(),'Submit Application')]").click()
            self.driver.find_element_by_class_name("style__dismiss___Zotdc").click()
            time.sleep(3)
            return True

        return False

    def get_configurations_csv(self):
        with open(os.path.join("configs.json"), "r", encoding='utf-8') as file:
            self.configs = json.loads(file.read())

    def refresh(self):


    def save_jobs(self):
        filename = f'jobs_from_page_{self.configs.get("page_done")}.csv'
        df = pd.DataFrame.from_dict(self.details)
        df.to_csv(filename, index=False)

        with open(os.path.join("configs.json"), "w", encoding='utf-8') as file:
            file.write(json.dumps({"page_done": self.page_counter}))

    def get_title(self):
        try:
            title = self.driver.find_element_by_xpath("//div[@class='style__job-title___28HlN']")
            self.cont_t = 0
            return title.text
        except Exception:
            if self.cont_t < 10:
                print("Retrying for title... ")
                self.cont_t += 1
                time.sleep(3)
                return self.get_title()

    def get_type_of_job(self):
        try:
            type_of_job = self.driver.find_element_by_class_name("style__job-type-info___2oQHN")
            self.cont_j = 0
            return type_of_job.text
        except Exception:
            if self.cont_j < 10:
                print("Retrying for type of job...")
                self.cont_j += 1
                time.sleep(3)
                return self.get_type_of_job()

    def get_deadline(self):
        try:
            deadline = self.driver.find_element_by_class_name('style__content___3I6Ej')
            self.cont_d = 0
            return deadline.text
        except Exception:
            if self.cont_d < 10:
                print("Retrying for deadline...")
                self.cont_d += 1
                time.sleep(3)
                return self.get_deadline()

    def get_left_column(self):
        try:
            left_column = self.driver.find_element_by_class_name("style__cards___2bvJ9")
            return left_column
        except Exception:
            if self.cont_l < 5:
                print("Retrying for left column...")
                time.sleep(3)
                self.cont_l += 1
                return self.get_left_column()

    def capture_jobs(self):

        left_column = self.get_left_column()

        links = left_column.find_elements_by_tag_name('a')
        self.cont_l = 0

        for i in links:
            time.sleep(2)
            applied = False
            """try:
                applied = self.apply_job()
            except Exception:
                pass"""

            title = self.get_title()

            try:
                location = self.driver.find_element_by_class_name("style__list-with-tooltip___2c5rW")
                location = location.text
            except Exception as e:
                print(e)
                location = 'WorldWide or United States'

            type_of_job = self.get_type_of_job()

            deadline = self.get_deadline()

            self.details.append({"on_page": self.page_counter, "title": title, "location": location,
                                 "type_of_job": type_of_job, "deadline": deadline, "applied": applied})

            i.click()
            self.job_counter += 1
            print("Jobs scraped: " + str(len(self.details)), end='\r')

    def driver_function(self):
        self.get_configurations_csv()
        self.get_into_account()
        self.get_num_pages()

        while self.configs.get("page_done") > self.page_counter:
            time.sleep(3)
            self.driver.find_element_by_css_selector("svg.svg-inline--fa.fa-chevron-right.fa-w-10.style__left"
                                                     "-icon___1hSd_.icon").click()
            self.page_counter += 1

        try:
            for page in range(self.num_of_pages - self.page_counter + 1):
                time.sleep(4)

                try:
                    self.capture_jobs()
                except Exception as e:
                    print(e)
                    time.sleep(3)
                    self.capture_jobs()

                self.driver.find_element_by_css_selector("svg.svg-inline--fa.fa-chevron-right.fa-w-10.style__left"
                                                         "-icon___1hSd_.icon").click()

                self.page_counter += 1

        except Exception as e:
            print(e)

        finally:
            self.save_jobs()
            self.driver.quit()
            exit(0)


def pages(page):
    num_page = page.text
    num_page = num_page.split("/")

    return int(num_page[1])


if __name__ == '__main__':
    try:
        automation = Automation()
        automation.driver_function()
    except Exception as e:
        print(e)
        time.sleep(10)
        automation = Automation()
        automation.driver_function()