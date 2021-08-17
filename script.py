from selenium import webdriver
from selenium.webdriver.support.ui import Select, WebDriverWait
from requests_html import HTMLSession, AsyncHTMLSession
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time, credentials, requests
import concurrent.futures
import threading

base_url = 'https://member.identityiq.com'
# Setup our headless browser. 
options = webdriver.ChromeOptions()
# options.add_argument('--headless')
options.add_experimental_option('excludeSwitches', ['enable-logging'])

driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

def main():
    try:
        data = loginIdentityIQ()
        return data
    except:
        return 'Wrong Credentials or Slow Internet Connectivity Detected. Please try again.'

def loginIdentityIQ():
    driver.maximize_window()
    driver.get(base_url + '/login.aspx')
    time.sleep(2)

    WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.ID,'txtUsername')))
    username = driver.find_element_by_id("txtUsername")
    WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.ID,'txtPassword')))
    password = driver.find_element_by_id("txtPassword")

    username.send_keys(credentials.email)
    password.send_keys(credentials.password)

    driver.find_element_by_xpath("//input[@id='imgBtnLogin']").click()
    time.sleep(2)

    if driver.current_url == 'https://member.identityiq.com/SecurityQuestions.aspx':
        data = question()
        return data
        # except:
        #     print('Security Question Issue')
    elif driver.current_url == 'https://member.identityiq.com/Dashboard.aspx':
        data = report()
        return data
    else:
        return False

def question():
    WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.ID,'FBfbforcechangesecurityanswer_txtSecurityAnswer')))
    answer = driver.find_element_by_id("FBfbforcechangesecurityanswer_txtSecurityAnswer")
    answer.send_keys(credentials.ssn)

    driver.find_element_by_xpath("//input[@id='FBfbforcechangesecurityanswer_ibtSubmit']").click()
    time.sleep(2)

    if driver.current_url == 'https://member.identityiq.com/Dashboard.aspx':
        data = report()
        # print('data', data)
        return data
    else:
        return False

def report():
    driver.get(base_url + '/CreditReport.aspx')
    time.sleep(4)
    r_table = driver.find_element_by_xpath("//table[@id='reportTop']")
    r_body = r_table.find_element_by_tag_name('tbody')
    r_row = r_body.find_element_by_tag_name("tr")
    r_col = r_row.find_elements_by_tag_name("td")
    
    r =[
        {
            r_col[0].text: r_col[1].text,
            r_col[2].text: r_col[3].text
        }
    ]
    
    # print('aya')
    # pi = []
    # cs = []
    # s = []
    # ah = []
    # i = []
    # cc = []
    # result = []
    # with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
    #     print('idr bhi aya')
    #     future = {executor.map(getPersonalInformation(driver), getCreditScore(driver), getSummary(driver), getAccountHistory(driver), getInquiries(driver), getCreditorContacts(driver))}
    #     for result in future:
    #         print(result)
    #         print(dict(result))
    
    pi = getPersonalInformation()
    cs = getCreditScore()
    s = getSummary()
    ah = getAccountHistory()
    i = getInquiries()
    # Ignore Public Information
    cc = getCreditorContacts()

    # threading.Thread(target=getPersonalInformation).start()
    # threading.Thread(target=getCreditScore).start()
    # threading.Thread(target=getSummary).start()
    # threading.Thread(target=getAccountHistory).start()
    # threading.Thread(target=getInquiries).start()
    # threading.Thread(target=getCreditorContacts).start()
    
    data = {
        'Personal Information': pi,
        'Credit Score': cs,
        'Summary': s,
        'Account History': ah,
        'Inquiries': i,
        'Creditor Contacts': cc
    }
    
    return data

def getPersonalInformation():
    pi_array =[]
    pi_table = driver.find_elements_by_xpath("//table[@class='rpt_content_table rpt_content_header rpt_table4column']")[0]
    pi_body = pi_table.find_element_by_tag_name('tbody')
    pi_rows = pi_body.find_elements_by_tag_name("tr")
    for val, row in enumerate(pi_rows):
        if val!=0:
            pi_cols = row.find_elements_by_class_name("info")
            pi_array.extend([pi_cols[0].text, pi_cols[1].text, pi_cols[2].text])
        else:
            continue
    pi =[
            {
                'key': 'TransUnion', 
                'values': {
                    'Credit Report Date': pi_array[0],
                    'Name': pi_array[3],
                    'Also Knows As': pi_array[6],
                    'Former': pi_array[9],
                    'Date of Birth': pi_array[12],
                    'Current Address(es)': pi_array[15],
                    'Previous Address(es)': pi_array[18],
                    'Employers': pi_array[21]
                }
            }, 
            {
                'key': 'Experian', 
                'values': {
                    'Credit Report Date': pi_array[1],
                    'Name': pi_array[4],
                    'Also Knows As': pi_array[7],
                    'Former': pi_array[10],
                    'Date of Birth': pi_array[13],
                    'Current Address(es)': pi_array[16],
                    'Previous Address(es)': pi_array[19],
                    'Employers': pi_array[22]
                }
            }, 
            {
                'key': 'Equifax', 
                'values': {
                    'Credit Report Date': pi_array[2],
                    'Name': pi_array[5],
                    'Also Knows As': pi_array[8],
                    'Former': pi_array[11],
                    'Date of Birth': pi_array[14],
                    'Current Address(es)': pi_array[17],
                    'Previous Address(es)': pi_array[20],
                    'Employers': pi_array[23]
                }
            }
        ]
    return pi

