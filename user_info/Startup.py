import PySimpleGUI as sg
import json
import writefile
import gui2
from sys import exit

try:
    with open("personal_info.json", "r") as file:
        user_info = json.load(file)
except FileNotFoundError:
    user_info = {}
    user_info["Job Title must Contain"] = []
    user_info["Job Title Keywords to Ignore"] = []
    user_info["Companies to Ignore"] = []

states = ["", "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware", "Florida",
          "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts",
          "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico",
          "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina",
          "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"]
countries = ["", "United States of America", "Other"]
time_zone = ["", "PST", "MST", "CST", "EST"]

sg.theme("Gray Gray Gray")


# sg.theme_previewer()

def info_from_user_info(v) -> str:
    try:
        return str(user_info[v])
    except:
        return ""


layout1 = [
    [sg.Text("Personal Info", font=("Helvetica", 12, "bold"))],
    [sg.HorizontalSeparator()],
    [sg.Text("First Name", size=(15, 1)), sg.Input(default_text=info_from_user_info("first name"), key="First Name"),
     sg.Text("error", key="firsterror", text_color="red", visible=False)],
    [sg.Text("Last Name", size=(15, 1)), sg.Input(default_text=info_from_user_info("last name"), key="Last Name"),
     sg.Text("error", key="lasterror", text_color="red", visible=False)],
    [sg.Text("Middle Name", size=(15, 1)), sg.Input(default_text=info_from_user_info("middle name"), key="Middle Name")],
    [sg.Text("LinkedIn", size=(15, 1)), sg.Input(default_text=info_from_user_info("linkedin"), key="LinkedIn")],
    [sg.Text("Website", size=(15, 1)), sg.Input(default_text=info_from_user_info("website"), key="Website")],
    # [sg.Text("Language", size=(15, 1)), sg.Input(default_text=info_from_user_info("language"), key="Language"),
    # sg.Text("error", key="languageerror", text_color="red", visible=False)],
    [sg.Text("Contact Info", font=("Helvetica", 12, "bold"))],
    [sg.HorizontalSeparator()],
    [sg.Text("Time Zone", size=(15, 1)),
     sg.Drop(values=time_zone, default_value=info_from_user_info("time zone").upper(), auto_size_text=True, key="Time Zone")],
    [sg.Text("Email", size=(15, 1)), sg.Input(default_text=info_from_user_info("email"), key="Email"),
     sg.Text("error", key="emailerror", text_color="red", visible=False)],
    [sg.Text("Phone Number", size=(15, 1)), sg.Input(default_text=info_from_user_info("phone"), key="Phone Number"),
     sg.Text("in xxxxxxxxxx format", key="phoneerror", text_color="red", visible=False)],
    [sg.Text("Country", size=(15, 1)), sg.Drop(values=countries, default_value=info_from_user_info("country"), auto_size_text=True, key="Country"),
     sg.Text("error", key="countryerror", text_color="red", visible=False)],
    [sg.Text("State", size=(15, 1)), sg.Drop(values=states, default_value=info_from_user_info("state"), auto_size_text=True, key="State"),
     sg.Text("error", key="stateerror", text_color="red", visible=False)],
    [sg.Text("County", size=(15, 1)), sg.Input(default_text=info_from_user_info("county"), key="County")],
    [sg.Text("City", size=(15, 1)), sg.Input(default_text=info_from_user_info("city"), key="City"),
     sg.Text("error", key="cityerror", text_color="red", visible=False)],
    [sg.Text("Address", size=(15, 1)), sg.Input(default_text=info_from_user_info("address"), key="Address"),
     sg.Text("error", key="addresserror", text_color="red", visible=False)],
    [sg.Text("Zip Code", size=(15, 1)), sg.Input(default_text=info_from_user_info("zip"), key="Zip code"),
     sg.Text("error", key="ziperror", text_color="red", visible=False)],
    [sg.Submit()]
]

window = sg.Window("Personal Info", layout1, size=(600, 500))
if "years of experience" not in user_info or len(str(user_info["years of experience"])) == 0:
    yearexp = 0
else:
    yearexp = int(info_from_user_info("years of experience"))

layout2 = [
    [sg.Text("Job Expectations", font=("Helvetica", 12, "bold"))],
    [sg.HorizontalSeparator()],
    [sg.Text("Salary", size=(15, 1)), sg.Input(key="Salary", default_text=info_from_user_info("salary"))],
    [sg.Text("Notice Period", size=(15, 1)), sg.Input(key="Notice Period", default_text=info_from_user_info("notice period"))],
    [sg.Submit()]
]

