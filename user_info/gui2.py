import PySimpleGUI as sg
import json
import writefile
from datetime import datetime, date

GPA = ["", "2.0", "2.1", "2.2", "2.3", "2.4", "2.5", "2.6", "2.7", "2.8", "2.9", "3.0", "3.1",
       "3.2",
       "3.3", "3.4", "3.5", "3.6", "3.7", "3.8", "3.9", "4.0"]
DEGREE = ["", "High School", "Bachelor", "Master", "PHD"]


def update(prompts, key: str):
    test2 = []
    for x in prompts[key]:
        items = list(x.values())
        if isinstance(items[-1], list):
            items[-1] = "\n".join(items[-1])
        test2.append(items)
    return test2


def date_check(index):
    if "/" in index:
        parts = index.split("/")
        if len(parts) == 2 and parts[0] in (
                ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]) and len(
            parts[1]) == 4 and \
                parts[1] != type(
            int()) or parts[1] < 1:
            return True
    return False


# put into util
def input_error(errormessage, test, error_text=None) -> bool:
    if test:
        if error_text is not None:
            errormessage.update(visible=True, value=error_text)
        else:
            errormessage.update(visible=True)
        return True
    elif errormessage.visible:
        errormessage.update(visible=False)
        return False
    else:
        return False


def date_check2(window, values) -> bool:
    if date_check(values["start"]):
        window["start_error"].update(visible=False)
    elif not window["start_error"].visible:
        window["start_error"].update(value="must be in mm/yyyy", visible=True)
        return True

    if date_check(values["end"]):
        window["end_error"].update(visible=False)
    else:
        window["end_error"].update(value="must be in mm/yyyy", visible=True)
        return True
    one = values["start"].split("/")
    two = values["end"].split("/")

    if (int(one[1]) == int(two[1]) and int(one[0]) <= int(two[0])) or int(one[1]) < int(two[1]):
        window["end_error"].update(visible=False)
        window["start_error"].update(visible=False)
        return False
    else:
        window["end_error"].update(value="end cannot be before start", visible=True)
        return True


def pop_up(colm_names: list[str], name: str, dic=None):
    def load(dic, value):
        if dic is None or value not in dic:
            return ""
        elif value == "duties":
            return "\n".join(dic[value])
        else:
            return dic[value]

    layout = []
    for x in range(len(colm_names)):
        if colm_names[x] == "Duties":
            layout.append(
                [sg.Text("Duties", size=(15, 1)),
                 sg.Multiline(key=colm_names[x].lower(), size=(50, 20),
                              default_text=load(dic, colm_names[x].lower())),
                 sg.Text("have each duty end with a period and new line", key=x, text_color="red",
                         visible=False)])
            continue
        elif colm_names[x] == "Degree":
            layout.append([sg.Text("Degree", size=(15, 1)),
                           sg.Drop(values=DEGREE, default_value=load(dic, colm_names[x].lower()),
                                   auto_size_text=True, key=colm_names[x].lower()),
                           sg.Text("required", key=x, text_color="red", visible=False)])
            continue
        elif colm_names[x] == "GPA":
            layout.append(
                [sg.Text("GPA", size=(15, 1)),
                 sg.Spin(values=GPA, initial_value=load(dic, colm_names[x].lower()), size=(6, 1),
                         key=colm_names[x].lower()),
                 sg.Text("required", key=x, text_color="red", visible=False)])
            continue
        if colm_names[x] in ["Start", "End"]:
            error = sg.Text("must be in mm/yyyy", key=colm_names[x].lower() + "_error",
                            text_color="red", visible=False)
        else:
            error = sg.Text("required", key=x, text_color="red", visible=False)
        layout.append([sg.Text(colm_names[x], size=(15, 1)), sg.Input(key=colm_names[x].lower(),
                                                                      default_text=load(dic,
                                                                                        colm_names[
                                                                                            x].lower())),
                       error])
    layout.append([sg.Submit()])

    window = sg.Window(name, layout)

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            window.close()
            return -1

        if event == "Submit":
            error = False
            index = 0
            for x in values.keys():
                if x in ["start", "end"]:
                    error = date_check2(window, values) or error
                elif x == "duties":

                    def duties_check(errormessage, x) -> bool:
                        for i in x.split("\n"):
                            if len(i) == 0 or i[-1] != "." or i.find(".", 0, len(i) - 1) != -1:
                                return input_error(errormessage, True,
                                                   "have each duty end with a period")
                        return False

                    error = duties_check(window[index], values[x]) or error
                else:
                    error = input_error(window[index], len(values[x]) == 0, "required") or error
                index += 1
            if not error and event == "Submit":
                if "duties" in values:
                    values["duties"] = [x.strip()+"." for x in values["duties"].split(".")]
                    del values["duties"][-1]
                window.close()
                return values