def getCreditScore():
    cs_array = []
    cs_table = driver.find_elements_by_xpath("//table[@class='rpt_content_table rpt_content_header rpt_table4column']")[1]
    cs_body = cs_table.find_element_by_tag_name('tbody')
    cs_rows = cs_body.find_elements_by_tag_name("tr")
    for val, row in enumerate(cs_rows):
        if val!=0:
            cs_cols = row.find_elements_by_class_name("info")
            cs_array.extend([cs_cols[0].text, cs_cols[1].text, cs_cols[2].text])
        else:
            continue
    cs = [
        {
            'key': 'TransUnion',
            'values': {
                'Credit Score': cs_array[0],
                'Lender Rank': cs_array[3],
                'score Scale': cs_array[6]
            }
        },
        {
            'key': 'Experian',
            'values': {
                'Credit Score': cs_array[1],
                'Lender Rank': cs_array[4],
                'score Scale': cs_array[7]
            }
        },
        {
            'key': 'Equifax',
            'values': {
                'Credit Score': cs_array[2],
                'Lender Rank': cs_array[5],
                'score Scale': cs_array[8]
            }
        }
    ]
    return cs

def getSummary():
    s_array = []
    s_table = driver.find_elements_by_xpath("//table[@class='rpt_content_table rpt_content_header rpt_table4column']")[2]
    s_body = s_table.find_element_by_tag_name('tbody')
    s_rows = s_body.find_elements_by_tag_name("tr")
    for val, row in enumerate(s_rows):
        if val!=0:
            s_cols = row.find_elements_by_class_name("info")
            s_array.extend([s_cols[0].text, s_cols[1].text, s_cols[2].text])
        else:
            continue
    s = [
        {
            'key': 'TransUnion',
            'values': {
                'Total Accounts': s_array[0],
                'Open Accounts': s_array[3],
                'Closed Accounts': s_array[6],
                'Delinquent': s_array[9],
                'Derogatory': s_array[12],
                'Collection': s_array[15],
                'Balances': s_array[18],
                'Payments': s_array[21],
                'Public Records': s_array[24],
                'Inquiries(2 years)': s_array[27]
            }
        },
        {
            'key': 'Experian',
            'values': {
                'Total Accounts': s_array[1],
                'Open Accounts': s_array[4],
                'Closed Accounts': s_array[7],
                'Delinquent': s_array[10],
                'Derogatory': s_array[13],
                'Collection': s_array[16],
                'Balances': s_array[19],
                'Payments': s_array[22],
                'Public Records': s_array[25],
                'Inquiries(2 years)': s_array[28]
            }
        },
        {
            'key': 'Equifax',
            'values': {
                'Total Accounts': s_array[2],
                'Open Accounts': s_array[5],
                'Closed Accounts': s_array[8],
                'Delinquent': s_array[11],
                'Derogatory': s_array[14],
                'Collection': s_array[17],
                'Balances': s_array[20],
                'Payments': s_array[23],
                'Public Records': s_array[26],
                'Inquiries(2 years)': s_array[29]
            }
        }
    ]
    return s