layout3 = [
    [sg.Text("Right now you only need to input the chat gpt info", font=("Helvetica", 12, "bold"))],
    [sg.Text("LinkedIn", font=("Helvetica", 12, "bold"))],
    [sg.HorizontalSeparator()],
    [sg.Text("Username", size=(15, 1)), sg.Input(key="LinkedIn Username", default_text=info_from_user_info("linkedin email"))],
    [sg.Text("Password", size=(15, 1)), sg.Input(key="LinkedIn Password", default_text=info_from_user_info("linkedin password"))],
    [sg.Text("Indeed", font=("Helvetica", 12, "bold"))],
    [sg.HorizontalSeparator()],
    [sg.Text("Username", size=(15, 1)), sg.Input(key="Indeed Username", default_text=info_from_user_info("indeed email"))],
    [sg.Text("Password", size=(15, 1)), sg.Input(key="Indeed Password", default_text=info_from_user_info("indeed password"))],
    [sg.Text("Workday", font=("Helvetica", 12, "bold"))],
    [sg.HorizontalSeparator()],
    [sg.Text("Username", size=(15, 1)), sg.Input(key="Workday Username", default_text=info_from_user_info("workday email"))],
    [sg.Text("Password", size=(15, 1)), sg.Input(key="Workday Password", default_text=info_from_user_info("workday password"))],
    [sg.Text("ICIMS", font=("Helvetica", 12, "bold"))],
    [sg.HorizontalSeparator()],
    [sg.Text("Username", size=(15, 1)), sg.Input(key="ICIMS Username", default_text=info_from_user_info("icims email"))],
    [sg.Text("Password", size=(15, 1)), sg.Input(key="ICIMS Password", default_text=info_from_user_info("icims password"))],
    [sg.Text("Gmail account for Chat GPT", font=("Helvetica", 12, "bold"))],
    [sg.Text("Required if you want chat gpt to answer questions or write cover letters", font=("Helvetica", 12, "bold"))],
    [sg.HorizontalSeparator()],
    [sg.Text("Username", size=(15, 1)), sg.Input(key="Chatgpt Username", default_text=info_from_user_info("chatgpt email"))],
    [sg.Text("Password", size=(15, 1)), sg.Input(key="Chatgpt Password", default_text=info_from_user_info("chatgpt password"))],

    [sg.Submit(),sg.Button("Skip", key="skip")]
]


def table_update(v, user_info):
    return list(zip(*[user_info[v]][::-1]))


eleml = sg.Table(table_update("Job Title must Contain", user_info), ["Job Title must Contain"],
                 justification="center", enable_click_events=True, key="eleml")
elemm = sg.Table(table_update("Job Title Keywords to Ignore", user_info), ["Job Title Keywords to Ignore"],
                 justification="center", enable_click_events=True, key="elemm")
elemr = sg.Table(table_update("Companies to Ignore", user_info), ["Companies to Ignore"],
                 justification="center", enable_click_events=True, key="elemr")
hold = elemr.get()
layoutl = [[eleml],
           [sg.Text("Job Title must contains one of these words")],
           [sg.Text("Cannot be empty", key="emptyColm1", text_color="red", visible=False)],
           [sg.Button("Add", key="addl"), sg.Button("Remove", key="removel")]]
layoutm = [[elemm],
           [sg.Text("Job Title must not contains one of these words")],
           [sg.Button("Add", key="addm"), sg.Button("Remove", key="removem")]]
layoutr = [[elemr],
           [sg.Text("must be exact match")],
           [sg.Button("Add", key="addr"), sg.Button("Remove", key="remover")]]
layout4 = [
    [sg.Text("skip for now")],

    [sg.Col(layoutl), sg.Col(layoutm), sg.Col(layoutr)],
    [sg.Submit(),sg.Button("Skip", key="skip")]
]

layout5 = [
    [sg.Text("Resume Path"), sg.Text(info_from_user_info("resume"), key="path1"), sg.Button("Edit", key=1)],
    [sg.Text("Only required if you do not plan on using the resume finetuning")],
    [sg.Text("Transcript Path"), sg.Text(info_from_user_info("transcript"), key="path2"), sg.Button("Edit", key=2)],
    [sg.Submit(),sg.Button("Skip", key="skip")]
]


def input_error(errormessage, test) -> bool:
    if test:
        errormessage.update(visible=True)
        return True
    elif errormessage.visible:
        errormessage.update(visible=False)
        return False
    else:
        return False


