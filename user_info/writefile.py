import json

state = {'Alabama': 'al',
         'Alaska': 'ak',
         'Arizona': 'az',
         'Arkansas': 'ar',
         'California': 'ca',
         'Colorado': 'co',
         'Connecticut': 'ct',
         'Delaware': 'de',
         'Florida': 'fl',
         "Georgia": 'ga',
         'Hawaii': 'hi',
         'Idaho': 'id',
         'Illinois': 'il',
         'Indiana': 'in',
         'Iowa': 'ia',
         'Kansas': 'ks',
         'Kentucky': 'ky',
         'Louisiana': 'la',
         'Maine': 'me',
         'Maryland': 'md',
         'Massachusetts': 'ma',
         'Michigan': 'mi',
         'Minnesota': 'mn',
         'Mississippi': 'ms',
         'Missouri': 'mo',
         'Montana': 'mt',
         'Nebraska': 'ne',
         'Nevada': 'nv',
         'New Hampshire': 'nh',
         'New Jersey': 'nj',
         'New Mexico': 'nm',
         'New York': 'ny',
         'North Carolina': 'nc',
         'North Dakota': 'nd',
         'Ohio': 'oh',
         'Oklahoma': 'ok',
         'Oregon': 'or',
         'Pennsylvania': 'pa',
         'Rhode Island': 'ri',
         'South Carolina': 'sc',
         'South Dakota': 'sd',
         'Tennessee': 'tn',
         'Texas': 'tx',
         'Utah': 'ut',
         'Vermont': 'vt',
         'Virginia': 'va',
         'Washington': 'wa',
         'West Virginia': 'wv',
         'Wisconsin': 'wi',
         'Wyoming': 'wy'
         }

def generate():
    with open("personal_info.json", 'r') as file:
        user_info = json.load(file)
    with open("alt_names.json", 'r') as file:
        tags = json.load(file)
    masterdic = {}

    if len(user_info['middle name']) == 0:
        user_info["name"] = user_info['first name'] + ' ' + user_info['last name']
    else:
        user_info["name"] = user_info['first name'] + ' ' + user_info['middle name'] + ' ' + user_info['last name']
    user_info["please provide more information"] = "see resume"
    user_info["do you currently have any family members"] = 'no'
    user_info["have you been previously employed"] = 'no|never'
    user_info["are you currently working"] = 'no'
    if 'degree' in user_info:
        user_info["degree"] = user_info["degree"] + '|' + user_info["degree"] + '\'s degree|' + user_info["degree"] + '\'s of science'
    if 'state' in user_info and len(user_info['state']) > 0:
        user_info["state"] = user_info["state"] + '|' + state[user_info["state"]]

    if user_info['country'] == "United States of America":
        user_info['country'] = 'united states of america' + '|united states'
        user_info["phone country code"] = "united states (+1)"
        user_info["extension"] = "1"
        #assume this for now
        user_info["u.s. citizen or legal permanent resident"] = 'yes'

    if user_info["u.s. citizen or legal permanent resident"] == 'yes':
        user_info["require sponsorship"] = 'no'
        user_info['require employer visa sponsorship'] = 'no'
        user_info["authorized to work"] = 'yes'
        user_info["u.s. citizen"] = 'yes'
        user_info["what's your citizenship"] = "citizen"
        user_info["which countries are you currently legally authorized to work in"] = "US"
    else:
        user_info["require sponsorship"] = 'yes'
        user_info['require employer visa sponsorship'] = 'yes'
        user_info["authorized to work"] = 'no'
        user_info["u.s. citizen"] = 'no'




    for text in user_info:
        if text in tags:
            for j in tags[text]:
                masterdic[j] = user_info[text]
        else:
            masterdic[text] = user_info[text]


    #if user_info["u.s. citizen or legal permanent resident"] == 'yes':
    #    masterdic["what's your citizenship"] = "citizen"
    #    masterdic["which countries are you currently legally authorized to work in"] = "US"

    if user_info["do you currently have any family members"] == 'no':
        masterdic["name of relative"] = ""
    for i in user_info["language"].split('|'):
        masterdic['proficiency in ' + i.lower()] = "native"

    #for i in user_info["country"].lower().split('|'):
    #    if i in ["united states", "us"]:
    #        masterdic["phone country code"] = "united states (+1)"
    #        masterdic["extension"] = "1"
    #        break

    with open("default_responses.json", 'r') as file:
        default = json.load(file)

    masterdic = masterdic | default
    with open("responses.json", 'w') as file:
        json.dump(masterdic, file, indent=2)
if __name__ == '__main__':
    generate()
