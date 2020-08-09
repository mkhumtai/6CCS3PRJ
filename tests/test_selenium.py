from selenium import webdriver
import os


# Setup selenium driver
def test_setup():
    PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
    DRIVER_BIN = os.path.join(PROJECT_ROOT, "chromedriver_mac")
    global driver
    #driver = webdriver.Chrome('chromedriver_mac')
    driver = webdriver.Chrome(executable_path=DRIVER_BIN)
    driver.implicitly_wait(10)


# Check that users who are not logged receives Unauthorized user notice
def test_login_required():
    driver.get('https://k1763918.herokuapp.com/logout.html')
    driver.get('https://k1763918.herokuapp.com/allTime.html')
    assert "Unauthorized" in driver.page_source


# Check that users are able to register
def test_register():
    driver.get('https://k1763918.herokuapp.com/logout.html')
    driver.get('https://k1763918.herokuapp.com/register.html')
    driver.find_element_by_id('username').send_keys('testing_user')
    driver.find_element_by_id('email').send_keys('testing@gmail.com')
    driver.find_element_by_id('password').send_keys('testing_password')
    driver.find_element_by_xpath("//button[@class='btn btn-fill btn-primary']").click()


# Test that users cannot register with the same information
def test_user_exists():
    driver.get('https://k1763918.herokuapp.com/logout.html')
    driver.get('https://k1763918.herokuapp.com/register.html')
    driver.find_element_by_id('username').send_keys('testing_user')
    driver.find_element_by_id('email').send_keys('testing@gmail.com')
    driver.find_element_by_id('password').send_keys('testing_password')
    driver.find_element_by_xpath("//button[@class='btn btn-fill btn-primary']").click()
    assert "User exists!" in driver.page_source


# Check that users with incorrect login details cannot login
def test_unauthenticated_user():
    driver.get('https://k1763918.herokuapp.com/login.html')
    driver.find_element_by_id('username').send_keys('random_user')
    driver.find_element_by_id('password').send_keys('wrong_password')
    driver.find_element_by_xpath("//button[@class='btn btn-fill btn-primary']").click()
    assert "<label>Unknown user</label>" in driver.page_source


# Check that users with correct login details can login
def test_authenticated_user():
    driver.get('https://k1763918.herokuapp.com/login.html')
    driver.find_element_by_id('username').send_keys('testing_user')
    driver.find_element_by_id('password').send_keys('testing_password')
    driver.find_element_by_xpath("//button[@class='btn btn-fill btn-primary']").click()
    assert "No. of Cases by quarter" in driver.page_source


# Check that table visualization can be viewed from /query.html
def test_query_table():
    driver.get('https://k1763918.herokuapp.com/query.html')
    sero = driver.find_element_by_xpath("//input[@value='H5N1 HPAI']")
    region = driver.find_element_by_xpath("//input[@value='Asia']")
    type = driver.find_element_by_xpath("//input[@value='wild']")
    sero.click()
    region.click()
    type.click()
    driver.find_element_by_name("from_date").send_keys('01/01/2004')
    driver.find_element_by_name("to_date").send_keys('01/01/2020')
    driver.find_element_by_xpath("//input[@value='Table']").click()
    assert "Data gathered from" in driver.page_source


# Check that zero rows are returned when data queried incorrectly
def test_query_table():
    driver.get('https://k1763918.herokuapp.com/query.html')
    sero = driver.find_element_by_xpath("//input[@value='H5N1 HPAI']")
    region = driver.find_element_by_xpath("//input[@value='Asia']")
    sero.click()
    region.click()
    driver.find_element_by_name("from_date").send_keys('01/01/2004')
    driver.find_element_by_name("to_date").send_keys('01/01/2020')
    driver.find_element_by_xpath("//input[@value='Table']").click()
    assert "Total rows: 0" in driver.page_source


# Check that marker visualization can be viewed from /query.html
def test_query_marker():
    driver.get('https://k1763918.herokuapp.com/query.html')
    sero = driver.find_element_by_xpath("//input[@value='H5N1 HPAI']")
    region = driver.find_element_by_xpath("//input[@value='Asia']")
    type = driver.find_element_by_xpath("//input[@value='wild']")
    sero.click()
    region.click()
    type.click()
    driver.find_element_by_name("from_date").send_keys('01/01/2004')
    driver.find_element_by_name("to_date").send_keys('01/01/2020')
    driver.find_element_by_xpath("//input[@value='Markers']").click()
    assert "Interactive Map" in driver.page_source


# Check that heatmap visualization can be viewed from /query.html
def test_query_heatmap():
    driver.get('https://k1763918.herokuapp.com/query.html')
    sero = driver.find_element_by_xpath("//input[@value='H5N1 HPAI']")
    region = driver.find_element_by_xpath("//input[@value='Asia']")
    type = driver.find_element_by_xpath("//input[@value='wild']")
    sero.click()
    region.click()
    type.click()
    driver.find_element_by_name("from_date").send_keys('01/01/2004')
    driver.find_element_by_name("to_date").send_keys('01/01/2020')
    driver.find_element_by_xpath("//input[@value='Heatmap']").click()
    assert "Heatmap using Leaflet" in driver.page_source


def test_teardown():
    driver.close()
    driver.quit()