next = False
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        exit()

    error = False
    error = input_error(window["ziperror"], len(values["Zip code"]) != 5 or not values["Zip code"].isdigit()) or error
    error = input_error(window["phoneerror"], len(values["Phone Number"]) != 10 or not values["Phone Number"].isdigit()) or error
    error = input_error(window["emailerror"], "@" not in values["Email"]) or error
    error = input_error(window["firsterror"], len(values["First Name"]) == 0) or error
    error = input_error(window["lasterror"], len(values["Last Name"]) == 0) or error
    # error = input_error( window["languageerror"], len(values["Language"]) == 0) or error
    error = input_error(window["countryerror"], len(values["Country"]) == 0) or error
    error = input_error(window["cityerror"], len(values["City"]) == 0) or error
    error = input_error(window["addresserror"], len(values["Address"]) == 0) or error
    if not error and event == "Submit":
        next = True
        user_info["first name"] = values["First Name"]
        user_info["last name"] = values["Last Name"]
        user_info["middle name"] = values["Middle Name"]
        user_info["linkedin"] = values["LinkedIn"]
        user_info["website"] = values["Website"]
        # user_info["language"] = values["Language"]
        user_info["language"] = "English"
        user_info["time zone"] = values["Time Zone"]
        user_info["email"] = values["Email"]
        user_info["phone"] = values["Phone Number"]
        user_info["country"] = values["Country"]
        user_info["county"] = values["County"]
        user_info["state"] = values["State"]
        user_info["city"] = values["City"]
        user_info["address"] = values["Address"]
        user_info["zip"] = values["Zip code"]
        break

window.close()
if next:
    next = False
    window = sg.Window("Education and Experience", layout2)
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            exit()
        if event == "Submit":
            next = True
            user_info["salary"] = values["Salary"]
            user_info["notice period"] = values["Notice Period"]
            user_info["do you have any contractual obligations"] = "no"
            user_info["do you hold an active or current security clearance"] = "yes"
            break

window.close()
if next:
    next = False
    window = sg.Window("Login", layout3)
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            exit()
        if event == 'skip':
            next = True
            break
        if event == "Submit":
            next = True

            user_info["linkedin email"] = values["LinkedIn Username"]
            user_info["linkedin password"] = values["LinkedIn Password"]
            user_info["indeed email"] = values["Indeed Username"]
            user_info["indeed password"] = values["Indeed Password"]
            user_info["icims email"] = values["ICIMS Username"]
            user_info["icims password"] = values["ICIMS Password"]
            user_info["workday email"] = values["Workday Username"]
            user_info["workday password"] = values["Workday Password"]
            user_info["chatgpt email"] = values["Chatgpt Username"]
            user_info["chatgpt password"] = values["Chatgpt Password"]
            break

window.close()
window = sg.Window("Keywords", layout4)
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        exit()
    if event == 'skip':
        next = True
        break
    if event == "Submit":
        if not input_error(window["emptyColm1"], len(user_info["Job Title must Contain"]) == 0):
            next = True
            break

    if event == "addl":
        new_item = sg.popup_get_text("Add Keyword")
        user_info["Job Title must Contain"].append(new_item)
        eleml.update(table_update("Job Title must Contain", user_info))
    elif event == "addm":
        new_item = sg.popup_get_text("Add Keyword to Ignore")
        user_info["Job Title Keywords to Ignore"].append(new_item)
        elemm.update(table_update("Job Title Keywords to Ignore", user_info))
    elif event == "addr":
        new_item = sg.popup_get_text("Add Company to Ignore")
        user_info["Companies to Ignore"].append(new_item)
        elemr.update(table_update("Companies to Ignore", user_info))
    elif event == "removel" and len(values["eleml"]) > 0:
        user_info["Job Title must Contain"].pop(values["eleml"][0])
        eleml.update(table_update("Job Title must Contain", user_info))
    elif event == "removem" and len(values["elemm"]) > 0:
        user_info["Job Title Keywords to Ignore"].pop(values["elemm"][0])
        elemm.update(table_update("Job Title Keywords to Ignore", user_info))
    elif event == "remover" and len(values["elemr"]) > 0:
        user_info["Companies to Ignore"].pop(values["elemr"][0])
        elemr.update(table_update("Companies to Ignore", user_info))

window.close()
window = sg.Window("Documents", layout5)

while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED:
        exit()
    if event == 'skip':
        next = True
        window.close()
        break
    if event == "Submit":
        next = True
        user_info["resume"] = window.find_element("path1").get()
        user_info["transcript"] = window.find_element("path2").get()
        window.close()
        break
    if event == 1:
        path = sg.popup_get_file("Resume")
        window.find_element("path1").update(path)
    if event == 2:
        path = sg.popup_get_file("Transcript")
        window.find_element("path2").update(path)

if next:
    with open("personal_info.json", "w") as file:
        json.dump(user_info, file, indent=2)

writefile.generate()
gui2.fill_chatgptinfo()
