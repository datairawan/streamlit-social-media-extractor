import streamlit as st
from streamlit_option_menu import option_menu
from serpapi import GoogleSearch
import pandas as pd
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options as ChromeOptions
import random, pandas as pd, time, re
from python_gsheet import config_gsheet
gsheet = config_gsheet()

def extract_group_status(text):
    if "private group" in text.lower():
        group_status = "Private"
    elif "public group" in text.lower():
        group_status = "Public"
    elif "grup publik" in text.lower():
        group_status = "Public"
    elif "grup privat" in text.lower():
        group_status = "Privat"
    else:
        group_status = "Others"
    return group_status

def extract_activities(text):
    if "Activity" in text:
        activities = text.split('\nActivity\n')[-1].split('Created')[0]

        if "No new post" in activities:
            today_post = '0'
        else:
            today_post = activities.split('new post')[0].lstrip().rstrip()

        total_members = activities.split('total members')[0].split('\n')[-1].lstrip().rstrip().replace(',','')
    elif "Aktivitas" in text:
        activities = text.split('\nAktivitas\n')[-1].split('Dibuat')[0]

        if "Tidak ada postingan" in activities:
            today_post = '0'
        else:
            today_post = activities.split('postingan baru hari ini')[0].lstrip().rstrip()

        total_members = activities.split('anggota total')[0].split('\n')[-1].lstrip().rstrip().replace(',','')
    else:
        today_post = ''
        total_members = ''

    return activities, today_post, total_members

def extract_group_name(text):
    if "Private group" in text:
        group_name = text.split('\nPrivate group')[0].split('\n')[-1]
    elif "Public group" in text:
        group_name = text.split('\nPublic group')[0].split('\n')[-1]
    elif "Grup Publik" in text:
        group_name = text.split('\nGrup Publik')[0].split('\n')[-1]
    elif "Grup Privat" in text:
        group_name = text.split('\nGrup Privat')[0].split('\n')[-1]
    else:
        group_name = 'unknown'
    return group_name

with st.sidebar:
    selected = option_menu(
        menu_title = None,
        options=["Social Media Extraction","Facebook Scraper","Price Competition"],
        icons=["instagram","facebook","tags"] #https://icons.getbootstrap.com/
    )

if selected == "Social Media Extraction":
    api_key = "00f7be7329a4f222afcf08795a8986e17efd931ed5a7b371f72642218906be1f"
    #tips: https://serpapi.com/blog/tips-and-tricks-of-google-search-api/
    def search_result(query, location="Indonesia", localization="id",channel="instagram"):
        search = GoogleSearch({
                                "q": "site:"+channel+".com "+query, 
                                "location": location,
                                "gl": localization,
                                "num": "100",
                                "no_cache": "true",
                                "api_key": api_key
                            })
        result = search.get_dict()
        result = pd.DataFrame(result["organic_results"])
        result = result[["title","link"]]
        return result

    channel = st.radio("Select Channel",  options=["Facebook","Instagram","Tiktok","Youtube"], horizontal =True)

    if channel == "Instagram":
        search_channel = "instagram"
    elif channel == "Facebook":
        search_channel = "facebook"
    elif channel == "Tiktok":
        search_channel = "tiktok"
    elif channel == "Youtube":
        search_channel = "youtube"
    else:
        pass

    form = st.form("form-1")
    influencer_focus = form.text_input("Profile Criteria")
    form_submit = form.form_submit_button("Submit")
    print(influencer_focus)
    print(search_channel)
    print(form_submit)

    query = "profile "+ influencer_focus

    if query == "profile ":
        pass
    elif form_submit == False:
        pass
    else:
        print("getting data ready")
        df = search_result(query, channel=search_channel)

        col1, col2, col3 = st.tabs(["Download CSV", "Upload Gsheet", "See Result"])

        with col1:
            st.download_button(label="Download as CSV",
                            data=df.to_csv().encode('utf-8'),
                            file_name='instagram_profile.csv',
                            mime='text/csv',
                            )

        with col2:
            form2 = st.form("form-2")
            form2.text_input("Input your Gsheet ID")
            form2.form_submit_button("Upload to Google Sheet")

        with col3:
            st.dataframe(df)
elif selected == "Facebook Scraper":
    
    def get_selenium_driver():

        import time
        from python_gsheet import config_gsheet
        gsheet = config_gsheet()
        sheet_url = "1XeBe8oLwMeq_UxxwMzD6PpeNF4wL7XJzbjlmHvN5Q0o"
        user_agent = gsheet.read_gsheet(sheet_url,"Agent")["user_agent"].tolist()[random.randint(0, 8)]
        selenium_arguments = gsheet.read_gsheet(sheet_url,"Selenium Argument")["arguments"].tolist()
        selenium_arguments.append("user-agent="+user_agent)

        chrome_options = ChromeOptions()
        for i in range(len(selenium_arguments)):
            chrome_options.add_argument(selenium_arguments[i])

        driver = webdriver.Chrome(options=chrome_options)
        driver.get("https://web.facebook.com/groups/968529856818122")
        
        return driver

    form3 = st.form("form-3")
    url = form3.text_area("Facebook Group URL")
    group_statistics = form3.form_submit_button("Extract Group Statistics")
    
    url = [x.rstrip().lstrip() for x in url.split(',')]
    print(url)

    if group_statistics == True:
        with st.spinner('Wait for it...'):
            df_result = pd.DataFrame()
            df = pd.DataFrame()
            driver = get_selenium_driver()
            for u in url:
                try:
                    group_url = u
                    driver.get(group_url+"/about")

                    try:
                        driver.find_element(By.XPATH,"//div[@aria-label='Close']").click()
                    except:
                        pass

                    element = driver.find_elements(By.TAG_NAME,"div")[0]
                    df = pd.DataFrame({'url' : group_url,
                                    'element_text' : element.text}, index=[0])

                    df["group name"] = [extract_group_name(x) for x in df["element_text"]]
                    df["status"] = [extract_group_status(x) for x in df["element_text"]]
                    df["today post"] = [int(extract_activities(x)[1]) for x in df["element_text"]]
                    df["total members"] = [int(extract_activities(x)[2].replace('.','')) for x in df["element_text"]]

                    df = df.drop("element_text", axis=1).sort_values('today post', ascending=False)
                    df = df.reset_index(drop=True)
                except:
                    pass
                df_result = df_result._append(df)
        st.success('Done!')
        st.dataframe(df_result)
    else:
        pass

elif selected == "Price Competition":
    st.text("LAH KOK GITU")