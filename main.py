from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
import os
import pandas as pd


class Automation:
    def __init__(self):
        self.details = []
        self.configs = {}
        self.resumes = {}
        self.covers = {}
        self.common_resume = None
        self.driver = None
        self.title = None
        self.username = "mschrier@uw.edu"
        self.password = "Mountrainier1!"
        self.cont_t = 0
        self.cont_j = 0
        self.cont_d = 0
        self.cont_l = 0
        self.cont_al = 0
        self.cont_cn = 0
        self.num_of_pages = 0
        self.page_counter = 1
        self.job_counter = 0

    def get_into_account(self):
        self.driver = webdriver.Chrome(executable_path=ChromeDriverManager().install())
        page_num = self.configs.get("page_done")
        self.driver.get(f"https://app.joinhandshake.com/postings?page={page_num}&per_page=200&sort_direction=desc"
                        f"&sort_column=default")
        self.page_counter = page_num
        self.driver.find_element_by_class_name("select2-chosen").click()
        self.driver.find_element_by_class_name("select2-input").send_keys("university of washington")
        time.sleep(3)
        self.driver.find_element_by_class_name("select2-result-label").click()
        time.sleep(3)
        self.driver.find_element_by_id("sso-name").click()
        time.sleep(4)

        self.driver.find_element_by_id("weblogin_netid").send_keys(self.username)
        self.driver.find_element_by_id("weblogin_password").send_keys(self.password)
        self.driver.find_element_by_id("submit_button").click()
        time.sleep(30)

        # self.driver.find_element_by_xpath("//span[contains(text(),'Jobs')]").click()
        #if self.configs.get("on_page") == 1:
        #    self.driver.get("https://uw.joinhandshake.com/postings?page=1&per_page=200&sort_direction=desc&sort_column=default")

    def get_num_pages(self):
        self.num_of_pages = pages(self.driver.find_element_by_class_name("style__page___2NW2u"))

    def click_apply(self):
        try:
            apply = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "style__button-content___1myJg"))
            )
            if apply.text.lower() == "apply" or apply.text.lower() == "quick apply":
                apply.click()
            self.cont_al = 0
            return apply
        except Exception:
            if self.cont_al < 5:
                time.sleep(2)
                self.click_apply()
                return self.click_apply()

    def apply_job(self):
        apply = self.click_apply()

        if apply.text.lower() == "apply":
            found = False
            resume = ""
            time.sleep(2)
            # self.driver.find_element_by_class_name("style__pill___3uHDM.style__small___1oG3P.style__blue___mBOsr"
            #                                        ".style__inverse___2z_Ei.style__clickable___3a6Y8").click()
            for key, value in self.resumes.items():
                if key in self.title.lower() and len(value) > 5:
                    resume = value
                    found = True
                    break

            if not found:
                resume = self.configs.get("common_resume")
            print(resume, apply.text)
            
            self.driver.find_element_by_class_name("Select-multi-value-wrapper").click()
            print("clicked")
            self.driver.find_element_by_class_name("Select-multi-value-wrapper").send_keys(resume)
            print("send")
            self.driver.find_element_by_class_name("Select-menu-outer").click()
            self.driver.find_element_by_xpath("//span[contains(text(),'Submit Application')]").click()
            self.driver.find_element_by_class_name("style__dismiss___Zotdc").click()
            time.sleep(3)
            return True

        elif apply.text.lower() == "quick apply":
            # self.driver.find_element_by_class_name("style__button-content___1myJg").click()
            time.sleep(2)
            print("Clicked")
            self.driver.find_element_by_xpath("//span[contains(text(),'Submit Application')]").click()
            print("Above zotdc")
            self.driver.find_element_by_class_name("style__dismiss___Zotdc").click()
            time.sleep(3)
            return True

        return False

    def get_configurations_csv(self):
        with open(os.path.join("configs.json"), "r", encoding='utf-8') as file:
            self.configs = json.loads(file.read())

        # Getting resumes and covers
        for key, value in self.configs.items():
            if key.startswith("resume"):
                resume_name = key.split("_")[1]
                self.resumes.update({resume_name: value})
            elif key.startswith("cover"):
                cover_name = key.split("_")[1]
                self.covers.update({cover_name: value})

    def save_jobs(self):
        filename = f'jobs_from_page_{self.configs.get("page_done")}.csv'
        df = pd.DataFrame.from_dict(self.details)
        df.to_csv(filename, index=False)

        new_config = {
            "page_done": self.page_counter,
        }

        for key, value in self.configs.items():
            if key != "page_done":
                new_config.update({key: value})

        with open(os.path.join("configs.json"), "w", encoding='utf-8') as file:
            file.write(json.dumps(new_config))

    def get_title(self):
        try:
            title = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//div[@class='style__job-title___1Ux6D']"))
            )
            self.cont_t = 0
            return title.text
        except Exception:
            if self.cont_t < 5:
                print("Retrying for title... ")
                self.cont_t += 1
                time.sleep(3)
                return self.get_title()

    def get_type_of_job(self):
        try:
            type_of_job = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "style__job-type-info___27Rhf"))
            )
            self.cont_j = 0
            return type_of_job.text
        except Exception:
            if self.cont_j < 5:
                print("Retrying for type of job...")
                self.cont_j += 1
                time.sleep(3)
                return self.get_type_of_job()

    def get_deadline(self):
        try:
            deadline = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'style__content___1ZhQ7'))
            )
            self.cont_d = 0
            return deadline.text
        except Exception:
            if self.cont_d < 5:
                print("Retrying for deadline...")
                self.cont_d += 1
                time.sleep(3)
                return self.get_deadline()

    def get_company_name(self):
        try:
            c_name = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'style__employer-name___1Eqgf'))
            )
            self.cont_cn = 0
            return c_name.text
        except Exception:
            if self.cont_cn < 5:
                self.cont_cn += 1
                time.sleep(3)
                return self.get_company_name()

    def get_left_column(self):
        try:
            left_column = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "style__cards___3PF23"))
            )
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

        count = 0
        for i in links:
            if count > 0:
                title = self.get_title()
                self.title = title  # Current title

                applied = False
                try:
                    applied = self.apply_job()
                except Exception:
                    pass

                try:
                    location = self.driver.find_element_by_class_name("style__list-with-tooltip___UXouc")
                    location = location.text
                except Exception:
                    location = 'WorldWide or United States'

                type_of_job = self.get_type_of_job()

                deadline = self.get_deadline()

                company_name = self.get_company_name()

                self.details.append({"on_page": self.page_counter, "title": title, "location": location,
                                     "type_of_job": type_of_job, "deadline": deadline, "company_name": company_name,
                                     "applied": applied})

                self.job_counter += 1
                print("Jobs scraped: " + str(len(self.details)), end='\r')

            i.click()
            count += 1

    def driver_function(self):
        self.get_configurations_csv()
        self.get_into_account()
        self.get_num_pages()

        try:
            for page in range(self.num_of_pages - self.page_counter + 1):
                time.sleep(2)

                try:
                    self.capture_jobs()
                except Exception:
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