def getAccountHistory():
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    
    time.sleep(1)
    
    account_table = driver.find_elements_by_xpath("//table[@class='rpt_content_table rpt_content_header rpt_table4column ng-scope']")
    account_length = len(account_table)
    ah = []

    for x in range(0, account_length):
        account_array = []
        payment_array = []
        account_table = driver.find_elements_by_xpath("//table[@class='rpt_content_table rpt_content_header rpt_table4column ng-scope']")[x]
        account_body = account_table.find_element_by_tag_name('tbody')
        account_rows = account_body.find_elements_by_tag_name("tr")
        for val, row in enumerate(account_rows):
            if val!=0:
                account_cols = row.find_elements_by_class_name("info")
                account_array.extend([account_cols[0].text, account_cols[1].text, account_cols[2].text])
            else:
                continue

        payment_table = driver.find_elements_by_xpath("//table[@class='rpt_content_table addr_hsrty']")[x]
        payment_body = payment_table.find_element_by_tag_name('tbody')
        payment_rows = payment_body.find_elements_by_tag_name("tr")
        for row in payment_rows:
            payment_cols = row.find_elements_by_class_name("info")
            for col in payment_cols:
                payment_array.append(col.text)
        
        payment_history = []
        count = 0

        while count<24:
            payment_history.append({
                    'Month': payment_array[count],
                    'Year': payment_array[count+24],
                    'TransUnion': payment_array[count+48],
                    'Experian': payment_array[count+72],
                    'Equifax': payment_array[count+96]
                }
            )
            count = count + 1

        ah.append(
            {
                'key': x,
                'TransUnion': {
                    'Account #': account_array[0],
                    'Account Type': account_array[3],
                    'Account Type - Detail': account_array[6],
                    'Bureau Code': account_array[9],
                    'Account Status': account_array[12],
                    'Monthly Payment': account_array[15],
                    'Date Opened': account_array[18],
                    'Balance': account_array[21],
                    'No. of Months (terms)': account_array[24],
                    'High Credit': account_array[27],
                    'Credit Limit': account_array[30],
                    'Past Due': account_array[33],
                    'Payment Status': account_array[36],
                    'Last Reported': account_array[39],
                    'Comments': account_array[42],
                    'Date Last Active': account_array[45],
                    'Date of Last Payment': account_array[48]
                },
                'Experian': {
                    'Account #': account_array[1],
                    'Account Type': account_array[4],
                    'Account Type - Detail': account_array[7],
                    'Bureau Code': account_array[10],
                    'Account Status': account_array[13],
                    'Monthly Payment': account_array[16],
                    'Date Opened': account_array[19],
                    'Balance': account_array[22],
                    'No. of Months (terms)': account_array[25],
                    'High Credit': account_array[28],
                    'Credit Limit': account_array[31],
                    'Past Due': account_array[34],
                    'Payment Status': account_array[37],
                    'Last Reported': account_array[40],
                    'Comments': account_array[43],
                    'Date Last Active': account_array[46],
                    'Date of Last Payment': account_array[49]
                },
                'Equifax': {
                    'Account #': account_array[2],
                    'Account Type': account_array[5],
                    'Account Type - Detail': account_array[8],
                    'Bureau Code': account_array[11],
                    'Account Status': account_array[14],
                    'Monthly Payment': account_array[17],
                    'Date Opened': account_array[20],
                    'Balance': account_array[23],
                    'No. of Months (terms)': account_array[26],
                    'High Credit': account_array[29],
                    'Credit Limit': account_array[32],
                    'Past Due': account_array[35],
                    'Payment Status': account_array[38],
                    'Last Reported': account_array[41],
                    'Comments': account_array[44],
                    'Date Last Active': account_array[47],
                    'Date of Last Payment': account_array[50]
                },
                'Payment History': payment_history
            }
        )
    return ah

def getInquiries():
    try:
        i = []
        i_table = driver.find_elements_by_xpath("//table[@class='rpt_content_table rpt_content_header rpt_content_contacts ng-scope']")[-2]
        i_body = i_table.find_element_by_tag_name('tbody')
        i_rows = i_body.find_elements_by_tag_name("tr")
        for val, row in enumerate(i_rows):
            if val!=0:
                i_cols = row.find_elements_by_class_name("info")
                i.append({'Creditor Name': i_cols[0].text, 'Type of Business': i_cols[1].text, 'Date of Inquiry': i_cols[2].text, 'Credit Bureau': i_cols[3].text})
            else:
                continue
    except:
        i.append({'Creditor Name': '', 'Type of Business': '', 'Date of Inquiry': '', 'Credit Bureau': ''}) 
    return i

def getCreditorContacts():
    try:
        cc = []
        cc_table = driver.find_elements_by_xpath("//table[@class='rpt_content_table rpt_content_header rpt_content_contacts ng-scope']")[-1]
        cc_body = cc_table.find_element_by_tag_name('tbody')
        cc_rows = cc_body.find_elements_by_tag_name("tr")
        for val, row in enumerate(cc_rows):
            if val!=0:
                cc_cols = row.find_elements_by_class_name("info")
                cc.append({'Creditor Name': cc_cols[0].text, 'Address': cc_cols[1].text, 'Phone Number': cc_cols[2].text})
            else:
                continue
    except:
        cc.append({'Creditor Name': '', 'Address': '', 'Phone Number': ''}) 
    return cc

# define main
if __name__ == '__main__':
    main()