def fill_chatgptinfo():
    with open("personal_info.json", "r") as file:
        user_info = json.load(file)
    with open("query.json", "r") as file:
        query = json.load(file)

    try:
        with open("start up.json", "r") as file:
            prompts = json.load(file)
    except FileNotFoundError:
        prompts = {"work experience": [], "project experience": [], "education": []}
    NAME = user_info["first name"] + " " + user_info["last name"]

    # query["task"] = "Write a humanized cover letter as " + NAME + " using the resume to match the skills from the last prompt."
    sg.theme("Gray Gray Gray")

    def table_window(name: str, dic_name: str, colm_names: list[str], message: str):
        layout1 = [
            [sg.Text(name)],
            [sg.Text(message)],
            [sg.Table(update(prompts, dic_name), colm_names,
                      justification="center", enable_click_events=True, key="table", row_height=50,
                      max_col_width=100)],
            [sg.Button("Add", key="add"), sg.Button("Edit", key="edit"),
             sg.Button("Remove", key="remove")],
            [sg.Submit(),sg.Button("Skip", key="skip")]
        ]

        window = sg.Window(name, layout1)
        while True:
            event, values = window.read()
            if event == sg.WIN_CLOSED:
                exit()
            if event == "Submit":
                window.close()
                break
            if event == "skip":
                window.close()
                break
            if event == "add":
                new_info = pop_up(colm_names, name)
                if new_info != -1:
                    prompts[dic_name].append(new_info)
                    prompts[dic_name] = sorted(prompts[dic_name],
                                               key=lambda x: datetime.strptime(x["end"], "%m/%Y"),
                                               reverse=True)
                    window["table"].update(update(prompts, dic_name))
            elif event == "remove" and len(values["table"]) > 0:
                del prompts[dic_name][values["table"][0]]
                window["table"].update(update(prompts, dic_name))
            elif event == "edit" and len(values["table"]) > 0:
                new_info = pop_up(colm_names, name, prompts[dic_name][values["table"][0]])
                if new_info != -1:
                    prompts[dic_name][values["table"][0]] = new_info
                    prompts[dic_name] = sorted(prompts[dic_name],
                                               key=lambda x: datetime.strptime(x["end"], "%m/%Y"),
                                               reverse=True)
                    window["table"].update(update(prompts, dic_name))

    table_window("Work Experience", "work experience",
                 ["Job Title", "Company", "Start", "End", "Duties"], "Required for Resume Finetune and chat gpt")
    table_window("Project Experience", "project experience",
                 ["Job Title", "Start", "End", "Duties"], "Optional")
    table_window("Education", "education", ["School", "Degree", "Major", "GPA", "Start", "End"],
                 "Required for Resume Finetune and chat gpt")

    user_info["school"] = prompts["education"][0]["school"]
    user_info["degree"] = prompts["education"][0]["degree"]
    user_info["major"] = prompts["education"][0]["major"]
    user_info["gpa"] = prompts["education"][0]["gpa"]

    user_info["last job title"] = prompts["work experience"][0]["job title"]
    user_info["last job company"] = prompts["work experience"][0]["company"]

    summ = 0
    for jobs in prompts["work experience"]:
        start = jobs["start"].split("/")
        end = jobs["end"].split("/")
        summ += int(end[0]) - int(start[0]) + (int(end[1]) - int(start[1])) * 12
    user_info["years of experience"] = str(round(summ / 12))
    prompts["task"] = "Act as " + NAME + " with " + str(
        user_info["years of experience"]) + " years of work experience. Respond with ok."
    with open("personal_info.json", "w") as file:
        json.dump(user_info, file, indent=2)
    with open("start up.json", "w") as file:
        json.dump(prompts, file, indent=2)
    with open("query.json", "w") as file:
        json.dump(query, file, indent=2)


if __name__ == "__main__":
    fill_chatgptinfo()
