from selenium import webdriver
import Applicationsite2 as App2
import jobhostUtil
import PySimpleGUI as sg

# turn into

# problems with smart recuiters notiched ip address maybe custom marking

def gui():
    layout1 = [
        [sg.Text('auto app system')],
        [sg.Text('Use ChatGPT')],
        [sg.Radio('Yes', 'ChatGPT', default=True, size=(15, 1), key='yes1'),
         sg.Radio('No', 'ChatGPT', size=(15, 1))],
        [sg.Text('Resume Finetune')],
        [sg.Radio('Yes', 'Finetune', default=True, size=(15, 1), key='yes2'),
         sg.Radio('No', 'Finetune', size=(15, 1))],
        [sg.Text('Link to app', size=(15, 1)), sg.Input(
            default_text='',
            key='link')],
        [sg.Submit(), sg.Cancel()]
    ]
    sg.theme('Gray Gray Gray')
    window = sg.Window("Main", layout1)

    while True:
        event, values = window.read()
        if event == "Submit":
            window.close()
            start(values['link'], values['yes1'], values['yes2'])
            break
        if event == sg.WIN_CLOSED:
            window.close()
            break
def start(url, ChatGPT, finetune):

    driver, user_info, applied_list = jobhostUtil.load(url)
    # automate job info retrival
    # greenhouse
    # lever

    site = jobhostUtil.determine_website(driver, user_info, ChatGPT, finetune, None)
    if site.question_cycle():
        print('pass')

if __name__ == "__main__":
    url = ''
    gui()
    #start(url,True,True)
